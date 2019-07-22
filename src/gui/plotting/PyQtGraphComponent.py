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
from PyQt5.QtWidgets import QVBoxLayout
from pyqtgraph.opengl import GLViewWidget

from gui.plotting.PlotComponent import PlotComponent


class PyQtGraphComponent(PlotComponent):
    """A component which enables plotting via PyQtGraph."""

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.plot_widget = GLViewWidget()
        self.layout.addWidget(self.plot_widget)
