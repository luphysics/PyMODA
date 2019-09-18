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
import collections

import numpy as np
import scipy
import scipy.integrate
import scipy.interpolate
import scipy.optimize

"""
Contains Python replicas of oft-used Matlab functions.
"""


def isempty(value):
    """
    Imitates MATLAB's `isempty` function by returning whether the object
    is empty - if it has a length - or whether it is None.
    """
    if not is_arraylike(value):
        return value is None

    if isinstance(value, np.ndarray):
        return value.size == 0

    return len(value) == 0


def is_arraylike(value):
    return hasattr(value, "__len__")


def backslash(x, y):
    """Imitates the MATLAB backslash operator."""
    return np.linalg.lstsq(x, y, rcond=None)[0]  # TODO: check this


def nextpow2(x):
    return np.ceil(np.log2(abs(x)))


def quadgk(func, x0, x1, limit, epsabs, epsrel):
    if epsrel <= 0:
        epsrel = np.max([50 * eps, 5e-29])
    return scipy.integrate.quad(func, x0, x1, limit=limit, epsabs=epsabs, epsrel=epsrel)


def interp1(x, y, xq):
    # TODO: check this is consistent with Matlab
    scipy.interpolate.interp1d(x, y, kind="slinear", fill_value="extrapolate")


def sqrt(n): return np.sqrt(n)


def farr(arr): return np.asarray(arr, dtype=np.float64)


def carr(arr): return np.asarray(arr, dtype=np.complex64)


def fminsearch(func, x0, xtol):
    return scipy.optimize.fmin(func=func, x0=x0, xtol=xtol)


# Function aliases.
isfinite = np.isfinite
isnan = np.isnan
rand = np.random.rand
exp = np.exp
log = np.log
min = np.min
max = np.max
argmax = np.argmax
argmin = np.argmin
concat = np.concatenate

fft = np.fft.fft
ifft = np.fft.ifft

nonzero = np.nonzero
asarray = np.asarray
cumsum = np.cumsum
vstack = np.vstack
hstack = np.hstack

matmul = np.matmul

conj = np.conj
abs = np.abs
mean = np.mean
sum = np.sum
ceil = np.ceil
arange = np.arange
length = len
zeros = np.zeros
ifft = np.fft.ifft
atan = np.arctan
sin = np.sin
cos = np.cos

# Variable and constant aliases.
twopi = 2 * np.pi
pi = np.pi
eps = np.finfo(np.float64).eps
inf = np.inf
Inf = inf
NAN = np.NaN
linspace = np.linspace


def find(arr, condition):
    l = len(arr)
    indices = []
    for i in range(l):
        if condition(arr[i]):
            indices.append(i)

    return indices
