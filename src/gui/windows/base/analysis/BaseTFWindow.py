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
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QDialog, QListWidget, QProgressBar

from gui.dialogs.files.SelectFileDialog import SelectFileDialog
from gui.windows.base.MaximisedWindow import MaximisedWindow
from gui.windows.base.analysis.BaseTFView import BaseTFView
from gui.windows.base.analysis.plots.AmplitudePlot import AmplitudePlot
from gui.windows.base.analysis.plots.SignalPlot import SignalPlot
from gui.windows.base.analysis.plots.WFTPlot import WFTPlot


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
        self.setup_progress()

        self.btn_calculate.clicked.connect(self.presenter.calculate)
        self.presenter.init()

    def main_plot(self) -> WFTPlot:
        return self.plot_main

    def signal_plot(self) -> SignalPlot:
        return self.plot_top

    def amplitude_plot(self) -> AmplitudePlot:
        return self.plot_right

    def setup_radio_preproc(self):
        self.radio_preproc_on.setChecked(True)

    def setup_radio_cut_edges(self):
        self.radio_cut_on.setChecked(True)

    def get_preprocessing(self):
        return self.radio_preproc_on.isChecked()

    def update_signal_listview(self, items):
        list_widget: QListWidget = self.list_select_data
        list_widget.clear()
        list_widget.addItems(items)
        list_widget.setCurrentRow(0)
        self.presenter.on_signal_selected(list_widget.selectedIndexes()[0].data())

    def setup_signal_listview(self):
        self.list_select_data.itemClicked.connect(self.presenter.on_signal_selected)

    def set_log_text(self, text):
        """Sets the text displayed in the log pane, and scrolls to the bottom."""
        if text != "\n":
            self.text_log.setPlainText(text.rstrip())
            self.text_log.moveCursor(QtGui.QTextCursor.End)

    def get_cut_edges(self) -> bool:
        return self.radio_cut_on.isChecked()

    def get_preprocess(self) -> bool:
        return self.radio_preproc_on.isChecked()

    def on_calculate_started(self):
        self.main_plot().set_in_progress(True)
        self.amplitude_plot().clear()
        self.amplitude_plot().set_in_progress(True)
        btn = self.btn_calculate

        btn.setText("Cancel")
        btn.setStyleSheet("color: blue;")

        btn.clicked.disconnect()
        btn.clicked.connect(self.presenter.cancel_calculate)

    def on_calculate_stopped(self):
        self.main_plot().set_in_progress(False)
        self.amplitude_plot().set_in_progress(False)
        btn = self.btn_calculate

        btn.setText("Calculate")
        btn.setStyleSheet("color: black;")

        btn.clicked.disconnect()
        btn.clicked.connect(self.presenter.calculate)

    def setup_progress(self):
        self.update_progress(0, 0)

    def update_progress(self, current, total):
        lbl = self.lbl_progress
        progress: QProgressBar = self.progress

        if current >= total:
            progress.hide()
        else:
            progress.show()
            progress.setValue(current / total * 100)

        lbl.setText(self.progress_message(current, total))
