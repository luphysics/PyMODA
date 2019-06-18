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

import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication

from gui import resources
from gui.base.CentredWindow import CentredWindow
from gui.resources import get_ui


class LauncherWindow(CentredWindow):

    def __init__(self, application):
        super(LauncherWindow, self).__init__()
        self.application = application
        self.init_ui()

    def init_ui(self):
        uic.loadUi(get_ui("launcher"), self)
        self.setWindowTitle(resources.get_name())
        self.btn_time_freq.clicked.connect(self.click)

    def click(self):
        self.application.start_time_frequency()
