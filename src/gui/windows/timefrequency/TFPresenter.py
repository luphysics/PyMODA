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

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.base.analysis.BaseTFPresenter import BaseTFPresenter
from maths.Signals import Signals
from maths.TFOutputData import TFOutputData
from maths.TimeSeries import TimeSeries
from maths.algorithms.TFParams import TFParams, _wt, _wft, create
from maths.algorithms.preprocessing import preprocess
from maths.multiprocessing.MPHelper import MPHelper


class TFPresenter(BaseTFPresenter):
    """
    The Presenter in control of the time-frequency window.
    """

    def get_total_tasks_count(self) -> int:
        return len(self.signals) if self.is_calculating_all else 1

    def calculate(self, calculate_all: bool):
        """Calculates the desired transform(s), and plots the result."""
        self.set_calculating_all(calculate_all)

        if self.mp_handler:
            self.mp_handler.stop()

        params = self.get_params(all_signals=calculate_all)
        if params.transform == _wft:
            if self.view.get_fmin() is None:
                # Will be caught by error handling and shown as a dialog.
                raise Exception("Minimum frequency must be defined for WFT.")

        self.is_plotted = False
        self.view.main_plot().clear()
        self.view.main_plot().set_in_progress(True)
        self.invalidate_data()

        self.mp_handler = MPHelper()
        self.mp_handler.wft(
            params=params,
            window=self.view.get_window(),
            on_result=self.on_calculation_completed)

        log: bool = (params.transform == _wt)
        self.view.main_plot().set_log_scale(logarithmic=log)
        self.view.amplitude_plot().set_log_scale(logarithmic=log)

        self.view.on_calculate_started()
        self.view.update_progress(0, self.get_total_tasks_count())
        print("Started calculation...")

    def on_calculation_completed(self, name, times, freq, values, ampl, powers, avg_ampl, avg_pow):
        """Called when the calculation of the desired transform(s) is completed."""
        self.view.on_calculate_stopped()

        t = self.signals.get(name)
        t.output_data = TFOutputData(
            times,
            values,
            ampl,
            freq,
            powers,
            avg_ampl,
            avg_pow
        )

        print(f"Finished calculation for '{name}'.")
        self.on_task_completed(self.get_total_tasks_count())

        # Plot result if all signals finished.
        if all([s.output_data.is_valid() for s in self.signals_calc]):
            self.plot_output()
            self.on_all_tasks_completed()

    def get_values_to_plot(self, amplitude=None) -> tuple:
        """
        Returns the data needed to plotting the transform.
        :param amplitude: overrides the normal value of whether to plotting amplitude instead of power
        :return: the times, frequencies, amplitudes/powers, and average amplitudes/powers
        """
        amp: bool = self.plot_ampl
        if amplitude is not None:
            amp = amplitude

        tf_data = self.get_selected_signal().output_data
        if not tf_data.is_valid():
            return None, None, None, None

        if amp:  # Plot amplitudes.
            values = tf_data.ampl
            avg_values = tf_data.avg_ampl
        else:  # Plot powers.
            values = tf_data.powers
            avg_values = tf_data.avg_pow

        return tf_data.times, tf_data.freq, values, avg_values

    def set_plot_type(self, amplitude_selected=True):
        """
        Set the type of plotting to display (power or amplitude). This affects
        the main plotting and the amplitude plotting.

        :param amplitude_selected: whether to set the plotting type as amplitude (not power)
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
        else:
            self.view.main_plot().clear()
            self.view.amplitude_plot().clear()

    def get_params(self, all_signals=True) -> TFParams:
        """
        Creates the parameters to use when performing the calculations.
        """
        if all_signals:
            self.signals_calc = self.signals
        else:
            self.signals_calc = self.signals.only(self.selected_signal_name)

        return create(
            params_type=TFParams,
            signals=self.signals_calc,
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

    def plot_signal(self):
        """Plots the signal on the SignalPlot."""
        self.view.plot_signal(self.get_selected_signal())

    def plot_preprocessed(self):
        sig = self.get_selected_signal()
        p = preprocess(sig.signal, sig.frequency, 0.2, 3)
        self.view.plot_preproc.plot(sig.times, sig.signal, p)

    def on_data_loaded(self):
        """Called when the time-series data has been loaded."""
        self.view.update_signal_listview(self.signals.names())
        self.plot_signal()
        self.plot_preprocessed()

    def on_signal_selected(self, item):
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
            self.plot_output()

    def get_selected_signal(self) -> TimeSeries:
        """Returns the currently selected signal as a TimeSeries."""
        return self.signals.get(self.selected_signal_name)
