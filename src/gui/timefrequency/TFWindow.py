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
from maths.utils import float_or_none


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

        self.setup_radio_plot()
        self.setup_radio_transform()
        self.setup_radio_preproc()
        self.setup_radio_cut_edges()
        self.setup_radio_stats_avg()
        self.setup_radio_stats_paired()
        self.setup_radio_test()

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
        dialog = SelectFileDialog()

        code = dialog.exec()
        if code == QDialog.Accepted:
            self.presenter.set_open_file(dialog.get_file())

    def plot_signal(self, time_series):
        signal_plot = self.plot_top
        signal_plot.plot(time_series)

    def get_window(self) -> QWindow:
        return self

    def main_plot(self) -> WFTPlot:
        return self.plot_main

    def setup_radio_plot(self):
        self.radio_plot_ampl.setChecked(True)

    def setup_radio_transform(self):
        self.radio_transform_wft.setChecked(True)

    def setup_radio_preproc(self):
        self.radio_preproc_on.setChecked(True)

    def setup_radio_cut_edges(self):
        self.radio_cut_on.setChecked(True)

    def setup_radio_stats_avg(self):
        self.radio_stat_median.setChecked(True)

    def setup_radio_stats_paired(self):
        self.radio_unpaired.setChecked(True)

    def setup_radio_test(self):
        self.radio_test_ampl.setChecked(True)

    def get_preprocessing(self):
        return self.radio_preproc_on.isChecked()

    def get_fmin(self) -> float:
        edit = self.line_fmin
        text = edit.text()
        return float_or_none(text)

    def get_fmax(self) -> float:
        text = self.line_fmax.text()
        return float_or_none(text)

    def get_f0(self) -> float:
        text = self.line_res.text()
        return float_or_none(text)

    def get_fstep(self) -> float:
        text = "" # Placeholder.
        return float_or_none(text)

    def get_padding(self) -> str:
        return super().get_padding()

    def get_rel_tolerance(self) -> float:
        return super().get_rel_tolerance()

    def get_cut_edges(self) -> bool:
        return super().get_cut_edges()

    def get_preprocess(self) -> bool:
        return super().get_preprocess()

    def get_transform_window(self) -> str:
        return super().get_transform_window()
