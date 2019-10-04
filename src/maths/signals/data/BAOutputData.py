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
from dataclasses import dataclass
from numpy import ndarray


@dataclass
class BAOutputData:
    """
    Data class containing data returned by bispectrum analysis.
    """

    # Amplitude and power of wavelet transform 1.
    amp_wt1: ndarray
    pow_wt1: ndarray

    # Average amplitude and power of wavelet transform 1.
    avg_amp_wt1: ndarray
    avg_pow_wt1: ndarray

    # Amplitude and power of wavelet transform 2.
    amp_wt2: ndarray
    pow_wt2: ndarray

    # Average amplitude and power of wavelet transform 2.
    avg_amp_wt2: ndarray
    avg_pow_wt2: ndarray

    times: ndarray
    freq: ndarray

    # Bispectra.
    bispxxx: ndarray
    bispppp: ndarray
    bispxpp: ndarray
    bisppxx: ndarray

    # Surrogates.
    surrxxx: ndarray
    surrppp: ndarray
    surrxpp: ndarray
    surrpxx: ndarray
