#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2019  Lancaster University
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
import string

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from data import resources
from gui.base.SelectFileDialog import SelectFileDialog
from gui.base.windows.MaximisedWindow import MaximisedWindow
from gui.timefrequency.FrequencyDialog import FrequencyDialog
from gui.timefrequency.SignalPlot import SignalPlot
from maths.TimeSeries import TimeSeries


class TimeFreqWindow(MaximisedWindow):
    """
    The window which is used to perform time-frequency analysis.
    """

    name = "Time-Frequency Analysis"
    open_file: string = None
    freq: float = None
    time_series: TimeSeries = None

    def __init__(self, application):
        super().__init__()
        self.application = application

    def maximise_on_start(self):
        return True  # Just here for testing purposes.

    def init_ui(self):
        uic.loadUi(resources.get("layout:window_time_freq.ui"), self)
        self.set_title()
        self.setup_menu_bar()
        self.select_file()

        self.plot_main.plot(None)

    def set_title(self, name=""):
        super(TimeFreqWindow, self).set_title(self.get_window_name())

    def get_window_name(self):
        """
        Gets the name of this window, adding the currently open file
        if applicable.
        """
        title = self.name
        if self.open_file:
            title += f" - {self.open_file}"
        return title

    def setup_menu_bar(self):
        menu = self.menubar
        file = menu.addMenu("File")
        file.addAction("Load data file")
        file.triggered.connect(self.select_file)

    def select_file(self):
        """Opens a dialog to select a file, and gets the result."""
        dialog = SelectFileDialog()

        code = dialog.exec()
        if code == QDialog.Accepted:
            self.open_file = dialog.get_file()
            print(f"Opening {self.open_file}...")
            self.set_title()
            self.load_data()

    def load_data(self):
        """Loads the time-series data."""
        self.time_series = TimeSeries.from_file(self.open_file)
        if not self.time_series.has_frequency():
            dialog = FrequencyDialog(self.on_freq_changed)
            code = dialog.exec()
            if code == QDialog.Accepted:
                self.set_frequency(self.freq)
                self.on_data_loaded()

    def on_data_loaded(self):
        """Called when the time-series data has been loaded."""
        self.plot_signal()

    def on_freq_changed(self, freq):
        """Called when the frequency is changed."""
        self.freq = float(freq)

    def set_frequency(self, freq: float):
        """Sets the frequency of the time-series."""
        self.time_series.set_frequency(freq)

    def plot_signal(self):
        """Plots the signal on the SignalPlot."""
        signal_plot: SignalPlot = self.plot_top
        signal_plot.plot(self.time_series)
