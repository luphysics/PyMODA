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
from typing import List

from PyQt5.QtWidgets import QListWidgetItem

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.common.BaseTFPresenter import BaseTFPresenter
from maths.params.DHParams import DHParams
from maths.params.TFParams import create
from maths.signals.Signals import Signals
from processes.MPHandler import MPHandler


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

        if self.mp_handler:
            self.mp_handler.stop()

        self.mp_handler = MPHandler()

        params = self.get_params(all_signals=calculate_all)
        self.params = params

        self.is_plotted = False
        self.view.main_plot().clear()
        self.invalidate_data()

        self.view.main_plot().set_log_scale(logarithmic=True)

        self.view.on_calculate_started()

        all_data = await self.mp_handler.coro_harmonics(
            self.signals_calc, params, self.on_progress_updated
        )

        if not isinstance(all_data, List):
            all_data = [all_data]

        for signal, data in zip(self.signals_calc, all_data):
            signal.data = data

        self.view.on_calculate_stopped()
        self.update_plots()

    def update_plots(self) -> None:
        sig = self.get_selected_signal()
        main_plot = self.view.main_plot()

        if hasattr(sig, "data"):
            scalefreq, res, pos1, pos2 = sig.data

            main_plot.set_log_scale(logarithmic=True, axis="x")
            main_plot.set_log_scale(logarithmic=True, axis="y")

            index = self.view.get_plot_index()
            main_plot.pcolormesh(
                scalefreq, sig.data[index + 1], scalefreq, custom_cmap=False
            )

            lbl = "Frequency (Hz)"
            main_plot.update_xlabel(lbl)
            main_plot.update_ylabel(lbl)

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
            self.view.on_xlim_edited()

    def get_params(self, all_signals: bool = True) -> DHParams:
        if all_signals:
            self.signals_calc = self.signals
        else:
            self.signals_calc = self.signals.only(self.selected_signal_name)

        return create(
            signals=self.signals_calc,
            params_type=DHParams,
            scale_min=self.view.get_scale_min(),
            scale_max=self.view.get_scale_max(),
            sigma=self.view.get_sigma(),
            time_res=self.view.get_time_res(),
            surr_count=self.view.get_surr_count(),
        )
