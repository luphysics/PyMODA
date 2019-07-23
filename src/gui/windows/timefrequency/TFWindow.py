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

from PyQt5 import QtGui
from PyQt5.QtGui import QWindow

from data import resources
from gui.windows.base.analysis.BaseTFWindow import BaseTFWindow
from gui.windows.timefrequency.TFPresenter import TFPresenter
from gui.windows.timefrequency.TFView import TFView
from maths.utils import float_or_none


class TFWindow(BaseTFWindow, TFView):
    """
    The time-frequency window. This class is the "View" in MVP,
    meaning that it should defer responsibility for tasks to the
    presenter.
    """

    def __init__(self, application):
        TFView.__init__(self, application, TFPresenter(self))
        BaseTFWindow.__init__(self)

    def init_ui(self):
        super().init_ui()
        self.setup_radio_plot()
        self.setup_radio_transform()
        self.setup_radio_stats_avg()
        self.setup_radio_stats_paired()
        self.setup_radio_test()
        self.setup_combo_wt()

    def get_layout_file(self) -> str:
        return resources.get("layout:window_time_freq.ui")

    def plot_signal(self, time_series):
        """Plots the signal in the top-left plotting."""
        self.signal_plot().plot(time_series)

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

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        """Called when the window closes. Cancels any calculations that are in progress."""
        self.presenter.on_close()
        super().closeEvent(e)

    def get_window(self) -> QWindow:
        return self

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

    def on_transform_toggled(self, is_wt):
        """Called when the type of transform (WT or WFT) is toggled."""
        self.setup_combo_wt(is_wt)

    def setup_combo_wt(self, is_wt=True):
        """
        Sets up the "WT / WFT Type" combobox according to the current transform type.
        :param is_wt: whether the current transform is WT (not WFT)
        """
        combo = self.combo_window
        combo.clear()

        # Gets the list of items from the tuple, since the bool evaluates to 0 or 1.
        items = self._window_items[is_wt]
        for i in items:
            combo.addItem(i)

    def setup_radio_plot(self):
        self.radio_plot_ampl.setChecked(True)
        self.radio_plot_ampl.toggled.connect(self.on_plot_type_toggled)

    def setup_radio_transform(self):
        self.radio_transform_wt.setChecked(True)
        self.radio_transform_wt.toggled.connect(self.on_transform_toggled)

    def setup_radio_stats_avg(self):
        self.radio_stat_median.setChecked(True)

    def setup_radio_stats_paired(self):
        self.radio_unpaired.setChecked(True)

    def setup_radio_test(self):
        self.radio_test_ampl.setChecked(True)

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

    def get_wt_wft_type(self) -> str:
        combo = self.combo_window
        return combo.currentText()

    def get_transform_type(self) -> str:
        if self.radio_transform_wft.isChecked():
            transform = "wft"
        else:
            transform = "wt"
        return transform
