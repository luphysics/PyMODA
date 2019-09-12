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
from typing import Callable, Union, Any, Tuple

import numpy as np
from nptyping import Array


def dec_float_or_none(func: Callable[[], str]) -> Callable[[], Union[Tuple[float, ...], float, None]]:
    """
    This decorator will ensure that a function returning one or more
    strings returns its values as floats or None.

    It is useful for functions which return user-entered data from the GUI;
    for example, getting the float version of data in a QLineEdit. The
    function using this decorator needs only return the text in the QLineEdit
    as a string.
    """

    def wrapper(*args):
        if len(args) == 1:
            # If called in a class method.
            result = func(args[0])
        else:
            # If not called in a class method.
            result = func()

        if isinstance(result, tuple) and len(result) > 0:
            # Multiple values returned, convert them all.
            out = tuple(float_or_none(it) for it in result)
        else:
            # Just one value, convert it.
            out = float_or_none(result)

        return out

    return wrapper


def float_or_none(var: Any) -> Union[float, None]:
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


def int_or_none(var: Any, round_int=False) -> Union[int, None]:
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


def isfloat(var: Any) -> bool:
    """
    Returns whether a variable can be represented as a float.
    Returns False for any boolean variable.
    """
    return float_or_none(var) is not None


def subset2d(arr, count):
    shape = arr.shape
    new_shape = (
        np.int(np.ceil(shape[0] / count)),
        np.int(np.ceil(shape[1] / count)),
    )
    result = np.empty(shape=new_shape, dtype=arr.dtype)

    for i in range(new_shape[0]):
        result[i] = arr[i * count][::count]

    return result


def calc_subset_count(arr):
    """
    Given a 2D array of data, estimates the optimal
    subset count to improve performance while not
    significantly affecting the appearance of the
    results.
    """
    return 1  # TODO: add implementation.


def matlab_to_numpy(arr) -> Array:
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
