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
from PyQt5.QtWidgets import QDialog, QCheckBox

from data import resources
from gui.BaseUI import BaseUI
from utils.settings import Settings


class MatlabRuntimeDialog(QDialog, BaseUI):
    def __init__(self):
        self.dont_show_again = False
        super(MatlabRuntimeDialog, self).__init__()

    def setup_ui(self) -> None:
        uic.loadUi(resources.get("layout:dialog_matlab_runtime.ui"), self)

        checkbox: QCheckBox = self.checkbox_dont_show_again
        checkbox.stateChanged.connect(self.on_check)

    def on_check(self, state: int):
        self.dont_show_again = bool(state)
