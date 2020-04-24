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
Translation of the wavelet phase coherence algorithm from MODA.

STATUS: Finished, although surrogates are not complete (see `surrogates.py`).
"""
from typing import Tuple

import numpy as np
from numpy import ndarray
from pymodalib.algorithms.coherence import tlphcoh, wphcoh


def wpc(
    wt1: ndarray, wt2: ndarray, freq: ndarray, fs: float, wsize: int = 10
) -> Tuple[ndarray, ndarray, ndarray]:
    """
    Wavelet phase coherence.

    :param wt1: wavelet transform of the first signal
    :param wt2: wavelet transform of the second signal
    :param freq: frequencies at which transforms were calculated
    :param fs: sampling frequency
    :param wsize: window size
    :return: [2D array] absolute value of time-localised phase coherence; [1D array] phase coherence; [1D array] phase difference
    """
    tlpc = tlphcoh(wt1, wt2, freq, fs, wsize)
    pc, pdiff = wphcoh(wt1, wt2)
    return np.abs(tlpc), pc, pdiff
