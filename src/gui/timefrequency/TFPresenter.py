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
from PyQt5.QtWidgets import QDialog

import errorhandling
from gui.base.ErrorBox import ErrorBox
from gui.base.FrequencyDialog import FrequencyDialog
from gui.timefrequency.TFView import TFView
from maths.TimeSeries import TimeSeries
from maths.multiprocessing.MPHelper import MPHelper
from maths.algorithms.params import WFTParams


class TFPresenter:
    """
    The Presenter in control of the time-frequency window.
    """

    def __init__(self, view: TFView):
        self.view = view
        self.is_plotted = False
        self.plot_ampl = True

        self.time_series = None
        self.open_file = None
        self.freq = None
        self.mp_handler = None

        errorhandling.subscribe(self.on_error)

    def init(self):
        # Add zoom listener to the signal plot, which is displayed in the top left.
        self.view.signal_plot().add_zoom_listener(self.on_signal_zoomed)

        # Open dialog to select a data file.
        self.view.select_file()

    def on_error(self, exc_type, value, traceback):
        self.cancel_calculate()
        ErrorBox(exc_type, value, traceback)

    def on_signal_zoomed(self, rect):
        if rect.is_valid():
            self.view.set_xlimits(rect.x1, rect.x2)
            self.time_series.set_xlimits(rect.x1, rect.x2)

    def calculate(self):
        """Calculates the desired transform(s), and plots the result."""
        if self.mp_handler:
            self.mp_handler.stop()

        self.is_plotted = False
        self.view.main_plot().clear()
        self.view.main_plot().set_in_progress(True)

        self.mp_handler = MPHelper()
        self.mp_handler.wft(
            params=self.get_params(),
            window=self.view.get_window(),
            on_result=self.on_calculation_completed)

        self.view.on_calculate_started()

    def on_calculation_completed(self, times, ampl, freq, powers, avg_ampl, avg_pow):
        """Called when the calculation of the desired transform(s) is completed."""
        self.view.on_calculate_stopped()

        self.times = times
        self.ampl = ampl
        self.frequencies = freq
        self.powers = powers
        self.avg_ampl = avg_ampl
        self.avg_pow = avg_pow

        values, avg_values = self.get_values_to_plot()

        self.plot(times, freq, values, avg_values)
        self.is_plotted = True

    def get_values_to_plot(self, amplitude=None):
        amp = self.plot_ampl
        if amplitude is not None:
            amp = amplitude

        if amp:
            values = self.ampl
            avg_values = self.avg_ampl
        else:
            values = self.powers
            avg_values = self.avg_pow

        return values, avg_values

    def cancel_calculate(self):
        """
        Cancels the calculation of the desired transform(s),
        killing their processes immediately.
        """
        if self.mp_handler:
            self.mp_handler.stop()
        self.view.on_calculate_stopped()
        self.is_plotted = False

    def set_plot_type(self, amplitude_selected):
        """
        Set the type of plot to display (power or amplitude). This affects
        the main plot and the amplitude plot.

        :param amplitude_selected: whether to set the plot type as amplitude (not power)
        """
        self.plot_ampl = amplitude_selected
        if self.is_plotted:
            values, avg_values = self.get_values_to_plot()
            self.plot(self.times, self.frequencies, values, avg_values)

    def plot(self, times, freq, values, avg_values):
        self.view.main_plot().plot(times, values, freq)
        self.view.amplitude_plot().plot(avg_values, freq)

    def get_params(self) -> WFTParams:
        """Creates the parameters to use when performing the calculations."""
        return WFTParams.create(
            time_series=self.time_series,
            fmin=self.view.get_fmin(),
            fmax=self.view.get_fmax(),
            f0=self.view.get_f0(),
            fstep=self.view.get_fstep(),
            padding=self.view.get_padding(),
            window=self.view.get_transform_window(),
            rel_tolerance=self.view.get_rel_tolerance(),
            cut_edges=self.view.get_cut_edges(),
            preprocess=self.view.get_preprocess(),
        )

    def load_data(self):
        """
        Loads the time-series data from the currently
        selected file, via a dialog.
        """
        self.time_series = TimeSeries.from_file(self.open_file)
        if not self.time_series.has_frequency():
            dialog = FrequencyDialog(self.on_freq_changed)
            code = dialog.exec()
            if code == QDialog.Accepted:
                self.set_frequency(self.freq)
                self.on_data_loaded()

    def on_freq_changed(self, freq):
        """Called when the frequency is changed."""
        self.freq = float(freq)

    def set_frequency(self, freq: float):
        """Sets the frequency of the time-series."""
        self.time_series.set_frequency(freq)

    def plot_signal(self):
        """Plots the signal on the SignalPlot."""
        self.view.plot_signal(self.time_series)

    def on_data_loaded(self):
        """Called when the time-series data has been loaded."""
        self.plot_signal()

    def get_window_name(self) -> str:
        """
        Gets the name of this window, adding the currently open file
        if applicable.
        """
        title = self.view.name
        if self.open_file:
            title += f" - {self.open_file}"
        return title

    def set_open_file(self, file: str):
        self.open_file = file
        print(f"Opening {self.open_file}...")
        self.view.update_title()
        self.load_data()
