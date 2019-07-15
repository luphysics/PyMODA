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
from PyQt5.QtWidgets import QDialog, QListWidgetItem

import errorhandling
import stdout_redirect
from gui.base.ErrorBox import ErrorBox
from gui.base.FrequencyDialog import FrequencyDialog
from gui.timefrequency.TFView import TFView
from maths.Signals import Signals
from maths.TFOutputData import TFOutputData
from maths.TimeSeries import TimeSeries
from maths.multiprocessing.MPHelper import MPHelper
from maths.algorithms.params import TFParams, _wft, _wt


class TFPresenter:
    """
    The Presenter in control of the time-frequency window.
    """

    def __init__(self, view: TFView):
        self.view = view
        self.is_plotted = False
        self.plot_ampl = True

        self.signals = None
        self.selected_signal_name = None
        # self.time_series = None
        self.open_file = None
        self.freq = None
        self.mp_handler = None
        self.logger = stdout_redirect.WindowLogger(self.on_log)

        errorhandling.subscribe(self.on_error)
        stdout_redirect.subscribe(self.logger)

    def init(self):
        # Add zoom listener to the signal plot, which is displayed in the top left.
        self.view.signal_plot().add_zoom_listener(self.on_signal_zoomed)

        # Open dialog to select a data file.
        self.view.select_file()

    def on_error(self, exc_type, value, traceback):
        """Called when an error occurs, provided that the debug argument is not in use."""
        self.cancel_calculate()
        ErrorBox(exc_type, value, traceback)

    def on_log(self, text):
        """Called when a log should occur; tells view to display message in log pane."""
        self.view.set_log_text(text)

    def on_signal_zoomed(self, rect):
        """Called when the signal plot (top left) is zoomed, and sets the x-limits."""
        if rect.is_valid():
            self.view.set_xlimits(rect.x1, rect.x2)
            self.signals.set_xlimits(rect.x1, rect.x2)

    def invalidate_data(self):
        """
        Sets the current data as invalid, so that it is not plotted
        while a calculation is in progress.
        """
        for d in self.signals:
            d.output_data.invalidate()

    def calculate(self):
        """Calculates the desired transform(s), and plots the result."""
        if self.mp_handler:
            self.mp_handler.stop()

        self.is_plotted = False
        self.view.main_plot().clear()
        self.view.main_plot().set_in_progress(True)
        self.invalidate_data()

        params = self.get_params()

        self.mp_handler = MPHelper()
        self.mp_handler.wft(
            params=params,
            window=self.view.get_window(),
            on_result=self.on_calculation_completed)

        log: bool = (params.transform == _wt)
        self.view.main_plot().set_log_scale(logarithmic=log)
        self.view.amplitude_plot().set_log_scale(logarithmic=log)

        self.view.on_calculate_started()
        print("Started calculation...")

    def on_calculation_completed(self, name, times, freq, ampl, powers, avg_ampl, avg_pow):
        """Called when the calculation of the desired transform(s) is completed."""
        self.view.on_calculate_stopped()

        t = self.signals.get(name)
        t.output_data = TFOutputData(
            times,
            ampl,
            freq,
            powers,
            avg_ampl,
            avg_pow
        )

        if self.selected_signal_name == t.name:
            self.plot_output()
            print("Completed calculation.")

    def get_values_to_plot(self, amplitude=None) -> tuple:
        """
        Returns the data needed to plot the transform.
        :param amplitude: overrides the normal value of whether to plot amplitude instead of power
        :return: the times, frequencies, amplitudes/powers, and average amplitudes/powers
        """
        amp: bool = self.plot_ampl
        if amplitude is not None:
            amp = amplitude

        tf_data = self.get_selected_signal().output_data
        if not tf_data.is_valid():
            return None, None, None, None

        if amp:
            values = tf_data.ampl
            avg_values = tf_data.avg_ampl
        else:
            values = tf_data.powers
            avg_values = tf_data.avg_pow

        return tf_data.times, tf_data.freq, values, avg_values

    def cancel_calculate(self):
        """
        Cancels the calculation of the desired transform(s),
        killing their processes immediately.
        """
        if self.mp_handler:
            self.mp_handler.stop()
        self.view.on_calculate_stopped()
        self.is_plotted = False
        print("Calculation terminated.")

    def set_plot_type(self, amplitude_selected=True):
        """
        Set the type of plot to display (power or amplitude). This affects
        the main plot and the amplitude plot.

        :param amplitude_selected: whether to set the plot type as amplitude (not power)
        """
        self.plot_ampl = amplitude_selected
        if self.is_plotted:
            t, f, values, avg_values = self.get_values_to_plot()
            self.plot(t, f, values, avg_values)

    def plot(self, times, freq, values, avg_values):
        self.view.main_plot().plot(times, values, freq)
        self.view.amplitude_plot().plot(avg_values, freq)

    def plot_output(self):
        """
        Plots the output of the WT/WFT calculations for the currently selected signal.
        """
        t, f, values, avg_values = self.get_values_to_plot()

        if t is not None and f is not None:
            self.plot(t, f, values, avg_values)
            self.is_plotted = True

    def get_params(self) -> TFParams:
        """
        Creates the parameters to use when performing the calculations.
        """
        return TFParams.create(
            signals=self.signals,
            fmin=self.view.get_fmin(),
            fmax=self.view.get_fmax(),
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

    def load_data(self):
        """
        Loads the time-series data from the currently
        selected file, and allows the frequency to be set
        via a dialog.
        """
        self.signals = Signals.from_file(self.open_file)
        if not self.signals.has_frequency():
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
        self.signals.set_frequency(freq)

    def plot_signal(self):
        """Plots the signal on the SignalPlot."""
        self.view.plot_signal(self.get_selected_signal())

    def on_data_loaded(self):
        """Called when the time-series data has been loaded."""
        self.view.update_signal_listview(self.signals.names())
        self.plot_signal()

    def on_signal_selected(self, item):
        """
        Called when a signal is selected in the QListWidget.
        Plots the new signal in the top-left plot and, if
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
            self.plot_output()

    def get_window_name(self) -> str:
        """
        Gets the name of this window, adding the currently open file
        if applicable.
        """
        title = self.view._name
        if self.open_file:
            title += f" - {self.open_file}"
        return title

    def set_open_file(self, file: str):
        """Sets the name of the data file in use, and loads its data."""
        self.open_file = file
        print(f"Opening {self.open_file}...")
        self.view.update_title()
        self.load_data()

    def get_selected_signal(self) -> TimeSeries:
        """Returns the currently selected signal as a TimeSeries."""
        return self.signals.get(self.selected_signal_name)
