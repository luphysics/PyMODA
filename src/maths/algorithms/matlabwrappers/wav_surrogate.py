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


def calculate(signal: ndarray, surr_type: str, adj: int) -> ndarray:
    """
    Calculates surrogates using the MATLAB-packaged function. Used in bispectrum analysis for
    IAAFT2 surrogates.

    :param signal: the signal
    :param surr_type: the type of surrogate
    :param adj: ?
    :return: [1D array] the surrogate signal
    """
    import matlab
    import wavsurrogate

    package = wavsurrogate.initialize()

    if isinstance(signal, ndarray):
        signal = signal.tolist()

    result = package.wavsurrogate(matlab.double(signal), surr_type, adj)

    return result
