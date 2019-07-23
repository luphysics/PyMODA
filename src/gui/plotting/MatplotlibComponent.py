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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QVBoxLayout, QApplication
from matplotlib import patches
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_qt5agg import (FigureCanvas)
from matplotlib.figure import Figure

from gui.plotting.PlotComponent import PlotComponent
from gui.plotting.Callbacks import Callbacks
from gui.plotting.PlotOptionsBar import PlotOptionsBar
from gui.windows.base.analysis.plots.Rect import Rect


class MatplotlibComponent(PlotComponent):
    """A component which enables plotting via matplotlib."""

    def __init__(self, parent):
        self.callbacks: Callbacks = None
        self.canvas: FigureCanvas = None
        self.layout: QVBoxLayout = None
        self.axes = None
        self.log = False  # Whether the axes should be logarithmic.

        self.temp_plots = []  # Temporary crosshair plots which should be removed on each update.
        self.selected_plots = []  # Selected crosshair plots which should be kept.
        self.crosshair_width = 0.7
        self.show_crosshair = True

        self.temp_patch = None  # The actual rectangle being drawn on the plotting.
        self.rect: Rect = None  # The Rect object representing the coordinates of the rectangle.
        self.rect_stack = []  # A List of Rect objects corresponding to a stack of previous zoom states.

        self.zoom_listeners = []  # A list of listeners which are notified of zoom events.
        super(MatplotlibComponent, self).__init__(parent)

    def init_ui(self):
        super().init_ui()

        self.canvas = FigureCanvas(Figure())
        self.init_callbacks()
        self.options = PlotOptionsBar(self.callbacks)

        self.setMouseTracking(True)
        self.layout = QVBoxLayout(self)
        self.set_in_progress(False)

        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.options)

        self.axes = self.canvas.figure.subplots()
        self.axes.set_xlabel(self.get_xlabel())
        self.axes.set_ylabel(self.get_ylabel())

        self.fig = self.axes.get_figure()
        background = self.palette().color(QPalette.Background)
        self.fig.patch.set_facecolor(background.name())

    def init_callbacks(self):
        """
        Creates the callbacks for interacting with the plotting.
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

    def on_plot_complete(self):
        """
        Should be called after the first plotting is complete. It will then set the initial state
        so that the reset button can work.
        """
        self.clear_rect_states()
        self.add_rect_state(self.current_rect())
        self.options.set_in_progress(False)
        self.canvas.draw()

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
        """Updates the plotting by redrawing the canvas."""
        super().update()
        self.canvas.draw()

    def set_log_scale(self, logarithmic=False):
        """
        Set whether the plotting should use a logarithmic y-scale.
        IMPORTANT: Note that the `apply_scale()` function must be called (usually in a subclass)
        for this function to have any effect.
        """
        self.log = logarithmic

    def apply_scale(self):
        """
        Applies the scale (either logarithmic or linear) according to `self.log`.
        """
        self.axes.set_yscale("log" if self.log else "linear")

    def remove_temp_crosshairs(self):
        """
        Removes the temporary crosshairs (the crosshairs that follow the cursor
        as it moves).
        """
        num = len(self.temp_plots)
        for i in range(num):
            item = self.temp_plots.pop()  # Take last item and remove from list.
            item.remove()  # Remove from plotting.

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
        """Removes all temporary items on the plotting."""
        self.remove_temp_crosshairs()
        self.remove_temp_rectangle()

    def on_move(self, event):
        """Called when the mouse moves over the plotting."""
        self.cross_cursor(True)
        x, y = self.xy(event)
        if x and y:
            self.pre_update()
            if self.rect:
                self.rect.set_corner(x, y)
                self.draw_rect()

            self.update()

    def on_click(self, event):
        """Called when the mouse clicks down on the plotting, but before the click is released."""
        if event.button == MouseButton.LEFT:
            x, y = self.xy(event)
            if x and y:
                self.rect = Rect(x, y)
                self.pre_update()
                self.update()

    def on_release(self, event):
        """Called when the mouse releases a click on the plotting."""
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

    def zoom_to(self, rect, save_state=True, trigger_listeners=True):
        """
        Zooms the plotting to the region designated by the rectangle.
        Adds the new state to the stack of states.
        """
        rect = rect.sorted()
        if save_state:
            self.add_rect_state(rect)

        self.axes.set_xlim(rect.x1, rect.x2)
        self.axes.set_ylim(rect.y1, rect.y2)
        self.update()

        if trigger_listeners:
            for l in self.zoom_listeners:
                l(rect)

    def set_xrange(self, x1=None, x2=None, **kwargs):
        """Set the range of x-values shown by the plotting."""
        rect = self.current_rect()
        if x1 is not None:
            rect.x1 = x1
        if x2 is not None:
            rect.x2 = x2
        self.zoom_to(rect, **kwargs)

    def add_zoom_listener(self, func):
        self.zoom_listeners.append(func)

    def remove_zoom_listener(self, func):
        self.zoom_listeners.remove(func)

    def clear_rect_states(self):
        self.rect_stack.clear()

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
        normal = self.rect_stack[0]
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
        """Clears the contents of the plotting."""
        self.axes.clear()
        self.canvas.draw()

    def set_in_progress(self, in_progress=True):
        """Sets the progress bar to display whether the plotting is in progress."""
        self.options.set_in_progress(in_progress)
