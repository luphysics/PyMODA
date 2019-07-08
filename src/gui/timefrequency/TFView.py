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
from PyQt5.QtGui import QWindow

from gui.base.components.PlotComponent import PlotComponent
from gui.timefrequency.plots.AmplitudePlot import AmplitudePlot
from gui.timefrequency.plots.WFTPlot import WFTPlot


class TFView:
    """
    A View class to be subclassed by the time-frequency window.
    """

    name = "Time-Frequency Analysis"

    def __init__(self, application):
        self.application = application

    def plot_signal(self, time_series):
        """Plots the signal on the SignalPlot."""
        pass

    def select_file(self):
        """Opens a dialog to select a file, and notifies the presenter."""
        pass

    def update_title(self, title=""):
        pass

    def main_plot(self) -> WFTPlot:
        """Returns the main plot, which is used to display the transform."""
        pass

    def amplitude_plot(self) -> AmplitudePlot:
        pass

    def get_window(self) -> QWindow:
        pass

    def setup_radio_plot(self):
        """Set up the radio buttons for plot amplitude/power."""
        pass

    def setup_radio_transform(self):
        pass

    def setup_radio_preproc(self):
        pass

    def setup_radio_cut_edges(self):
        pass

    def setup_radio_stats_avg(self):
        pass

    def setup_radio_stats_paired(self):
        pass

    def setup_radio_test(self):
        pass

    def get_preprocessing(self):
        pass

    def get_fmin(self) -> float:
        pass

    def get_fmax(self) -> float:
        pass

    def get_f0(self) -> float:
        pass

    def get_fstep(self) -> float:
        pass

    def get_padding(self) -> str:
        pass

    def get_rel_tolerance(self) -> float:
        pass

    def get_cut_edges(self) -> bool:
        pass

    def get_preprocess(self) -> bool:
        pass

    def get_transform_window(self) -> str:
        pass

    def on_calculate_started(self):
        pass

    def on_calculate_stopped(self):
        pass
