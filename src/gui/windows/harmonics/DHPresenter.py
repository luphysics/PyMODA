#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2020 Lancaster University
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
import asyncio
from typing import List, Dict

import numpy as np
from PyQt5.QtWidgets import QListWidgetItem
from numpy import ndarray

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.common.BaseTFPresenter import BaseTFPresenter
from maths.params.DHParams import DHParams
from maths.params.TFParams import create
from maths.signals.Signals import Signals
from processes.MPHandler import MPHandler
from utils.decorators import override
from utils.dict_utils import sanitise


class DHPresenter(BaseTFPresenter):
    def __init__(self, view):
        super(DHPresenter, self).__init__(view)

        from gui.windows.harmonics import DHWindow

        self.view: DHWindow = view
        self.is_calculating_all = True

    def calculate(self, calculate_all: bool) -> None:
        """
        Calculates the harmonics, and plots the results.

        :param calculate_all: whether to calculate for all signals, or just the current signal
        """
        asyncio.ensure_future(self.coro_calculate(calculate_all))
        print("Started calculation...")

    async def coro_calculate(self, calculate_all: bool) -> None:
        """
        Coroutine to perform the calculation.

        :param calculate_all: whether to calculate for all signals, or just the current signal
        """
        self.is_calculating_all = calculate_all
        self.view.enable_save_data(False)
        for s in self.signals:
            s.data = None

        if self.mp_handler:
            self.mp_handler.stop()

        self.mp_handler = MPHandler()

        params = self.get_params(all_signals=calculate_all)
        self.params = params
        self.params.preprocess = self.view.get_preprocess()

        self.is_plotted = False
        self.view.main_plot().clear()
        self.invalidate_data()

        self.view.main_plot().set_log_scale(logarithmic=True)

        self.view.on_calculate_started()

        all_data = await self.mp_handler.coro_harmonics(
            self.signals_calc, params, self.params.preprocess, self.on_progress_updated
        )

        if not isinstance(all_data, List):
            all_data = [all_data]

        for signal, data in zip(self.signals_calc, all_data):
            signal.data = data

        self.view.enable_save_data(bool(all_data))
        self.view.on_calculate_stopped()
        self.update_plots()

    def update_plots(self) -> None:
        sig = self.get_selected_signal()
        main_plot = self.view.main_plot()

        lbl = "Frequency (Hz)"
        main_plot.get_xlabel = lambda: lbl
        main_plot.get_ylabel = lambda: lbl

        if hasattr(sig, "data") and sig.data:
            scalefreq, res, pos1, pos2 = sig.data

            main_plot.set_log_scale(logarithmic=True, axis="x")
            main_plot.set_log_scale(logarithmic=True, axis="y")

            index = self.view.get_plot_index()
            main_plot.pcolormesh(
                scalefreq, sig.data[index + 1], scalefreq, custom_cmap=False
            )
        else:
            main_plot.clear()

    def load_data(self) -> None:
        self.signals = Signals.from_file(self.open_file)

        if not self.signals.has_frequency():
            freq = FrequencyDialog().run_and_get()

            if freq:
                self.signals.set_frequency(freq)
                self.on_data_loaded()

    def on_data_loaded(self) -> None:
        self.view.update_signal_listview(self.signals.names())
        self.plot_signal()

    @override
    async def coro_get_data_to_save(self) -> Dict:
        if not self.params:
            return None

        preproc = await self.coro_preprocess_all_signals()
        preproc_arr = np.asarray(preproc)
        preprocess = self.params.preprocess

        for s in self.signals:
            if not hasattr(s, "data"):
                s.data = None

        output_data = [s.data for s in self.signals]
        cols = len(output_data)

        freq = [d[0] if d else None for d in output_data]
        res = [d[1] if d else None for d in output_data]
        pos1 = [d[2] if d else None for d in output_data]
        pos2 = [d[3] if d else None for d in output_data]

        first = 0
        while output_data[first] is None:
            first += 1

        freq_arr = np.empty((cols, *freq[first].shape))
        res_arr = np.empty((cols, *res[first].shape))
        pos1_arr = np.empty((cols, *pos1[first].shape))
        pos2_arr = np.empty((cols, *pos2[first].shape))

        for i in range(cols):
            if freq[i] is not None:
                freq_arr[i, :] = freq[i]
                res_arr[i, :, :] = res[i]
                pos1_arr[i, :, :] = pos1[i]
                pos2_arr[i, :, :] = pos2[i]
            else:
                freq_arr[i, :] = np.NaN
                res_arr[i, :, :] = np.NaN
                pos1_arr[i, :, :] = np.NaN
                pos2_arr[i, :, :] = np.NaN

        dh_data = {
            "res": res_arr,
            "freq": freq_arr,
            "pos1": pos1_arr,
            "pos2": pos2_arr,
            "preprocessed_signals": preproc_arr if preprocess else None,
            **self.params.items_to_save(),
        }

        return {"DHData": sanitise(dh_data)}

    def plot_signal(self) -> None:
        self.view.plot_signal(self.get_selected_signal())

    def on_signal_selected(self, item: [QListWidgetItem, str]) -> None:
        """
        Called when a signal is selected in the QListWidget.
        Plots the new signal in the top-left plotting and, if
        transform data is available, plots the transform and
        amplitude/power in the main plots.
        """
        if isinstance(item, QListWidgetItem):
            name = item.text()
        else:
            name = item

        self.signals.reset()
        if name != self.selected_signal_name:
            print(f"Selected signal: '{name}'")
            self.selected_signal_name = name

            self.plot_signal()
            self.update_plots()

            self.view.on_xlim_edited()
            self.plot_preprocessed_signal()

    async def coro_preprocess_selected_signal(self) -> List[ndarray]:
        sig = self.get_selected_signal()

        if not self.preproc_mp_handler:
            self.preproc_mp_handler = MPHandler()

        return await self.preproc_mp_handler.coro_preprocess(sig, None, None)

    def get_params(self, all_signals: bool = True) -> DHParams:
        if all_signals:
            self.signals_calc = self.signals
        else:
            self.signals_calc = self.signals.only(self.selected_signal_name)

        fmin = self.view.get_fmin()
        fmax = self.view.get_fmax()

        scale_min = 1 / fmax
        scale_max = 1 / fmin

        return create(
            signals=self.signals_calc,
            params_type=DHParams,
            scale_min=scale_min,
            scale_max=scale_max,
            sigma=self.view.get_sigma(),
            time_res=self.view.get_time_res(),
            surr_count=self.view.get_surr_count(),
            crop=self.view.get_cut_edges(),
        )
