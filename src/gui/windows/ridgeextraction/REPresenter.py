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
from typing import Tuple, Union, Dict, Optional, List

import numpy as np
from PyQt5.QtWidgets import QListWidgetItem
from numpy import ndarray

from gui.windows.timefrequency.TFPresenter import TFPresenter
from maths.params.REParams import REParams
from maths.params.TFParams import create
from maths.signals.data.TFOutputData import TFOutputData
from utils.decorators import override
from utils.dict_utils import sanitise


class REPresenter(TFPresenter):
    """
    The presenter in control of the ridge-extraction window.

    Inherits from TFPresenter because REPresenter requires much of the same functionality.
    """

    def __init__(self, view):
        super(REPresenter, self).__init__(view)

        from gui.windows.ridgeextraction.REWindow import REWindow

        self.view: REWindow = view
        self.re_params: REParams = None

    @override
    def calculate(self, calculate_all: bool) -> None:
        self.view.set_ridge_filter_disabled(True)
        self.view.switch_to_single_plot()
        super(REPresenter, self).calculate(calculate_all)

    @override
    def on_all_transforms_completed(self) -> None:
        super(REPresenter, self).on_all_transforms_completed()
        self.view.set_ridge_filter_disabled(False)

    def on_ridge_extraction_clicked(self) -> None:
        intervals = self.view.get_interval_strings()
        if len(intervals) < 1:
            raise Exception(
                "At least one interval must be specified for ridge extraction."
            )

        print("Starting ridge extraction...")
        self.view.clear_all()
        self.view.switch_to_three_plots()

        asyncio.ensure_future(self.coro_ridge_extraction())

    async def coro_ridge_extraction(self) -> None:
        self.enable_save_data(False)

        params = self.get_re_params()
        self.re_params = params

        data: tuple = await self.mp_handler.coro_ridge_extraction(
            params, on_progress=self.on_progress_updated
        )

        for d in data:
            self.on_ridge_completed(*d)

        self.on_all_ridge_completed()

    def on_ridge_completed(
        self,
        name,
        times,
        freq,
        values,
        ampl,
        powers,
        avg_ampl,
        avg_pow,
        interval,
        filtered_signal,
        iphi,
        ifreq,
    ) -> None:
        sig = self.signals.get(name)

        d: TFOutputData = sig.output_data

        d.set_ridge_data(interval, filtered_signal, ifreq, iphi)
        d.values = values

        d.ampl = ampl
        d.powers = powers

        d.avg_ampl = avg_ampl
        d.avg_pow = avg_pow

        d.freq = freq
        d.times = times

    def on_all_ridge_completed(self) -> None:
        print("All ridge extraction completed.")
        sig = self.get_selected_signal()
        data = sig.output_data

        times = data.times

        main = self.view.main_plot()
        main.plot(times, data.ampl, data.freq)
        self.plot_ridge_data(data)

        self.enable_save_data(True)

    def plot_ridge_data(self, data: TFOutputData) -> None:
        times = data.times
        filtered, freq, phi = data.get_ridge_data(self.view.get_selected_interval())

        self.triple_plot(times, filtered, freq, phi, data.ampl, data.freq)

    def plot_band_data(self, data: TFOutputData) -> None:
        times = data.times
        band_data = data.get_band_data(self.view.get_selected_interval())

        if band_data:
            bands, phi, amp = band_data
            self.triple_plot(times, bands, amp, phi)

    def triple_plot(
        self,
        x_values: ndarray,
        top_y: ndarray,
        middle_y: ndarray,
        bottom_y: ndarray,
        main_values: ndarray = None,
        main_freq: ndarray = None,
    ) -> None:
        """
        Plots values on the 3 plots in the main section of the window.

        :param x_values: the values plotted on the x-axes (will be time values)
        :param top_y: the values plotted on the y-axis of the top plot
        :param middle_y: the values plotted on the y-axis of the middle plot
        :param bottom_y: the values plotted on the y-axis of the bottom plot
        :param main_values: when the middle plot is showing the result of the wavelet transform,
        these will be the amplitudes of the transform plotted on the middle plot
        :param main_freq: when the middle plot is showing the result of the wavelet transform,
        these will be the frequencies of the transform plotted on the middle plot
        """
        main = self.view.main_plot()
        main.clear()

        if main_values is not None and main_freq is not None:
            main.plot(x_values, main_values, main_freq)

        main.plot_line(x_values, middle_y, xlim=True)
        main.update()

        top = self.view.get_re_top_plot()
        top.clear()
        top.plot(x_values, top_y)

        bottom = self.view.get_re_bottom_plot()
        bottom.clear()
        bottom.plot(x_values, bottom_y)

    @override
    def on_signal_selected(self, item: Union[QListWidgetItem, str]) -> None:
        super().on_signal_selected(item)

        data = self.get_selected_signal().output_data
        if data.has_ridge_data():
            d = data.get_ridge_data(self.view.get_selected_interval())
            if d:
                _, freq, _ = d
                if freq is not None and len(freq) > 0:
                    self.plot_ridge_data(data)
            else:
                self.view.clear_all()

        if data.has_band_data():
            d = data.get_band_data(self.view.get_selected_interval())
            if d:
                self.plot_band_data(data)

    def on_interval_selected(self, interval: Tuple[float, float]) -> None:
        """Called when a frequency interval is selected."""
        if interval:
            fmin, fmax = interval
            print(f"Selected interval: {fmin}, {fmax}")
            self.plot_band_data(self.get_selected_signal().output_data)

    def on_filter_clicked(self) -> None:
        """Called when the "bandpass filter" button is clicked."""
        print("Starting filtering...")
        asyncio.ensure_future(self.coro_bandpass_filter())

    async def coro_bandpass_filter(self) -> None:
        data = await self.mp_handler.coro_bandpass_filter(
            self.signals,
            self.view.get_interval_tuples(),
            on_progress=self.on_progress_updated,
        )

        for d in data:
            name, bands, phase, amp, interval = d
            output_data = self.signals.get(name).output_data
            output_data.set_band_data(interval, bands, phase, amp)

        self.on_all_filter_completed()

    def on_all_filter_completed(self) -> None:
        """
        Called when all bandpass filter calculations have finished.
        """
        self.view.switch_to_three_plots()

        sig = self.get_selected_signal()
        data = sig.output_data

        main = self.view.main_plot()
        main.clear()
        self.plot_band_data(data)

        self.enable_save_data(True)

    @override
    async def coro_get_data_to_save(self) -> Optional[Dict]:
        tf_data = await super().coro_get_data_to_save()
        if not tf_data:
            return None

        output_data: List[TFOutputData] = [s.output_data for s in self.signals]
        cols = len(output_data)

        r_intervals = []
        r_freq = np.empty((tf_data["TFData"]["time"].size, cols))
        r_phase = np.empty(r_freq.shape)
        r_bands = np.empty(r_freq.shape)
        r_bands_phi = np.empty(r_freq.shape)
        r_bands_amp = np.empty(r_freq.shape)

        for index, d in enumerate(output_data):
            for key, value in d.ridge_data.items():
                filt, freq, phase = value

                if key not in r_intervals:
                    r_intervals.append(key)

                r_freq[:, index] = freq
                r_phase[:, index] = phase

            try:
                for key, value in d.band_data.items():
                    bands, phi, amp = value

                    if key not in r_intervals:
                        r_intervals.append(key)

                    r_bands[:, index] = bands
                    r_bands_phi[:, index] = phi
                    r_bands_amp[:, index] = amp
            except:
                pass

        ridge = {
            "frequency_bands": r_intervals,
            "ridge_frequency": r_freq,
            "ridge_phase": r_phase,
        }

        re_data = {**tf_data["TFData"], **ridge}

        return {"REData": sanitise(re_data)}

    def get_re_params(self) -> REParams:
        """
        Gets the ridge extraction params which are passed to the algorithm.
        """
        return create(
            signals=self.signals,
            params_type=REParams,
            intervals=self.view.get_interval_tuples(),
            # fmin=fmin,
            # fmax=fmax,
            f0=self.view.get_f0(),
            # Only one of these two will be used, depending on the selected transform.
            window=self.view.get_wt_wft_type(),
            wavelet=self.view.get_wt_wft_type(),
            cut_edges=self.view.get_cut_edges(),
            preprocess=self.view.get_preprocess(),
            transform=self.view.get_transform_type(),
        )
