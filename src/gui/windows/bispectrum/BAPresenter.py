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
from typing import Tuple, Union

from PyQt5.QtWidgets import QListWidgetItem
from numpy import ndarray

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.common.BaseTFPresenter import BaseTFPresenter
from maths.params.BAParams import BAParams
from maths.signals.data.BAOutputData import BAOutputData
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
        """Starts the coroutine which calculates the data."""
        asyncio.ensure_future(self.coro_calculate())

    async def coro_calculate(self):
        """Coroutine which calculates the bispectra."""
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
        """
        Updates all plots according to the currently selected plot type and current data.
        """
        data = self.get_selected_signal_pair()[0].output_data

        self.update_main_plot(data)
        self.update_side_plots(data)

    def update_main_plot(self, data):
        """
        Updates the main plot, plotting the wavelet transform or bispectrum depending
        on the selected plot type.

        :param data: the data object
        """
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

    def update_side_plots(self, data: BAOutputData):
        """
        Updates the side plot(s). For wavelet transforms this will be
        the average amplitude/power, but for bispectra this will be the
        biphase and biamplitude.

        :param data: the data object
        """
        if self.view.is_wt_selected():  # Plot average amplitude or power.
            amp_not_power = self.view.is_amplitude_selected()
            x, y = self.get_side_plot_data_wt(self.view.get_plot_type(), data, amp_not_power)

            if x is not None and y is not None and len(x) > 0:
                plot = self.view.plot_right_top
                plot.set_xlabel("Average amplitude")
                plot.set_ylabel("Frequency (Hz)")

                plot.set_log_scale(True, "y")
                plot.plot(x, y)
        else:  # Plot biphase and biamplitude.
            pass

    @staticmethod
    def get_side_plot_data_wt(plot_type: str, data: BAOutputData, amp_not_power: bool) -> Tuple[ndarray, ndarray]:
        """
        Gets the data required to plot the average amplitude/power on the side plot. Used
        when a wavelet transform is selected.

        :param plot_type: the plot type shown in the QComboBox, e.g. "Wavelet transform 1"
        :param data: the data object
        :param amp_not_power: whether the data should be amplitude, or power
        :return: the x-values, the y-values
        """
        _dict = {
            "Wavelet transform 1": (data.avg_amp_wt1 if amp_not_power else data.avg_pow_wt1, data.freq),
            "Wavelet transform 2": (data.avg_amp_wt2 if amp_not_power else data.avg_pow_wt2, data.freq),
        }
        return _dict.get(plot_type)

    @staticmethod
    def get_side_plot_data_bispec(plot_type: str, data: BAOutputData):
        """
        Gets the data required to plot the biphase and biamplitude on the side plots.
        Used when bispectrum is selected.

        :param plot_type the plot type shown in the QComboBox, e.g. "b111"
        :param data the data object
        :return: # TODO add this
        """
        pass

    @staticmethod
    def get_main_plot_data(plot_type: str, data: BAOutputData) -> Tuple[ndarray, ndarray, ndarray, bool]:
        """
        Gets the relevant arrays to plot in the main plot (WT or bispectrum).

        :param plot_type: the type of plot, as shown in the QComboBox; e.g. "Wavelet transform 1"
        :param data: the data object with all data
        :return: the x-values, the y-values, the c-values, and whether to use a log scale
        """
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
        """
        Loads the data from a file, showing a dialog to set the frequency of
        the signal.
        """
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

    def on_signal_selected(self, item: Union[QListWidgetItem, str]):
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
        """
        Gets the currently selected signal pair as a tuple containing 2 signals.
        """
        return self.signals.get_pair_by_name(self.selected_signal_name)

    def get_params(self) -> BAParams:
        """Gets data from the GUI to create the params used by the bispectrum calculation."""
        return BAParams(signals=self.signals,
                        preprocess=self.view.get_preprocess(),
                        fmin=self.view.get_fmin(),
                        fmax=self.view.get_fmax(),
                        f0=self.view.get_f0(),
                        nv=self.view.get_nv(),
                        surr_count=self.view.get_surr_count())
