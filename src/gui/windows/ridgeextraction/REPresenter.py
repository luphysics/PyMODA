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
from typing import Tuple, Union

import numpy as np
from PyQt5.QtWidgets import QListWidgetItem
from nptyping import Array

from gui.windows.ridgeextraction.REView import REView
from gui.windows.timefrequency.TFPresenter import TFPresenter
from maths.params.REParams import REParams
from maths.params.TFParams import create

from maths.signals.TFOutputData import TFOutputData


class REPresenter(TFPresenter):
    """
    The presenter in control of the ridge-extraction window.

    Inherits from TFPresenter because REPresenter requires much of the same functionality.
    """

    def __init__(self, view: REView):
        super(REPresenter, self).__init__(view)

    def calculate(self, calculate_all: bool):
        self.view.set_ridge_filter_disabled(True)
        self.view.switch_to_single_plot()
        super(REPresenter, self).calculate(calculate_all)

    def on_all_transforms_completed(self):
        super(REPresenter, self).on_all_transforms_completed()
        self.view.set_ridge_filter_disabled(False)

    def on_ridge_extraction_clicked(self):
        intervals = self.view.get_interval_strings()
        if len(intervals) < 1:
            raise Exception("At least one interval must be specified for ridge extraction.")

        print("Starting ridge extraction...")
        self.view.clear_all()
        self.view.switch_to_three_plots()

        self.mp_handler.ridge_extraction(self.get_re_params(),
                                         self.view,
                                         self.on_ridge_completed,
                                         on_progress=self.on_progress_updated)

    def on_ridge_completed(self,
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
                           ifreq
                           ):

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

        if all([i.output_data.has_ridge_data() for i in self.signals]):
            self.on_all_ridge_completed()

    def on_all_ridge_completed(self):
        print("All ridge extraction completed.")
        sig = self.get_selected_signal()
        data = sig.output_data

        times = data.times

        main = self.view.main_plot()
        main.plot(times, data.ampl, data.freq)
        self.plot_ridge_data(data)

    def plot_ridge_data(self, data: TFOutputData):
        times = data.times
        filtered, freq, phi = data.get_ridge_data(self.view.get_selected_interval())

        self.triple_plot(times, filtered, freq, phi, data.ampl, data.freq)

    def plot_band_data(self, data: TFOutputData):
        times = data.times
        band_data = data.get_band_data(self.view.get_selected_interval())

        if band_data:
            bands, phi, amp = band_data
            self.triple_plot(times, bands, amp, phi)

    def triple_plot(
            self,
            x_values: Array,
            top_y: Array,
            middle_y: Array,
            bottom_y: Array,
            main_values: Array = None,
            main_freq: Array = None
    ):
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

    def on_signal_selected(self, item: Union[QListWidgetItem, str]):
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

        if data.has_band_data():  # TODO: plot correct type
            d = data.get_band_data(self.view.get_selected_interval())
            if d:
                self.plot_band_data(data)

    def on_interval_selected(self, interval: Tuple[float, float]):
        """Called when a frequency interval is selected."""
        if not interval:
            return

        fmin, fmax = interval
        print(f"Selected interval: {fmin}, {fmax}")
        self.plot_band_data(self.get_selected_signal().output_data)

    def on_filter_clicked(self):
        """Called when the "bandpass filter" button is clicked."""
        print("Starting filtering...")

        self.mp_handler.bandpass_filter(
            self.signals,
            self.view.get_interval_tuples(),
            self.view,
            self.on_filter_completed,
            on_progress=self.on_progress_updated
        )

    def on_filter_completed(
            self,
            name: str,
            bands,
            phase,
            amp,
            interval: Tuple[float, float]
    ):
        """
        Called when the bandpass filter completes.
        """
        d: TFOutputData = self.signals.get(name).output_data
        d.set_band_data(interval, bands, phase, amp)

        if all([i.output_data.has_band_data() for i in self.signals]):
            self.on_all_filter_completed()

    def on_all_filter_completed(self):
        """
        Called when all bandpass filter calculations have finished.
        """
        self.view.switch_to_three_plots()
        print("All bandpass filtering completed.")

        sig = self.get_selected_signal()
        data = sig.output_data

        main = self.view.main_plot()
        main.clear()
        self.plot_band_data(data)

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
            fstep=self.view.get_fstep(),
            padding=self.view.get_padding(),

            # Only one of these two will be used, depending on the selected transform.
            window=self.view.get_wt_wft_type(),
            wavelet=self.view.get_wt_wft_type(),

            rel_tolerance=self.view.get_rel_tolerance(),
            cut_edges=self.view.get_cut_edges(),
            preprocess=self.view.get_preprocess(),
            transform=self.view.get_transform_type(),
        )
