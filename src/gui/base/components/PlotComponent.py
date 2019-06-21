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

from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qt5agg import (FigureCanvas)
from matplotlib.figure import Figure

from gui.base.components.BaseComponent import BaseComponent
from gui.base.plot.Callbacks import Callbacks


class PlotComponent(BaseComponent):
    """A component which enables plotting via matplotlib."""

    canvas = None
    layout = None
    axis = None
    callbacks: Callbacks = None
    temp_plots = []
    selected_plots = []
    crosshair_width = 0.7
    show_crosshair = True

    def __init__(self, parent):
        super(PlotComponent, self).__init__(parent)

    def init_ui(self):
        super().init_ui()
        self.setMouseTracking(True)
        layout = QVBoxLayout(self)
        self.layout = layout

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.canvas)

        self.axis = self.canvas.figure.subplots()
        self.init_callbacks()

    def init_callbacks(self):
        move = self.canvas.mpl_connect("motion_notify_event", self.on_move)
        click = self.canvas.mpl_connect("button_press_event", self.on_click)
        release = self.canvas.mpl_connect("button_release_event", self.on_release)
        leave = self.canvas.mpl_connect("axes_leave_event", self.on_leave)
        self.callbacks = Callbacks(move, click, release, leave)

    def on_move(self, event):
        x, y = self.xy(event)
        if x and y:
            self.pre_update()
            self.draw_lines(x, y)
            self.update()

    def pre_update(self):
        self.remove_temp()

    def update(self):
        self.canvas.draw()

    def remove_temp(self):
        num = len(self.temp_plots)
        for i in range(num):
            # Iterate in reverse order, because the list becomes shorter
            # with every pop.
            index = num - i - 1

            item = self.temp_plots.pop(index)
            item.remove()

    def on_click(self, event):
        x, y = self.xy(event)
        if x and y:
            self.pre_update()
            self.selected_plots.append(self.ver_line(x))
            self.selected_plots.append(self.hor_line(y))
            self.update()

    def on_release(self, event):
        x, y = self.xy(event)
        if x and y and self.show_crosshair:
            self.pre_update()
            self.selected_plots.append(self.ver_line(x))
            self.selected_plots.append(self.hor_line(y))
            self.update()
            if len(self.selected_plots) >= 2:
                self.show_crosshair = False

    def on_leave(self, event):
        self.pre_update()
        self.update()

    def xy(self, event):
        return event.xdata, event.ydata

    def get_bounds(self):
        ax = self.axis
        x1, x2 = ax.get_xlim()
        y1, y2 = ax.get_ylim()
        return Bounds(x1, x2, y1, y2)

    def draw_lines(self, x, y):
        """Draws a horizontal and vertical line, intersecting at (x,y)."""
        self.plot_hor(y)
        self.plot_ver(x)

    def plot_ver(self, x):
        line = self.ver_line(x)
        self.temp_plots.append(line)

    def ver_line(self, x):
        return self.axis.axvline(x, color="black", linewidth=self.crosshair_width)

    def plot_hor(self, y):
        line = self.hor_line(y)
        self.temp_plots.append(line)

    def hor_line(self, y):
        return self.axis.axhline(y, color="black", linewidth=self.crosshair_width)

    def clear(self):
        """Clears the contents of the plot."""
        self.axis.clear()


class Bounds:

    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
