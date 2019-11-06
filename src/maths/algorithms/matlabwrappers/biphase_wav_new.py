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

"""
Do not import this module in the main process, or it will break Linux support
due to issues with the LD_LIBRARY_PATH.
"""
from typing import Tuple

from numpy import ndarray

from maths.num_utils import matlab_to_numpy


def calculate(
    signal1: ndarray, signal2: ndarray, fs, f0, fr, opt: dict
) -> Tuple[ndarray, ndarray]:
    """
    Calculates the biphase and biamplitude from the bispectrum using the MATLAB-packaged function.
    """
    import biphaseWavPython
    import matlab

    package = biphaseWavPython.initialize()

    result = package.biphaseWavPython(
        matlab.double(signal1),
        matlab.double(signal2),
        fs,
        f0,
        matlab.double(list(fr)),
        opt,
        nargout=2,
    )

    biamp, biphase = result

    biamp = matlab_to_numpy(biamp)
    biphase = matlab_to_numpy(biphase)

    return biamp, biphase


def expand(_dict: dict) -> tuple:
    """
    Expands a dictionary into a MATLAB-friendly list of arguments.
    For example, {"fmin": 5, "f0": 1} expands to ("fmin", 5, "f0", 1).
    """
    _list = []
    for key, value in _dict.items():
        _list.append(key)
        _list.append(value)

    return tuple(_list)
