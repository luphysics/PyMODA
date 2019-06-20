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
import time

import numpy as np
from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qt5agg import (FigureCanvas)
from matplotlib.figure import Figure

from gui.base.components.BaseComponent import BaseComponent
from gui.base.components.ResizableComponent import ResizableComponent


class PlotComponent(BaseComponent):
    """A component which enables plotting via matplotlib."""

    canvas = None
    layout = None
    axis = None

    def __init__(self, parent):
        super(PlotComponent, self).__init__(parent)

    def init_ui(self):
        super().init_ui()
        layout = QVBoxLayout(self)
        self.layout = layout

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.canvas)

        self.axis = self.canvas.figure.subplots()

        # _static_ax = self.canvas.figure.subplots()
        # t = np.linspace(0, 10, 501)
        # _static_ax.plot(t, np.tan(t), ".")
