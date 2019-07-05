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

from PyQt5 import uic
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QDialog

from data import resources
from gui.base.SelectFileDialog import SelectFileDialog
from gui.base.windows.MaximisedWindow import MaximisedWindow
from gui.timefrequency.TFPresenter import TFPresenter
from gui.timefrequency.TFView import TFView
from gui.timefrequency.plots.WFTPlot import WFTPlot


class TFWindow(MaximisedWindow, TFView):
    """
    The window which is used to perform time-frequency analysis.
    """

    def __init__(self, application):
        self.presenter = TFPresenter(self)
        TFView.__init__(self, application)
        MaximisedWindow.__init__(self)

    def init_ui(self):
        uic.loadUi(resources.get("layout:window_time_freq.ui"), self)
        self.update_title()
        self.setup_menu_bar()
        self.btn_calculate.clicked.connect(self.presenter.calculate)
        self.presenter.init()

    def update_title(self, title=""):
        super().update_title(title if title else self.presenter.get_window_name())

    def setup_menu_bar(self):
        menu = self.menubar
        file = menu.addMenu("File")
        file.addAction("Load data file")
        file.triggered.connect(self.select_file)

    def select_file(self):
        """Opens a dialog to select a file, and notifies the presenter."""
        dialog = SelectFileDialog()

        code = dialog.exec()
        if code == QDialog.Accepted:
            self.presenter.set_open_file(dialog.get_file())

    def plot_signal(self, time_series):
        """Plots the signal on the SignalPlot."""
        signal_plot = self.plot_top
        signal_plot.plot(time_series)

    def get_window(self) -> QWindow:
        return self

    def main_plot(self) -> WFTPlot:
        return self.plot_main
