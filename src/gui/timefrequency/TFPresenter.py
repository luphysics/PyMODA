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

from gui.base.FrequencyDialog import FrequencyDialog
from gui.timefrequency.TFView import TFView
from maths.TimeSeries import TimeSeries
from maths.algorithms.mp_maths import MPHelper
from maths.algorithms.params import WFTParams


class TFPresenter:
    """
    The Presenter in control of the time-frequency window.
    """

    def __init__(self, view: TFView):
        self.view = view
        self.freq = None
        self.time_series = None
        self.open_file = None
        self.mp = None

    def init(self):
        self.view.select_file()

    def calculate(self):
        """Calculates the desired transform(s), and plots the result."""
        if self.mp:
            self.mp.stop()

        self.view.main_plot().clear()
        self.view.main_plot().set_in_progress()

        self.mp = MPHelper()
        self.mp.wft(
            params=self.get_params(),
            window=self.view.get_window(),
            on_result=self.view.main_plot().plot)

        self.view.on_calculate_started()

    def cancel_calculate(self):
        if self.mp:
            self.mp.stop()
        self.view.on_calculate_stopped()

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
        """Loads the time-series data from a file, via a dialog."""
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
