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

from gui import resources
from gui.base.CentredWindow import CentredWindow
from gui.base.SelectFileDialog import SelectFileDialog


class TimeFreqWindow(CentredWindow):

    def __init__(self, application):
        super().__init__()
        self.application = application

    def init_ui(self):
        self.set_title("Time-Frequency Analysis")
        uic.loadUi(resources.get_ui("window_time_freq"), self)
        self.setup_menu_bar()
        self.select_file()

    def setup_menu_bar(self):
        menu = self.menubar
        file = menu.addMenu("File")
        file.addAction("Load data file")

    def select_file(self):
        SelectFileDialog().exec_()
