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
import math
from PyQt5 import QtGui
from PyQt5.QtWidgets import QSlider, QComboBox

from data import resources
from gui import Application
from gui.windows.base.analysis.BaseTFWindow import BaseTFWindow
from gui.windows.phasecoherence.PCPresenter import PCPresenter
from gui.windows.phasecoherence.PCView import PCView
from maths.utils import int_or_none


class PCWindow(BaseTFWindow, PCView):
    """
    The phase coherence window.
    """

    def __init__(self, application: Application):
        PCView.__init__(self, application, PCPresenter(self))
        BaseTFWindow.__init__(self, application)

    def init_ui(self):
        super().init_ui()
        self.setup_surr_count()
        self.setup_surr_method()
        self.setup_surr_type()
        self.setup_analysis_type()

        amp = self.amplitude_plot()
        amp.set_xlabel("Overall Coherence")

    def plot_signal_pair(self, pair):
        plot = self.signal_plot()
        plot.plot(pair[0], clear=True)
        plot.plot(pair[1], clear=False)

    def get_layout_file(self) -> str:
        return resources.get("layout:window_phase_coherence.ui")

    def get_window(self):
        super().get_window()

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        super().closeEvent(e)
        self.presenter.on_close()

    def setup_surr_method(self):
        combo = self.combo_method
        combo.clear()

        items = self._surrogate_types
        for i in items:
            combo.addItem(i)

    def get_slider_count(self):
        return self.slider_surrogate

    def get_line_count(self):
        return self.line_surrogate

    def set_slider_value(self, value: int):
        if value > 1:
            self.update_slider_maximum(value)
            self.get_slider_count().setValue(value)

    def update_slider_maximum(self, value: int):
        s = self.get_slider_count()

        m = s.maximum()
        new_max = m
        if value >= m or m / value > 5:
            new_max = self.slider_maximum(value)

        s.setMaximum(max(19, new_max))

    @staticmethod
    def slider_maximum(value: int):
        """
        Gets the maximum value to use for the surrogate
        slider, based on the currently selected value.
        """
        return math.ceil(value / 10.0) * 10

    def setup_surr_count(self):
        """Sets up the "surrogate count" slider."""
        default = 19

        slider = self.get_slider_count()
        slider.setTickInterval(1)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setSingleStep(1)
        slider.valueChanged.connect(self.on_slider_change)
        slider.setRange(2, self.slider_maximum(default))
        slider.setValue(default)

        line = self.get_line_count()
        line.textEdited.connect(self.on_count_line_changed)
        line.returnPressed.connect(self.on_count_line_edited)
        line.editingFinished.connect(self.on_count_line_edited)
        line.setText(f"{default}")

    def on_count_line_edited(self):
        """Called when the surrogate count is typed manually."""
        c = self.get_surr_count()
        if c is None or c <= 1:
            value = 2
            self.get_line_count().setText(str(value))
            self.on_count_line_changed(value)

    def on_slider_change(self, value: int):
        l = self.get_line_count()
        l.setText(f"{value}")

    def setup_surr_type(self):
        combo = self.combo_wavelet_type
        combo.clear()

        items = self._wavelet_types
        for i in items:
            combo.addItem(i)

    def setup_analysis_type(self):
        self.radio_analysis_max.setChecked(True)

    def get_wt_wft_type(self):
        return self.combo_wavelet_type.currentText()

    def get_analysis_type(self) -> str:
        return super().get_analysis_type()

    def get_surr_count(self) -> int:
        return int_or_none(self.get_line_count().text())

    def get_surr_method(self) -> str:
        combo: QComboBox = self.combo_method
        return combo.currentText()

    def get_surr_enabled(self) -> bool:
        return self.checkbox_surr.isChecked()
