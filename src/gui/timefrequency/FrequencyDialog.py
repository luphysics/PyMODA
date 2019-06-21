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
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QComboBox

import args
from data import resources
from gui.base.BaseUI import BaseUI


class FrequencyDialog(QDialog, BaseUI):
    """A dialog which allows the sampling frequency to be entered."""

    select_text = "Select item"
    current_selected = None

    def __init__(self, freq_callback):
        super().__init__()
        self.freq_callback = freq_callback

    def init_ui(self):
        uic.loadUi(resources.get("layout:dialog_frequency.ui"), self)
        self.edit_freq.textChanged.connect(self.freq_changed)
        QTimer.singleShot(1000, self.check_args)

    def setup_combo(self):
        combo: QComboBox = self.combo_recent
        combo.addItem(self.select_text)
        combo.addItem(self.combo_text(10))
        combo.activated.connect(self.on_combo_change)

    def check_args(self):
        freq: float = args.args_freq()
        if freq:
            self.freq_changed(freq)
            self.accept()

    def combo_text(self, freq):
        return f"{freq} Hz"

    def freq_changed(self, value):
        self.freq_callback(value)

    def get_frequency(self):
        combo_value = self.combo_recent.text()

    def on_combo_change(self, value):
        self.current_selected = value
