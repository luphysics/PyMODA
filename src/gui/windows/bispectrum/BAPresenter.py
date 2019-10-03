#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2019 Lancaster University
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
from typing import Tuple

from PyQt5.QtWidgets import QListWidgetItem
from numpy import ndarray

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.common.BaseTFPresenter import BaseTFPresenter
from maths.params.BAParams import BAParams
from maths.signals.BAOutputData import BAOutputData
from maths.signals.SignalPairs import SignalPairs
from maths.signals.TimeSeries import TimeSeries
from processes.MPHandler import MPHandler


class BAPresenter(BaseTFPresenter):

    def __init__(self, view):
        super().__init__(view)

        from gui.windows.bispectrum.BAWindow import BAWindow
        self.view: BAWindow = view

    def init(self):
        super().init()
        self.view.switch_to_dual_plot()

    def calculate(self, calculate_all: bool):
        asyncio.ensure_future(self.coro_calculate())

    async def coro_calculate(self):
        if self.mp_handler:
            self.mp_handler.stop()

        self.is_plotted = False
        self.invalidate_data()

        self.mp_handler = MPHandler()
        data = await self.mp_handler.coro_bispectrum_analysis(self.signals,
                                                              self.get_params(),
                                                              self.on_progress_updated)

        for d in data:
            self.on_bispectrum_completed(*d)

        self.update_plots()

    def update_plots(self):
        data = self.get_selected_signal_pair()[0].output_data

        self.update_main_plot(data)
        self.update_side_plots(data)

    def update_main_plot(self, data):
        x, y, c, log = self.get_main_plot_data(self.view.get_plot_type(), data)

        if self.view.is_wt_selected():
            self.view.switch_to_dual_plot()
        else:
            self.view.switch_to_triple_plot()

        if c is not None:
            self.view.plot_main.set_log_scale(log, axis="x")
            self.view.plot_main.set_log_scale(True, axis="y")
            self.view.plot_main.plot(x=x, y=y, c=c)
            self.view.plot_main.update_xlabel("Frequency (Hz)")
            self.view.plot_main.update_ylabel("Frequency (Hz)")

    def update_side_plots(self, data):
        if self.view.is_wt_selected():
            pass # TODO


    @staticmethod
    def get_main_plot_data(plot_type: str, data: BAOutputData):
        if not isinstance(data, BAOutputData):
            return [None for _ in range(4)]

        _dict = {
            "Wavelet transform 1": (data.times, data.freq, data.amp_wt1, False),
            "Wavelet transform 2": (data.times, data.freq, data.amp_wt2, False),
            "b111": (data.freq, data.freq, data.bispxxx, True),
            "b222": (data.freq, data.freq, data.bispppp, True),
            "b122": (data.freq, data.freq, data.bispxpp, True),
            "b211": (data.freq, data.freq, data.bisppxx, True),
        }
        data = _dict.get(plot_type)
        if data is None:  # All plots.
            pass  # TODO

        return data

    def on_bispectrum_completed(self,
                                name: str,
                                freq: ndarray,
                                amp_wt1: ndarray,
                                pow_wt1: ndarray,
                                avg_amp_wt1: ndarray,
                                avg_pow_wt1: ndarray,
                                amp_wt2: ndarray,
                                pow_wt2: ndarray,
                                avg_amp_wt2: ndarray,
                                avg_pow_wt2: ndarray,
                                bispxxx: ndarray,
                                bispppp: ndarray,
                                bispxpp: ndarray,
                                bisppxx: ndarray,
                                surrxxx: ndarray,
                                surrppp: ndarray,
                                surrxpp: ndarray,
                                surrpxx: ndarray):

        # Attach the data to the first signal in the current pair.
        sig = self.signals.get(name)

        sig.output_data = BAOutputData(
            amp_wt1,
            pow_wt1,

            avg_amp_wt1,
            avg_pow_wt1,

            amp_wt2,
            pow_wt2,

            avg_amp_wt2,
            avg_pow_wt2,

            sig.times,
            freq,

            bispxxx,
            bispppp,
            bispxpp,
            bisppxx,

            surrxxx,
            surrppp,
            surrxpp,
            surrpxx
        )

    async def coro_load_data(self):
        self.signals = SignalPairs.from_file(self.open_file)

        if not self.signals.has_frequency():
            freq = await FrequencyDialog().coro_get()

            if freq:
                self.set_frequency(freq)
                self.on_data_loaded()
            else:
                raise Exception("Frequency was None. Perhaps it was mistyped?")

    def on_data_loaded(self):
        self.view.update_signal_listview(self.signals.get_pair_names())
        self.plot_signal_pair()

    def plot_signal_pair(self):
        self.view.plot_signal_pair(self.get_selected_signal_pair())

    def on_signal_selected(self, item):
        if isinstance(item, QListWidgetItem):
            name = item.text()
        else:
            name = item

        self.signals.reset()
        if name != self.selected_signal_name:
            print(f"Selected '{name}'")
            self.selected_signal_name = name
            self.plot_signal_pair()
            self.view.on_xlim_edited()

    def get_selected_signal_pair(self) -> Tuple[TimeSeries, TimeSeries]:
        return self.signals.get_pair_by_name(self.selected_signal_name)

    def get_params(self) -> BAParams:
        return BAParams(signals=self.signals,
                        preprocess=self.view.get_preprocess(),
                        fmin=self.view.get_fmin(),
                        fmax=self.view.get_fmax(),
                        f0=self.view.get_f0(),
                        nv=self.view.get_nv(),
                        surr_count=self.view.get_surr_count())
