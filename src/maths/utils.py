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


def float_or_none(var):
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


def isfloat(var):
    """
    Returns whether a variable can be represented as a float.
    Returns False for any boolean variable.
    """
    return float_or_none(var) is not None
