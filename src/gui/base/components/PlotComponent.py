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
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QVBoxLayout, QApplication
from matplotlib import patches
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_qt5agg import (FigureCanvas)
from matplotlib.figure import Figure

from gui.base.components.BaseComponent import BaseComponent
from gui.base.plot.Callbacks import Callbacks
from gui.base.plot.PlotOptionsBar import PlotOptionsBar
from gui.timefrequency.Rect import Rect


class PlotComponent(BaseComponent):
    """A component which enables plotting via matplotlib."""

    callbacks: Callbacks = None
    canvas: FigureCanvas = None
    layout: QVBoxLayout = None
    axes = None

    temp_plots = []  # Temporary crosshair plots which should be removed on each update.
    selected_plots = []  # Selected crosshair plots which should be kept.

    crosshair_width = 0.7
    show_crosshair = True

    temp_patch = None  # The actual rectangle being drawn on the plot.
    rect: Rect = None  # The Rect object representing the coordinates of the rectangle.
    rect_stack: List = []  # A List of Rect objects corresponding to a stack of previous zoom states.

    def __init__(self, parent):
        super(PlotComponent, self).__init__(parent)

    def init_ui(self):
        super().init_ui()

        self.setMouseTracking(True)
        self.layout = QVBoxLayout(self)
        self.canvas = FigureCanvas(Figure())
        self.init_callbacks()

        self.options = PlotOptionsBar(self.callbacks)

        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.options)

        self.axes = self.canvas.figure.subplots()
        self.axes.set_xlabel(self.get_xlabel())
        self.axes.set_ylabel(self.get_ylabel())

        self.fig = self.axes.get_figure()
        background = self.palette().color(QPalette.Background)
        self.fig.patch.set_facecolor(background.name())

    def get_xlabel(self):
        """Returns the label for the x-axis. Should be overridden in subclasses."""
        pass

    def get_ylabel(self):
        """Returns the label for the y-axis. Should be overridden in subclasses."""
        pass

    def init_callbacks(self):
        """
        Creates the callbacks for interacting with the plot.
        """
        move = self.canvas.mpl_connect("motion_notify_event", self.on_move)
        click = self.canvas.mpl_connect("button_press_event", self.on_click)
        release = self.canvas.mpl_connect("button_release_event", self.on_release)

        # We want "leave" to trigger for the axes and the figure, because a fast
        # mouse movement can cause the axes leave event to not occur.
        axes_leave = self.canvas.mpl_connect("axes_leave_event", self.on_leave)
        figure_leave = self.canvas.mpl_connect("figure_leave_event", self.on_leave)

        # Set the callbacks object to hold references to these callbacks.
        self.callbacks = Callbacks(move, click, release,
                                   axes_leave, figure_leave,
                                   self.on_reset, self.on_go_back)

    def on_initial_plot_complete(self):
        """
        Should be called after the first plot is complete. It will then set the initial state
        so that the reset button can work.
        """
        self.add_rect_state(self.current_rect())

    def cross_cursor(self, cross=True):
        """Sets the cursor to a cross, or resets it to the normal arrow style."""
        if cross:
            QApplication.setOverrideCursor(Qt.CrossCursor)
        else:
            QApplication.setOverrideCursor(Qt.ArrowCursor)

    def current_rect(self):
        """Creates a rect corresponding to the current state."""
        x1, x2 = self.xlim()
        y1, y2 = self.ylim()

        rect = Rect(x1, y1)
        rect.set_corner(x2, y2)
        return rect

    def pre_update(self):
        """Should be called before update()."""
        self.remove_temp()

    def update(self):
        """Updates the plot by redrawing the canvas."""
        super().update()
        self.canvas.draw()

    def remove_temp_crosshairs(self):
        """
        Removes the temporary crosshairs (the crosshairs that follow the cursor
        as it moves).
        """
        num = len(self.temp_plots)
        for i in range(num):
            item = self.temp_plots.pop()  # Take last item and remove from list.
            item.remove()  # Remove from plot.

    def remove_temp_rectangle(self):
        """
        Removes the temporary rectangle. This is necessary because the
        rectangle must be updated as the cursor moves, and the old version
        needs to be removed.
        """
        if self.temp_patch:
            self.temp_patch.remove()
            self.temp_patch = None

    def remove_temp(self):
        """Removes all temporary items on the plot."""
        self.remove_temp_crosshairs()
        self.remove_temp_rectangle()

    def on_move(self, event):
        """Called when the mouse moves over the plot."""
        self.cross_cursor(True)
        x, y = self.xy(event)
        if x and y:
            self.pre_update()
            if self.rect:
                self.rect.set_corner(x, y)
                self.draw_rect()

            self.update()

    def on_click(self, event):
        """Called when the mouse clicks down on the plot, but before the click is released."""
        if event.button == MouseButton.LEFT:
            x, y = self.xy(event)
            if x and y:
                self.rect = Rect(x, y)
                self.pre_update()
                self.update()

    def on_release(self, event):
        """Called when the mouse releases a click on the plot."""
        if event.button == MouseButton.LEFT:
            x, y = self.xy(event)
            if x and y:
                if self.rect:
                    self.zoom_to(self.rect)
                    self.rect = None

                if self.show_crosshair:
                    if len(self.selected_plots) >= 2:
                        self.show_crosshair = False

                self.pre_update()
                self.update()

    def zoom_to(self, rect):
        """
        Zooms the plot to the region designated by the rectangle.
        Adds the new state to the stack of states.
        """
        x1, x2 = rect.x1, rect.x2
        y1, y2 = rect.y1, rect.y2
        self.axes.set_xlim(x1, x2)
        self.axes.set_ylim(y1, y2)

        self.add_rect_state(rect)

    def add_rect_state(self, rect: Rect):
        """Adds a rect state to the stack of states."""
        self.rect_stack.append(rect)

    def on_leave(self, event):
        """Called when the mouse is no longer over the figure or the axes."""
        self.cross_cursor(False)
        self.pre_update()
        self.update()

    def on_reset(self):
        """Called when the reset button is pressed."""
        stack = self.rect_stack
        normal = stack[0]
        self.zoom_to(normal)
        self.update()

    def on_go_back(self):
        """Called when the back button is pressed."""
        if len(self.rect_stack) > 1:
            self.rect_stack.pop()  # Remove the current state from the list.
            state = self.rect_stack.pop()  # Get previous state and remove from list.
            self.zoom_to(state)
            self.update()

    def xy(self, event):
        """Returns the xy-coordinates from an event as a tuple."""
        return event.xdata, event.ydata

    def get_bounds(self):  # Not currently in use?
        """Gets the bounds of the plot; i.e. the points corresponding to maximum and minimum x and y."""
        x1, x2 = self.xlim()
        y1, y2 = self.ylim()
        return Bounds(x1, x2, y1, y2)

    def xlim(self):
        return self.axes.get_xlim()

    def ylim(self):
        return self.axes.get_ylim()

    def draw_rect(self):
        """
        Draws the rectangle (used to allow the user to zoom on a region).
        """
        rect = self.rect
        width, height = rect.get_width(), rect.get_height()
        x, y = rect.x1, rect.y1

        self.temp_patch = patches.Rectangle((x, y), width, height, edgecolor="red", fill=False, zorder=10)
        self.axes.add_patch(self.temp_patch)

    def draw_lines(self, x, y):
        """Draws a horizontal and vertical line, intersecting at (x,y)."""
        self.plot_hor(y)
        self.plot_ver(x)

    def plot_ver(self, x):
        """Plots a vertical line at a given x-value, and adds to the list of temporary plots."""
        line = self.ver_line(x)
        self.temp_plots.append(line)

    def ver_line(self, x):
        """Creates a vertical line at a given x-value."""
        return self.axes.axvline(x, color="black", linewidth=self.crosshair_width)

    def plot_hor(self, y):
        """Plots a horizontal line at a given y-value, and adds to the list of temporary plots."""
        line = self.hor_line(y)
        self.temp_plots.append(line)

    def hor_line(self, y):
        """Creates a horizontal line at a given y-value."""
        return self.axes.axhline(y, color="black", linewidth=self.crosshair_width)

    def clear(self):
        """Clears the contents of the plot."""
        self.axes.clear()


class Bounds:
    """
    An object representing the bounds of a plot. It contains the minimum and
    maximum x and y values.
    """

    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
