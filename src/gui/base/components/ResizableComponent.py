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
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from gui.base.components.BaseComponent import BaseComponent


class ResizableComponent(BaseComponent):
    """
    A component which can be resized by dragging
    the sides or corners.

    IMPORTANT: Not fully implemented. Not functioning correctly.
    """

    drag_area_size = 4

    def init_ui(self):
        self.setMouseTracking(True)

    def calc_bounds(self):
        pos = self.pos()
        height = self.height()
        width = self.width()
        self.bounds = Bounds(pos.x(), pos.y(), width, height)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        self.calc_bounds()
        pos = e.pos()
        x, y = pos.x(), pos.y()
        drag_horizontal = self.within_x(x)
        drag_vertical = self.within_y(y)

        if drag_horizontal and drag_vertical:
            self.cursor_drag_diag_f()
        elif drag_vertical:
            self.cursor_drag_ver()
        elif drag_horizontal:
            self.cursor_drag_hor()
        else:
            self.cursor_normal()

    def cursor_normal(self):
        QApplication.restoreOverrideCursor()

    def cursor_drag_diag_b(self):
        QApplication.setOverrideCursor(Qt.SizeBDiagCursor)

    def cursor_drag_diag_f(self):
        QApplication.setOverrideCursor(Qt.SizeFDiagCursor)

    def cursor_drag_hor(self):
        QApplication.setOverrideCursor(Qt.SizeHorCursor)

    def cursor_drag_ver(self):
        QApplication.setOverrideCursor(Qt.SizeVerCursor)

    def within_x(self, x):
        return self.bounds.dist_x(x) <= self.drag_area_size

    def within_y(self, y):
        return self.bounds.dist_y(y) <= self.drag_area_size


class Bounds:

    def __init__(self, x, y, width, height):
        self.top_left = (x, y)
        self.top_right = (x + width, y)
        self.bottom_left = (x, y + height)
        self.bottom_right = (x + width, y + height)

    def dist_x(self, x):
        return min(abs(self.top_left[0] - x),
                   abs(self.top_right[0] - x))

    def dist_y(self, y):
        return min(abs(self.top_left[1] - y),
                   abs(self.bottom_left[1] - y))
