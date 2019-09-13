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
from gui.common.BaseTFViewProperties import BaseTFViewProperties
from gui.plotting.plots.AmplitudePlot import AmplitudePlot
from gui.plotting.plots.SignalPlot import SignalPlot
from gui.plotting.plots.ColorMeshPlot import ColorMeshPlot


class BaseTFView(BaseTFViewProperties):
    """
    A base "View" class in MVP, which defines
    """

    # The title of the window.
    name = ""

    def __init__(self, application, presenter):
        BaseTFViewProperties.__init__(self)
        self.application = application

        # Prevent circular imports.
        from gui.common import BaseTFPresenter
        self.presenter: BaseTFPresenter = presenter

    def plot_signal(self, time_series):
        """Plots the signal on the SignalPlot."""
        pass

    def select_file(self):
        """Opens a dialog to select a file, and notifies the presenter."""
        pass

    def update_title(self, title=""):
        pass

    def main_plot(self) -> ColorMeshPlot:
        """Returns the main plot, which is used to display the transform."""
        pass

    def signal_plot(self) -> SignalPlot:
        pass

    def amplitude_plot(self) -> AmplitudePlot:
        pass

    def get_window(self):
        pass

    def setup_lineedit_fmin(self):
        pass

    def setup_lineedit_fmax(self):
        pass

    def setup_lineedit_res(self):
        pass

    def setup_radio_plot(self):
        """Set up the radio buttons for plotting amplitude/power."""
        pass

    def on_plot_type_toggled(self, ampl_selected):
        """
        Triggered when plotting type is changed from amplitude to power, or vice versa.
        :param ampl_selected: whether the plotting type is amplitude, not power
        """
        self.presenter.set_plot_type(ampl_selected)

    def setup_progress(self):
        """Sets up the progress bar which displays tasks in progress."""
        pass

    def update_progress(self, current, total):
        """Updates the progress bar with the current number of tasks completed."""
        pass

    def progress_message(self, current=0, total=0):
        """Gets the text to display under the progress bar."""
        if current < total:
            return f"Completed task {current} of {total}."
        return "No tasks in progress."

    def set_xlimits(self, x1, x2):
        """Sets the x-limits of the data."""
        pass

    def setup_xlim_edits(self):
        """Sets up the LineEdit widgets which allow the x-limits to be set."""
        pass

    def on_xlim_edited(self):
        """Called when the x-limits are edited."""
        pass

    def setup_radio_preproc(self):
        pass

    def setup_radio_cut_edges(self):
        pass

    def get_preprocessing(self):
        pass

    def get_fmin(self) -> float:
        pass

    def get_fmax(self) -> float:
        pass

    def get_f0(self) -> float:
        pass

    def get_preprocess(self) -> bool:
        pass

    def on_calculate_started(self):
        pass

    def on_calculate_stopped(self):
        pass

    def set_log_text(self, text):
        """Sets the text to display in the log section."""
        pass

    def setup_signal_listview(self):
        pass

    def update_signal_listview(self, items):
        """Updates the list displaying the signals."""
        pass

    def get_button_calculate_all(self):
        """Returns the button for calculating using all signals ("transform all")."""
        pass

    def get_button_calculate_single(self):
        """Returns the button for calculating using one signal ("transform single")."""
        pass
