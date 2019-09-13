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
from typing import Optional

from PyQt5.QtWidgets import QLineEdit, QSlider

from maths.num_utils import float_or_none, int_or_none
from utils.decorators import inty


class SurrogateComponent:

    def __init__(self, slider: QSlider, line_edit: QLineEdit):
        self.slider_surrogate: QSlider = slider
        self.line_surrogate: QLineEdit = line_edit

        self.setup_surr_count()

    @staticmethod
    def calc_slider_maximum(value: int):
        """
        Gets the maximum value to use for the surrogate
        slider, based on the currently selected value.
        """
        return math.ceil(value / 10.0) * 10

    def update_slider_maximum(self, value: int):
        s = self.slider_surrogate

        m = s.maximum()
        new_max = m
        if value >= m or m / value > 5:
            new_max = self.calc_slider_maximum(value)

        s.setMaximum(max(19, new_max))

    def set_slider_value(self, value: int):
        if value > 1:
            self.update_slider_maximum(value)
            self.slider_surrogate.setValue(value)

    def on_count_line_edited(self):
        """Called when the surrogate count is typed manually."""
        c = self.get_surr_count()
        if c is None or c <= 1:
            value = 2
            self.line_surrogate.setText(str(value))
            self.on_count_line_changed(value)

    def setup_surr_count(self):
        """Sets up the "surrogate count" slider."""
        default = 19

        slider = self.slider_surrogate
        slider.setTickInterval(1)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setSingleStep(1)
        slider.valueChanged.connect(self.on_slider_change)
        slider.setRange(2, self.calc_slider_maximum(default))
        slider.setValue(default)

        line = self.line_surrogate
        line.textEdited.connect(self.on_count_line_changed)
        line.returnPressed.connect(self.on_count_line_edited)
        line.editingFinished.connect(self.on_count_line_edited)
        line.setText(f"{default}")

    def on_slider_change(self, value: int):
        l = self.line_surrogate
        l.setText(f"{value}")

    def on_count_line_changed(self, value):
        count = int_or_none(value)
        if count is not None and count > 1:
            self.set_slider_value(count)

    @inty
    def get_surr_count(self) -> Optional[int]:
        return self.line_surrogate.text()
