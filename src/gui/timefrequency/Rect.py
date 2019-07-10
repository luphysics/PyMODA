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


class Rect:
    """
    A simple class representing the coordinates of a rectangle
    that is drawn in matplotlib. (x1,y1) refer to the upper left
    corner, while (x2,y2) are the lower right corner.
    """

    def __init__(self, x1, y1, x2=None, y2=None):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def set_corner(self, x2, y2):
        self.x2 = x2
        self.y2 = y2

    def sorted(self):
        if not self.is_valid():
            return self

        x1 = self.x1
        x2 = self.x2
        y1 = self.y1
        y2 = self.y2

        if x2 < x1:
            x1, x2 = x2, x1  # Swap values.

        if y2 < y1:
            y1, y2 = y2, y1  # Swap values.

        return Rect(x1, y1, x2, y2)

    def get_width(self):
        return self.x2 - self.x1

    def get_height(self):
        return self.y2 - self.y1

    def is_valid(self):
        return self.x2 is not None and self.y2 is not None

    def __str__(self) -> str:
        return f"{self.x1}, {self.y1}; {self.x2}, {self.y2}"
