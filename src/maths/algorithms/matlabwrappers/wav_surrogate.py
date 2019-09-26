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

from processes import mp_utils

# This must be above the matlab imports.
mp_utils.setup_matlab_runtime()

import wavsurrogate
import matlab
from numpy import ndarray

package = wavsurrogate.initialize()


def calculate(signal: ndarray, type: str, adj: int) -> ndarray:
    """
    Calculates the windowed Fourier transform.

    IMPORTANT: this function should not be called directly due to issues
    with the LD_LIBRARY_PATH on Linux. Instead, use `MPHandler` to call it
    safely in a new process.
    """
    result = package.wavsurrogate(matlab.double(signal.tolist()), type, adj)

    return result
