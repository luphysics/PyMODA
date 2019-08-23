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
from PyQt5.QtWidgets import QPushButton, QLineEdit

from gui.windows.base.ViewProperties import ViewProperties
from gui.windows.ridgeextraction.REPlot import REPlot


class REViewProperties(ViewProperties):

    def __init__(self):
        # The top and bottom REPlots.
        self.re_top: REPlot = None
        self.re_bottom: REPlot = None

        self.btn_add_region: QPushButton = None

        self.line_freq1: QLineEdit = None
        self.line_freq2: QLineEdit = None
