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

from PyQt5 import uic, QtGui
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QDialog, QListWidget

from data import resources
from gui.dialogs.files.SelectFileDialog import SelectFileDialog
from gui.windows.base.MaximisedWindow import MaximisedWindow
from gui.windows.timefrequency.TFPresenter import TFPresenter
from gui.windows.timefrequency.TFView import TFView
from gui.windows.timefrequency.plots.AmplitudePlot import AmplitudePlot
from gui.windows.timefrequency.plots.SignalPlot import SignalPlot
from gui.windows.timefrequency.plots.WFTPlot import WFTPlot
from maths.utils import float_or_none


class TFWindow(MaximisedWindow, TFView):
    """
    The time-frequency base window. This class is the "View" in MVP,
    meaning that it should defer responsibility for tasks to the
    presenter.
    """

    def __init__(self, application):
        TFView.__init__(self, application, TFPresenter(self))
        MaximisedWindow.__init__(self)

    def init_ui(self):
        uic.loadUi(resources.get("layout:window_time_freq.ui"), self)
        self.update_title()
        self.setup_menu_bar()

        # Setup radio buttons.
        self.setup_radio_plot()
        self.setup_radio_transform()
        self.setup_radio_preproc()
        self.setup_radio_cut_edges()
        self.setup_radio_stats_avg()
        self.setup_radio_stats_paired()
        self.setup_radio_test()
        self.setup_signal_listview()
        self.setup_xlim_edits()
        self.setup_combo_wt()

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
        """Plots the signal in the top-left plotting."""
        self.signal_plot().plot(time_series)

    def on_calculate_started(self):
        self.main_plot().set_in_progress(True)
        self.amplitude_plot().clear()
        self.amplitude_plot().set_in_progress(True)
        btn = self.btn_calculate

        btn.setText("Cancel")
        btn.setStyleSheet("color: red;")

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

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        """Called when the window closes. Cancels any calculations that are in progress."""
        self.presenter.cancel_calculate()
        super().closeEvent(e)

    def get_window(self) -> QWindow:
        return self

    def main_plot(self) -> WFTPlot:
        return self.plot_main

    def signal_plot(self) -> SignalPlot:
        return self.plot_top

    def amplitude_plot(self) -> AmplitudePlot:
        return self.plot_right

    def set_xlimits(self, x1, x2):
        """
        Sets the x-limits on the signal plotting, restricting the values to
        a certain range of times.

        :param x1: the lower limit
        :param x2: the upper limit
        """

        # Format to 4 decimal places.
        def format_4dp(x): return f"{x:.4f}"

        self.line_xlim1.setText(format_4dp(x1))
        self.line_xlim2.setText(format_4dp(x2))

    def setup_xlim_edits(self):
        """Sets up the refresh button to trigger x-limit changes."""
        self.btn_refresh.clicked.connect(self.on_xlim_edited)

    def on_xlim_edited(self):
        """Called when the x-limits have been changed."""
        x1 = self.line_xlim1.text()
        x2 = self.line_xlim2.text()
        self.signal_plot().set_xrange(x1=float_or_none(x1), x2=float_or_none(x2))

    def on_transform_toggled(self, is_wft):
        """Called when the type of transform (WT or WFT) is toggled."""
        self.setup_combo_wt(is_wft)

    def setup_combo_wt(self, is_wft=True):
        """
        Sets up the "WT / WFT Type" combobox according to the current transform type.
        :param is_wft: whether the current transform is WFT (not WT)
        """
        combo = self.combo_window
        combo.clear()

        # Gets the list of items from the tuple, since the bool evaluates to 0 or 1.
        items = self._window_items[is_wft]
        for i in items:
            combo.addItem(i)

    def setup_radio_plot(self):
        self.radio_plot_ampl.setChecked(True)
        self.radio_plot_ampl.toggled.connect(self.on_plot_type_toggled)

    def setup_radio_transform(self):
        self.radio_transform_wft.setChecked(True)
        self.radio_transform_wft.toggled.connect(self.on_transform_toggled)

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
        text = ""  # Placeholder.
        return float_or_none(text)

    def get_padding(self) -> str:
        return super().get_padding()

    def get_rel_tolerance(self) -> float:
        return super().get_rel_tolerance()

    def get_cut_edges(self) -> bool:
        return self.radio_cut_on.isChecked()

    def get_preprocess(self) -> bool:
        return self.radio_preproc_on.isChecked()

    def get_wt_wft_type(self) -> str:
        combo = self.combo_window
        return combo.currentText()

    def setup_signal_listview(self):
        self.list_select_data.itemClicked.connect(self.presenter.on_signal_selected)

    def update_signal_listview(self, items):
        list_widget: QListWidget = self.list_select_data
        list_widget.clear()
        list_widget.addItems(items)
        list_widget.setCurrentRow(0)
        self.presenter.on_signal_selected(list_widget.selectedIndexes()[0].data())

    def get_transform_type(self) -> str:
        if self.radio_transform_wft.isChecked():
            transform = "wft"
        else:
            transform = "wt"
        return transform

    def set_log_text(self, text):
        """Sets the text displayed in the log pane, and scrolls to the bottom."""
        if text != "\n":
            self.text_log.setPlainText(text.rstrip())
            self.text_log.moveCursor(QtGui.QTextCursor.End)
