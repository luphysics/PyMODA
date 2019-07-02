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
import scipy
import scipy.integrate


def isempty(value):
    """
    Imitates MATLAB's `isempty` function by returning whether the object
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
    return np.linalg.lstsq(x, y)[0] # TODO: check this


def nextpow2(x):
    return np.ceil(np.log2(abs(x)))


def quadgk(func, x0, x1, limit, epsabs, epsrel):
    if epsrel <= 0:
        epsrel = np.max([50 * eps, 5e-29])
    return scipy.integrate.quad(func, x0, x1, limit=limit, epsabs=epsabs, epsrel=epsrel)


twopi = 2 * np.pi
pi = np.pi
eps = np.finfo(np.float64).eps


def find(arr, condition):
    l = len(arr)
    indices = []
    for i in range(l):
        if condition(arr[i]):
            indices.append(i)

    return indices
