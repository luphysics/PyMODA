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

from numpy import ndarray

from maths.params.REParams import REParams


def calculate(tfsupp: ndarray, tfr: ndarray, freq, wopt, params: REParams) -> tuple:
    """
    Extracts ridge curve from wavelet transform or
    windowed Fourier transform using MATLAB-packaged function.

    :param tfsupp:
    :param tfr:
    :param freq:
    :param wopt:
    :param params:
    :return:
    """
    import rectfr
    import matlab

    package = rectfr.initialize()

    iamp, iphi, ifreq, rtfsupp = package.rectfr(
        tfsupp,
        matlab.double(tfr.tolist()),
        matlab.double(freq.tolist()),
        params.get(),
        "direct",
    )

    return iamp, iphi, ifreq
