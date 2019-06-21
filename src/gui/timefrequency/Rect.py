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

    x2, y2 = None, None

    def __init__(self, x1, y1):
        self.x1 = x1
        self.y1 = y1

    def set_corner(self, x2, y2):
        self.x2 = x2
        self.y2 = y2

    def get_width(self):
        return self.x2 - self.x1

    def get_height(self):
        return self.y2 - self.y1
