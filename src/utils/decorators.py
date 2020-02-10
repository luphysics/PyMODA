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

from maths.num_utils import float_or_none, int_or_none


def floaty(func):
    """
    This decorator will ensure that a function returning one or more
    strings returns its values as floats or None.

    It is useful for functions which return user-entered data from the GUI;
    for example, getting the float version of text in a QLineEdit. The
    function using this decorator needs only return the text in the QLineEdit
    as a string.
    """

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, tuple) and len(result) > 0:
            # Multiple values returned, convert them all.
            out = tuple(float_or_none(it) for it in result)
        else:
            # Just one value, convert it.
            out = float_or_none(result)
        return out

    return wrapper


def inty(func):
    """
    This decorator will ensure that a function returning one or more
    strings returns its values as ints or None.

    It is useful for functions which return user-entered data from the GUI;
    for example, getting the int version of text in a QLineEdit. The
    function using this decorator needs only return the text in the QLineEdit
    as a string.
    """

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, tuple) and len(result) > 0:
            # Multiple values returned, convert them all.
            out = tuple(int_or_none(it) for it in result)
        else:
            # Just one value, convert it.
            out = int_or_none(result)
        return out

    return wrapper


def deprecated(func):
    """
    Decorator that marks a function as deprecated, i.e. that it should no
    longer be used and will be removed in future.
    """

    def wrapper(*args, **kwargs):
        print(f"Warning: calling deprecated function '{func.__name__}'.")
        return func(*args, **kwargs)

    return wrapper


def override(func):
    """
    Decorator that marks a function as overriding a function from a parent class.

    Like in Java, this serves no real purpose other than to make the intention clearer to developers.
    """

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
