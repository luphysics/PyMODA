#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2020 Lancaster University
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
from PyQt5.QtWidgets import QComboBox, QLineEdit

from gui.windows.ViewProperties import ViewProperties


class DHViewProperties(ViewProperties):
    def __init__(self):
        self.combo_plot_type: QComboBox = None

        self.line_sigma: QLineEdit = None
        self.line_res: QLineEdit = None
        self.line_fmax: QLineEdit = None
        self.line_fmin: QLineEdit = None
