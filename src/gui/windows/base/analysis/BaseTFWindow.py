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
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from gui.dialogs.files.SelectFileDialog import SelectFileDialog
from gui.windows.base.MaximisedWindow import MaximisedWindow
from gui.windows.base.analysis.BaseTFView import BaseTFView
from gui.windows.timefrequency.plots.AmplitudePlot import AmplitudePlot
from gui.windows.timefrequency.plots.SignalPlot import SignalPlot
from gui.windows.timefrequency.plots.WFTPlot import WFTPlot


class BaseTFWindow(MaximisedWindow, BaseTFView):
    """
    A base analysis window that handles Qt-related code.
    """

    def get_layout_file(self) -> str:
        pass

    def update_title(self, title=""):
        super().update_title(title if title else self.presenter.get_window_name())

    def select_file(self):
        dialog = SelectFileDialog()

        code = dialog.exec()
        if code == QDialog.Accepted:
            self.presenter.set_open_file(dialog.get_file())

    def setup_menu_bar(self):
        menu = self.menubar
        file = menu.addMenu("File")
        file.addAction("Load data file")
        file.triggered.connect(self.select_file)

    def init_ui(self):
        uic.loadUi(self.get_layout_file(), self)
        self.update_title()
        self.setup_menu_bar()

        # Setup radio buttons and other UI elements.
        self.setup_radio_preproc()
        self.setup_radio_cut_edges()
        self.setup_signal_listview()
        self.setup_xlim_edits()

        self.btn_calculate.clicked.connect(self.presenter.calculate)
        self.presenter.init()

    def main_plot(self) -> WFTPlot:
        return self.plot_main

    def signal_plot(self) -> SignalPlot:
        return self.plot_top

    def amplitude_plot(self) -> AmplitudePlot:
        return self.plot_right
