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
DO NOT import this module in the main process, or it will break Linux support
due to issues with the LD_LIBRARY_PATH.
"""
from typing import List

from maths.multiprocessing import mp_utils


# This must be above the matlab imports.
mp_utils.setup_matlab_runtime()

import bispecWavNew
import matlab

package = bispecWavNew.initialize()


def calculate(signal1: List, signal2: List , params):
    """
    Calculates the windowed Fourier transform.

    IMPORTANT: this function should not be called directly due to issues
    with the LD_LIBRARY_PATH on Linux. Instead, use `MPHandler` to call it
    safely in a new process.
    """
    result = package.bispecWavNew(matlab.double(signal1),
                                  matlab.double(signal2),
                                  params.fs,
                                  params.get(),
                                  nargout=5)

    return result
