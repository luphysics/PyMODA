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
import asyncio
from functools import partial
from typing import List

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QProgressBar, QPushButton

from gui.windows.common.BaseTFViewProperties import BaseTFViewProperties
from gui.dialogs.files.SelectFileDialog import SelectFileDialog
from gui.windows.MaximisedWindow import MaximisedWindow
from gui.plotting.plots.AmplitudePlot import AmplitudePlot
from gui.plotting.plots.ColorMeshPlot import ColorMeshPlot
from gui.plotting.plots.SignalPlot import SignalPlot
from maths.num_utils import float_or_none
from utils.decorators import deprecated


class BaseTFWindow(BaseTFViewProperties, MaximisedWindow):
    """
    A base common window that handles UI-related code. Generally, the window should
    not make decisions on its own; it should rely on the presenter to react to major
    events such as a calculation being requested.

    However, the window should handle setting up its widgets and performing tasks which are
    only directly related to the window.
    """

    # The title of the window.
    name = ""

    def __init__(self, application, presenter):
        self.application = application
        self.presenter = presenter

        BaseTFViewProperties.__init__(self)
        MaximisedWindow.__init__(self, application)

    def get_layout_file(self) -> str:
        pass

    def update_title(self, title=""):
        super().update_title(title or self.presenter.get_window_name())

    def select_file(self):
        asyncio.ensure_future(self.coro_select_file())

    async def coro_select_file(self):
        """
        Prompts the user to select a file by opening a dialog. Suspends until
        the user has closed the dialog. If the user does not select a file,
        the window is unaffected.
        """
        # Sleep to prevent disconcerting mix of animations caused by the dialog opening
        # immediately after the window.
        await asyncio.sleep(0.1)

        file_path = SelectFileDialog().get_result()
        if file_path:
            self.presenter.on_file_selected(file_path)

    def plot_preprocessed_signal(self, times, signal, preproc_signal):
        """
        Does nothing by default. Will be overridden by the PreprocessComponent for
        windows which need it.
        """
        pass

    def setup_menu_bar(self):
        """
        Sets up the toolbar at the top of the window.
        """
        menu = self.menubar
        file = menu.addMenu("File")
        file.addAction("Load data file")
        file.triggered.connect(self.select_file)

    def setup_ui(self):
        uic.loadUi(self.get_layout_file(), self)
        self.update_title()
        self.setup_menu_bar()

        # Setup radio buttons and other UI elements.
        self.setup_radio_preproc()
        self.setup_signal_listview()
        self.setup_xlim_edits()
        self.setup_progress()

        self.setup_lineedit_fmax()
        self.setup_lineedit_fmin()
        self.setup_lineedit_res()

        self.btn_calculate_all.clicked.connect(partial(self.presenter.calculate, True))
        self.btn_calculate_single.clicked.connect(
            partial(self.presenter.calculate, False)
        )

    def on_plot_type_toggled(self, ampl_selected):
        """
        Called when the plot type is changed from amplitude to power, or vice versa.

        :param ampl_selected: whether the plotting type is amplitude, not power
        """
        self.presenter.set_plot_type(ampl_selected)

    @staticmethod
    def progress_message(current=0, total=0):
        """Gets the text to display under the progress bar."""
        if current < total:
            return f"Completed task {current} of {total}."
        return "No tasks in progress."

    def setup_lineedit_fmin(self):
        self.line_fmin.editingFinished.connect(self.on_freq_or_res_edited)

    def setup_lineedit_fmax(self):
        self.line_fmax.editingFinished.connect(self.on_freq_or_res_edited)

    def setup_lineedit_res(self):
        self.line_res.editingFinished.connect(self.on_freq_or_res_edited)

    def on_freq_or_res_edited(self):
        self.presenter.plot_preprocessed_signal()

    def main_plot(self) -> ColorMeshPlot:
        return self.plot_main

    def signal_plot(self) -> SignalPlot:
        return self.plot_top

    def amplitude_plot(self) -> AmplitudePlot:
        return self.plot_right

    def setup_radio_preproc(self):
        self.radio_preproc_on.setChecked(True)

    def get_preprocessing(self):
        return self.radio_preproc_on.isChecked()

    def update_signal_listview(self, items: List[str]):
        list_widget = self.list_select_data
        list_widget.clear()
        list_widget.addItems(items)
        list_widget.setCurrentRow(0)
        self.presenter.on_signal_selected(list_widget.selectedIndexes()[0].data())

    def setup_signal_listview(self):
        self.list_select_data.itemClicked.connect(self.presenter.on_signal_selected)

    def set_log_text(self, text: str):
        """Sets the text displayed in the log pane, and scrolls to the bottom."""
        if text != "\n":
            self.text_log.setPlainText(text.rstrip())
            self.text_log.moveCursor(QtGui.QTextCursor.End)

    def get_cut_edges(self) -> bool:
        return self.radio_cut_on.isChecked()

    def get_preprocess(self) -> bool:
        return self.radio_preproc_on.isChecked()

    def on_calculate_started(self):
        """
        Called when a calculation starts. Enables progress bars
        and sets up cancel button.
        """
        self.main_plot().set_in_progress(True)
        btn = self.btn_calculate_all

        btn.setText("Cancel")
        btn.setStyleSheet("color: blue;")

        self.btn_calculate_single.hide()

        btn.clicked.disconnect()
        btn.clicked.connect(self.presenter.cancel_calculate)

    def on_calculate_stopped(self):
        """
        Called when a calculation stops. Disables progress bars
        and resets cancel button.
        """
        self.main_plot().set_in_progress(False)
        btn = self.btn_calculate_all

        btn.setText("Transform All")
        btn.setStyleSheet("color: black;")
        self.btn_calculate_single.show()

        btn.clicked.disconnect()
        btn.clicked.connect(partial(self.presenter.calculate, True))

        self.setup_progress()

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

    @deprecated
    def get_button_calculate_all(self) -> QPushButton:
        return self.btn_calculate_all

    @deprecated
    def get_button_calculate_single(self) -> QPushButton:
        return self.btn_calculate_single

    def on_xlim_edited(self):
        """Called when the x-limits have been changed."""
        x1 = self.line_xlim1.text()
        x2 = self.line_xlim2.text()
        self.signal_plot().set_xrange(x1=float_or_none(x1), x2=float_or_none(x2))

    def setup_xlim_edits(self):
        """Sets up the refresh button to trigger x-limit changes."""
        self.btn_refresh.clicked.connect(self.on_xlim_edited)

    def set_xlimits(self, x1, x2):
        """
        Sets the x-limits on the signal plotting, restricting the values to
        a certain range of times.

        :param x1: the lower limit
        :param x2: the upper limit
        """

        # Format to 4 decimal places.
        def format_4dp(x):
            return f"{x:.4f}"

        self.line_xlim1.setText(format_4dp(x1))
        self.line_xlim2.setText(format_4dp(x2))
