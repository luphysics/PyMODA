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
from processes import mp_utils

# This must be above the matlab imports.
mp_utils.setup_matlab_runtime()

import biphaseWavPython
import matlab

package = biphaseWavPython.initialize()


def calculate(signal1: ndarray, signal2: ndarray, fs, fr, params: dict) -> Tuple[ndarray, ndarray]:
    """
    Calculates the biphase and biamplitude from the bispectrum.

    IMPORTANT: this function should not be called directly due to issues
    with the LD_LIBRARY_PATH on Linux. Instead, use `MPHandler` to call it
    safely in a new process.
    """
    params["PadLR1"] = matlab.double(params["PadLR1"])
    params["PadLR2"] = matlab.double(params["PadLR2"])

    twf1 = [complex(i) for i in params["twf1"][0]]
    twf2 = [complex(i) for i in params["twf2"][0]]

    twf1r = [i.real for i in twf1]
    twf2r = [i.real for i in twf2]
    twf1i = [i.imag for i in twf1]
    twf2i = [i.imag for i in twf2]

    del params["twf1"]
    del params["twf2"]

    params["twf1r"] = matlab.double(twf1r)
    params["twf2r"] = matlab.double(twf2r)
    params["twf1i"] = matlab.double(twf1i)
    params["twf2i"] = matlab.double(twf2i)

    result = package.biphaseWavPython(matlab.double(signal1),
                                      matlab.double(signal2),
                                      fs,
                                      fr,
                                      params,
                                      nargout=2)

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
