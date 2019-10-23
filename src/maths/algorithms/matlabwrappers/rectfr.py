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
import matlab
import rectfr

from maths.params.REParams import REParams

package = rectfr.initialize()


def calculate(tfsupp, tfr, freq, wopt, params: REParams) -> tuple:
    """
    Extracts ridge curve from wavelet transform or windowed Fourier transform.

    IMPORTANT: this function should not be called directly due to issues
    with the LD_LIBRARY_PATH on Linux. Instead, use `MPHandler` to call it
    safely in a new process.
    """

    iamp, iphi, ifreq, rtfsupp = package.rectfr(
        tfsupp,
        matlab.double(tfr.tolist()),  # Pass nothing; data is saved in cache.
        matlab.double(freq.tolist()),  # Pass nothing; data is saved in cache.
        params.get(),
        "direct",
    )

    return iamp, iphi, ifreq
