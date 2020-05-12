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
from typing import Any, Optional, List

import numpy as np
from numpy import ndarray

"""
File containing useful numerical functions.
"""


def float_or_none(var: Any) -> Optional[float]:
    """
    If the variable can be represented as a float, return the float value.
    Otherwise, return None.

    Note: if a boolean is passed, the function will return None.
    """
    result = None
    try:
        if not isinstance(var, bool):  # We don't want unexpected boolean conversions.
            result = float(var)
    except:
        pass
    return result


def int_or_none(var: Any, round_int=False) -> Optional[int]:
    """
    If the variable can be represented as an int, return the int value.
    Otherwise, return None.

    Note: if a boolean is passed, the function will return None.
    """
    result = None
    try:
        if not isinstance(var, bool):
            if round_int:
                result = np.round(var)
            else:
                result = int(var)
    except:
        pass
    return result


def float_to_str(var: float) -> str:
    """
    Returns a string representation of a float, without trailing zeros.
    """
    try:
        return f"{var:g}"
    except:
        return ""


def isfloat(var: Any) -> bool:
    """
    Returns whether a variable can be represented as a float.
    Returns False for any boolean variable.
    """
    return float_or_none(var) is not None


def subsample2d(arr, target):
    """
    Subsamples 2d arrays of data, using a naive algorithm (take every n-th element without interpolation).

    .. note ::
        Currently, this function only subsamples the array in the x-direction.

    Parameters
    ----------
    arr : ndarray
        [2D array] The array to subsample.
    target : int
        The target width of the array.

    Returns
    -------
    ndarray
        The subsampled array.
    """
    x, y = arr.shape

    factor = int(np.ceil(y / target))
    new_shape = (x, int(np.ceil(y / factor)))
    result = np.empty(shape=new_shape, dtype=arr.dtype)

    result[:, :] = arr[:, ::factor]
    return result


def calc_subset_count(arr):
    """
    Given a 2D array of data, estimates the optimal
    subset count to improve performance while not
    significantly affecting the appearance of the
    results.
    """
    return int(np.ceil(arr.shape[1] / 3840))


def matlab_to_numpy(arr) -> ndarray:
    """
    Converts a matlab array to a numpy array.
    Can be much faster than simply calling "np.asarray()",
    but does not appear to be faster for complex arrays.
    """
    try:
        # Should work for real arrays, maybe not for complex arrays.
        result = np.array(arr._data).reshape(arr.size, order="F")
    except:
        result = np.array(arr)
    return result


def multi_matlab_to_numpy(*args) -> List[ndarray]:
    """
    Converts multiple matlab arrays to numpy arrays using `matlab_to_numpy()`.
    """
    out = []
    for arr in args:
        out.append(matlab_to_numpy(arr))

    return out
