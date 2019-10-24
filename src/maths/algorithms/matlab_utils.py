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
import scipy.interpolate
import scipy.optimize

from utils.decorators import deprecated

"""
Contains useful Python replicas of oft-used Matlab functions. 
Import with wildcard to make all available.
"""


def sort2d(arr, descend=False):
    for i in range(arr.shape[1]):
        arr[:, i] = sorted(arr[:, i], reverse=descend)

    return arr


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
    f = scipy.interpolate.interp1d(x, y, kind="slinear", fill_value="extrapolate")
    return f(xq)


def sqrt(n):
    return np.sqrt(n)


def farr(arr):
    return np.asarray(arr, dtype=np.float64)


def carr(arr):
    return np.asarray(arr, dtype=np.complex64)


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

nanmin = np.nanmin
nanmax = np.nanmax

argmax = np.argmax
argmin = np.argmin
concat = np.concatenate

fft = np.fft.fft
ifft = np.fft.ifft
linspace = np.linspace

nonzero = np.nonzero
asarray = np.asarray
cumsum = np.cumsum
vstack = np.vstack
hstack = np.hstack

matmul = np.matmul  # Note: just use the '@' operator instead.

conj = np.conj
abs = np.abs
mean = np.mean
sum = np.sum
ceil = np.ceil
arange = np.arange
length = len
zeros = np.zeros
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


@deprecated
def find(arr, condition):
    """
    This shouldn't be used. numpy has built-in syntax for find:
    >>> x = np.arange(0, 20)
    >>> indices = (x < 5).nonzero() # Gets indices of elements less than 5.
    >>> indices = np.nonzero(x < 5) # Equivalent to the above.

    >>> # Gets indices of elements which are less than 5 and more than 1.
    >>> indices = np.nonzero((x < 5) & (x > 1)) # The inner brackets are important!

    >>> # Gets indices of elements which are less than 5 or more than 1.
    >>> indices = np.nonzero((x < 5) | (x > 1)) # The inner brackets are important!
    """
    l = len(arr)
    indices = []
    for i in range(l):
        if condition(arr[i]):
            indices.append(i)

    return indices
