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
from maths.algorithms.params import TFParams, _f0, _fmin
from utils import args

# This must be above the WFT and matlab imports.
args.setup_matlab_runtime()

import WFT
import matlab

package = WFT.initialize()


def calculate(time_series, params: TFParams):
    """
    Calculates the windowed Fourier transform.

    IMPORTANT: this function should not be called directly due to issues
    with the LD_LIBRARY_PATH on Linux. Instead, use `MPHelper` to call it
    safely in a new process.
    """
    signal_matlab = matlab.double([time_series.signal.tolist()])

    """
    The value passed for 'f0' should actually be that of 'fr' in the case
    of WFT. In the Matlab version this is handled before passing the value 
    to the function, so we'll do the same.
    
    When the value has been left blank, there is no problem because this
    case is handled by the Matlab function.
    """
    params_dict = params.get()

    f0 = params_dict.get(_f0)
    fmin = params_dict.get(_fmin)

    if f0 is not None and fmin is not None and fmin != 0:
        params_dict[_f0] = f0 / fmin

    wft, frequency = package.wft(signal_matlab,
                                 params.fs,
                                 params_dict,
                                 nargout=2)

    return wft, frequency
