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

import numpy as np
from numpy import ndarray

from maths.num_utils import multi_matlab_to_numpy
from processes import mp_utils

# This must be above the matlab imports.
mp_utils.setup_matlab_runtime()

import bispecWavPython
import matlab

package = bispecWavPython.initialize()


def calculate(signal1: ndarray, signal2: ndarray, fs, params: dict) -> Tuple[ndarray, ndarray, ndarray, ndarray, dict]:
    """
    Calculates the bispectrum of 2 signals.

    IMPORTANT: this function should not be called directly due to issues
    with the LD_LIBRARY_PATH on Linux. Instead, use `MPHandler` to call it
    safely in a new process.
    """

    result = package.bispecWavPython(matlab.double(signal1),
                                     matlab.double(signal2),
                                     fs,
                                     *expand(params),
                                     nargout=5)

    bisp, freq, wt1, wt2, opt = result
    bisp, freq, wt1, wt2 = multi_matlab_to_numpy(bisp, freq, wt1, wt2)

    opt["PadLR1"], opt["PadLR2"], opt["twf1"], opt["twf2"] = [n.tolist()[0] for n in multi_matlab_to_numpy(opt["PadLR1"],
                                                                                   opt["PadLR2"],
                                                                                   opt["twf1"],
                                                                                   opt["twf2"])]

    output = (np.abs(bisp), freq, np.abs(wt1), np.abs(wt2), opt)
    return output


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
