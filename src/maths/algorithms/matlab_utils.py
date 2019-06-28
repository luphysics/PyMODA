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
import numpy as np


def isempty(value):
    """
    Copies MATLAB's `isempty` function by returning whether the object
    is empty - if it has a length - or whether it is None.
    """
    if hasattr(value, "__len__"):
        return len(value) == 0
    return value is None


def isnan(value):
    return np.isnan(value)


def isfinite(value):
    return np.isfinite(value)


def backslash(x, y):
    """Imitates the MATLAB backslash operator."""
    return np.linalg.lstsq(x, y)
