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
from typing import Tuple, Union, Dict, List, Optional

import numpy as np
from PyQt5.QtWidgets import QListWidgetItem
from numpy import ndarray

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.common.BaseTFPresenter import BaseTFPresenter
from maths.params.BAParams import BAParams
from maths.signals.SignalPairs import SignalPairs
from maths.signals.TimeSeries import TimeSeries
from maths.signals.data.BAOutputData import BAOutputData
from processes.MPHandler import MPHandler
from utils.decorators import override
from utils.dict_utils import sanitise


class BAPresenter(BaseTFPresenter):
    def __init__(self, view):
        super().__init__(view)
        self.params: BAParams = None

        from gui.windows.bispectrum.BAWindow import BAWindow

        self.view: BAWindow = view

    def init(self):
        super().init()
        self.view.switch_to_dual_plot()

    def calculate(self, calculate_all: bool):
        """Starts the coroutine which calculates the data."""
        asyncio.ensure_future(self.coro_calculate())
        self.view.on_calculate_started()

    async def coro_calculate(self):
        """Coroutine which calculates the bispectra."""
        self.enable_save_data(False)

        if self.mp_handler:
            self.mp_handler.stop()

        self.is_plotted = False
        self.invalidate_data()

        # We need to use the same params for biphase later; save now because the UI could change.
        self.params = self.get_params()

        self.mp_handler = MPHandler()
        data = await self.mp_handler.coro_bispectrum_analysis(
            self.signals, self.params, self.on_progress_updated
        )

        for d in data:
            self.on_bispectrum_completed(*d)

        self.enable_save_data(True)

        self.view.on_calculate_stopped()
        self.update_plots()

    def add_point(self, x: float, y: float):
        asyncio.ensure_future(self.coro_biphase(x, y))
        self.view.on_calculate_started()

    async def coro_biphase(self, x: float, y: float):
        self.enable_save_data(False)
        self.mp_handler.stop()

        fs = self.params.fs
        f0 = self.params.f0
        fr = self.view.get_selected_freq_pair()
        x, y = fr

        if x is not None and y is not None:
            data = await self.mp_handler.coro_biphase(
                self.signals, fs, f0, fr, self.on_progress_updated
            )

            for d in data:
                self.on_biphase_completed(*d)

            self.enable_save_data(True)

            self.view.on_calculate_stopped()
            self.update_side_plots(self.get_selected_signal_pair()[0].output_data)

    def update_plots(self):
        """
        Updates all plots according to the currently selected plot type and current data.
        """
        data = self.get_selected_signal_pair()[0].output_data

        try:
            if "All plots" not in self.view.get_plot_type():
                self.update_main_plot(data)
                self.update_side_plots(data)
            else:
                self.update_all_plots(data)
        except AttributeError:
            pass
        except ValueError as e:
            msg = "zero-size array to reduction operation minimum which has no identity"
            if msg in str(e):
                print(
                    f"'{self.view.combo_plot_type.currentText()}' is not available to plot."
                )
            else:
                raise e

    def set_plot_type(self, amplitude_selected=True) -> None:
        """
        Set the type of plot to display (power or amplitude). This affects
        the main plot and the amplitude plot.

        :param amplitude_selected: whether to set the plot type as amplitude (not power)
        """
        self.plot_ampl = amplitude_selected
        self.update_plots()

    def update_all_plots(self, data: BAOutputData) -> None:
        self.view.switch_to_all_plots()

    def update_main_plot(self, data: BAOutputData) -> None:
        """
        Updates the main plot, plotting the wavelet transform or bispectrum depending
        on the selected plot type.

        :param data: the data object
        """
        x, y, c, log = self.get_main_plot_data(self.view.get_plot_type(), data)
        freq_x, freq_y = self.view.get_selected_freq_pair()

        if self.view.is_wt_selected():
            self.view.switch_to_dual_plot()
        else:
            self.view.switch_to_triple_plot()

        if freq_x is not None and freq_y is not None:
            self.view.plot_main.draw_crosshair(freq_x, freq_y)

        if c is not None:
            self.view.plot_main.set_log_scale(log, axis="x")
            self.view.plot_main.set_log_scale(True, axis="y")
            self.view.plot_main.update_xlabel("Frequency (Hz)")
            self.view.plot_main.update_ylabel("Frequency (Hz)")
            self.view.plot_main.plot(x=x, y=y, c=c)

    def update_side_plots(self, data: BAOutputData) -> None:
        """
        Updates the side plot(s). For wavelet transforms this will be
        the average amplitude/power, but for bispectra this will be the
        biphase and biamplitude.

        :param data: the data object
        """
        if self.view.is_wt_selected():  # Plot average amplitude or power.
            x, y = self.get_side_plot_data_wt(
                self.view.get_plot_type(), data, self.plot_ampl
            )

            if x is not None and y is not None and len(x) > 0:
                plot = self.view.plot_right_top
                plot.set_xlabel("Average amplitude")
                plot.set_ylabel("Frequency (Hz)")

                plot.set_log_scale(True, "y")
                plot.plot(x, y)
        else:  # Plot biphase and biamplitude.
            biamp, biphase = self.get_side_plot_data_bispec(
                self.view.get_plot_type(), self.view.get_selected_freq_pair(), data
            )

            times = self.get_selected_signal().times

            if biamp is not None:
                self.view.plot_right_middle.update_ylabel("Biamplitude")
                self.view.plot_right_middle.update_xlabel("Time (s)")
                self.view.plot_right_middle.plot(times, biamp)

            if biphase is not None:
                self.view.plot_right_bottom.update_ylabel("Biphase")
                self.view.plot_right_bottom.update_xlabel("Time (s)")
                self.view.plot_right_bottom.plot(times, biphase)

    @staticmethod
    def get_side_plot_data_wt(
        plot_type: str, data: BAOutputData, amp_not_power: bool
    ) -> Tuple[ndarray, ndarray]:
        """
        Gets the data required to plot the average amplitude/power on the side plot. Used
        when a wavelet transform is selected.

        :param plot_type: the plot type shown in the QComboBox, e.g. "Wavelet transform 1"
        :param data: the data object
        :param amp_not_power: whether the data should be amplitude, or power
        :return: the x-values, the y-values
        """
        _dict = {
            "Wavelet transform 1": (
                data.avg_amp_wt1 if amp_not_power else data.avg_pow_wt1,
                data.freq,
            ),
            "Wavelet transform 2": (
                data.avg_amp_wt2 if amp_not_power else data.avg_pow_wt2,
                data.freq,
            ),
        }
        return _dict.get(plot_type)

    @staticmethod
    def get_side_plot_data_bispec(
        plot_type: str, freq: Tuple[float, float], data: BAOutputData
    ):
        """
        Gets the data required to plot the biphase and biamplitude on the side plots.
        Used when bispectrum is selected.

        :param freq: the selected frequencies (x and y)
        :param plot_type the plot type shown in the QComboBox, e.g. "b111"
        :param data the data object
        :return: biamplitude and biphase
        """
        key = ", ".join([str(f) for f in freq])

        try:
            biamp = data.biamp.get(key)
            biphase = data.biphase.get(key)
        except AttributeError:
            biamp = None
            biphase = None

        if "None" in key or biamp is None:
            return None, None

        _dict = {
            "b111": (biamp[0], biphase[0]),
            "b222": (biamp[1], biphase[1]),
            "b122": (biamp[2], biphase[2]),
            "b211": (biamp[3], biphase[3]),
        }
        biamp, biphase = _dict.get(plot_type)
        return biamp, biphase

    def get_main_plot_data(
        self, plot_type: str, data: BAOutputData
    ) -> Tuple[ndarray, ndarray, ndarray, bool]:
        """
        Gets the relevant arrays to plot in the main plot (WT or bispectrum).

        :param plot_type: the type of plot, as shown in the QComboBox; e.g. "Wavelet transform 1"
        :param data: the data object with all data
        :return: the x-values, the y-values, the c-values, and whether to use a log scale
        """
        if not isinstance(data, BAOutputData):
            return [None for _ in range(4)]

        plot_surr = self.view.get_plot_surrogates_selected()

        if self.plot_ampl:
            wt1 = data.amp_wt1
            wt2 = data.amp_wt2
        else:
            wt1 = data.pow_wt1
            wt2 = data.pow_wt2

        _dict = {
            "Wavelet transform 1": (data.times, data.freq, wt1, False),
            "Wavelet transform 2": (data.times, data.freq, wt2, False),
            "b111": (data.freq, data.freq, data.bispxxx, True),
            "b222": (data.freq, data.freq, data.bispppp, True),
            "b122": (data.freq, data.freq, data.bispxpp, True),
            "b211": (data.freq, data.freq, data.bisppxx, True),
        }
        tup = _dict.get(plot_type)
        if tup is None:  # All plots.
            pass  # TODO

        if plot_surr and self.params.surr_count > 0 and "transform" not in plot_type:
            tup = self.apply_surrogates(plot_type, data, tup)

        return tup

    def apply_surrogates(
        self,
        plot_type: str,
        data: BAOutputData,
        tup: Tuple[ndarray, ndarray, ndarray, bool],
    ) -> Tuple[ndarray, ndarray, ndarray, bool]:
        """
        Applies surrogates to the data.

        :param plot_type: the type of plot, e.g. "b111" or "b211"
        :param data: the BAOutputData instance containing the data
        :param tup: a tuple containing the frequencies, bispectrum and a bool
        :return: tuple replicating the tuple parameter, but with its bispectrum replaced by a
        surrogate-adjusted bispectrum
        """
        fx, fy, bisp, b = tup

        K = np.int(np.floor((self.params.surr_count + 1) * self.params.alpha))
        surr = {
            "b111": data.surrxxx,
            "b222": data.surrppp,
            "b122": data.surrxpp,
            "b211": data.surrpxx,
        }.get(plot_type)[:, :, K]

        bisp = bisp.copy()

        bisp -= surr
        bisp[bisp < 0] = np.NAN

        return fx, fy, bisp, b

    def on_bispectrum_completed(
        self,
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
        surrpxx: ndarray,
        opt: Dict,
    ) -> None:
        self.opt: Dict = opt

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
            surrpxx,
            opt,
            {},
            {},
        )

    def on_biphase_completed(
        self,
        name: str,
        freq_x: float,
        freq_y: float,
        biamp1: ndarray,
        biphase1: ndarray,
        biamp2: ndarray,
        biphase2: ndarray,
        biamp3: ndarray,
        biphase3: ndarray,
        biamp4: ndarray,
        biphase4: ndarray,
    ) -> None:
        sig = self.signals.get(name)
        key = f"{freq_x}, {freq_y}"

        data = sig.output_data

        data.biamp[key] = [[] for _ in range(4)]
        data.biphase[key] = [[] for _ in range(4)]

        data.biamp[key][0] = biamp1
        data.biphase[key][0] = biphase1

        data.biamp[key][1] = biamp2
        data.biphase[key][1] = biphase2

        data.biamp[key][2] = biamp3
        data.biphase[key][2] = biphase3

        data.biamp[key][3] = biamp4
        data.biphase[key][3] = biphase4

    @override
    async def coro_get_data_to_save(self) -> Optional[Dict]:
        if not self.opt or not self.params:
            return None

        output_data: List[BAOutputData] = [
            s.output_data for s, _ in self.signals.get_pairs()
        ]
        cols = len(output_data)

        first = output_data[0]

        amp = np.empty((*first.amp_wt1.shape, cols * 2))
        avg_amp = np.empty((first.avg_amp_wt1.shape[0], cols * 2))

        b111 = np.empty((*first.bispxxx.shape, cols))
        b222 = np.empty(b111.shape)
        b122 = np.empty(b111.shape)
        b211 = np.empty(b111.shape)

        freq = first.freq
        time = first.times

        for index in range(0, len(output_data) * 2, 2):
            d = output_data[index]

            amp[:, :, index] = d.amp_wt1[:]
            avg_amp[:, index] = d.avg_amp_wt1[:]

            amp[:, :, index + 1] = d.amp_wt2[:]
            avg_amp[:, index + 1] = d.avg_amp_wt2[:]

            b111[:, :, index] = d.bispxxx
            b222[:, :, index] = d.bispppp
            b122[:, :, index] = d.bispxpp
            b211[:, :, index] = d.bisppxx

        ba_data = {
            "amplitude": amp,
            "avg_amplitude": avg_amp,
            "frequency": freq,
            "time": time,
            "b111": b111,
            "b222": b222,
            "b122": b122,
            "b211": b211,
            "fr": self.view.get_f0() or 1,
            "fmin": self.opt["fmin"],
            "fmax": self.opt["fmax"],
            "preprocessing": "on" if self.params.preprocess else "off",
            "sampling_frequency": self.params.fs,
        }
        return {"BAData": sanitise(ba_data)}

    def load_data(self) -> None:
        """
        Loads the data from a file, showing a dialog to set the frequency of
        the signal.
        """
        self.signals = SignalPairs.from_file(self.open_file)

        if not self.signals.has_frequency():
            freq = FrequencyDialog().run_and_get()

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

            self.plot_preprocessed_signal()

    def get_selected_signal_pair(self) -> Tuple[TimeSeries, TimeSeries]:
        """
        Gets the currently selected signal pair as a tuple containing 2 signals.
        """
        return self.signals.get_pair_by_name(self.selected_signal_name)

    def get_params(self) -> BAParams:
        """Gets data from the GUI to create the params used by the bispectrum calculation."""
        return BAParams(
            signals=self.signals,
            preprocess=self.view.get_preprocess(),
            fmin=self.view.get_fmin(),
            fmax=self.view.get_fmax(),
            f0=self.view.get_f0(),
            nv=self.view.get_nv(),
            surr_count=self.view.get_surr_count(),
            alpha=self.view.get_alpha(),
            opt={},
        )
