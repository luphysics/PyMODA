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
from PyQt5.QtWidgets import QLineEdit, QPushButton, QListWidget, QGroupBox

from gui.windows.ViewProperties import ViewProperties


class GCViewProperties(ViewProperties):
    def __init__(self):
        self.line_stat_fmin: QLineEdit = None
        self.line_stat_fmax: QLineEdit = None

        self.btn_stat_add: QPushButton = None
        self.btn_stat_del: QPushButton = None

        self.btn_stat_calc: QPushButton = None

        self.list_stat: QListWidget = None
        self.groupbox_stats: QGroupBox = None

        self.line_percentile: QLineEdit = None
        self.line_plot_percentile: QLineEdit = None
