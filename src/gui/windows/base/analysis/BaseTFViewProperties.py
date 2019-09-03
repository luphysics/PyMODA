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
from PyQt5.QtWidgets import QLineEdit, QListWidget, QMenuBar

from gui.windows.base.ViewProperties import ViewProperties
from gui.windows.base.analysis.plots.PreprocessPlot import PreprocessPlot


class BaseTFViewProperties(ViewProperties):

    def __init__(self):
        # The menu bar at the top of the window.
        self.menubar: QMenuBar = None

        # The plot which shows the preprocessed signal.
        self.plot_preproc: PreprocessPlot = None

        # The QLineEdits for frequencies.
        self.line_fmin: QLineEdit = None
        self.line_fmax: QLineEdit = None
        self.line_res: QLineEdit = None

        # The QListWidget which contains the names of different signals.
        self.list_select_data: QListWidget = None
