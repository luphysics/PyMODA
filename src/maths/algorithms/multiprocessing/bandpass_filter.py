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
from typing import Tuple

import numpy as np
from pymodalib.implementations.python.filtering import loop_butter
from scipy.signal import hilbert
from numpy import ndarray
from maths.signals.TimeSeries import TimeSeries

from processes.mp_utils import process


@process
def _bandpass_filter(
    time_series: TimeSeries, fmin, fmax, fs
) -> Tuple[str, ndarray, ndarray, ndarray, Tuple[float, float]]:
    """
    Performs the bandpass filter on a signal. Used in ridge-extraction and filtering.

    :param time_series: the signal
    :param fmin: the minimum frequency
    :param fmax: the maximum frequency
    :param fs:  the sampling frequency
    :return:
    [str] name of the signal;
    [?] bands
    [1D array] phase
    [1D array] amplitude
    [tuple] the min and max frequencies
    """
    bands, _ = loop_butter(time_series.signal, fmin, fmax, fs)
    h = hilbert(bands)

    phase = np.angle(h)
    amp = np.abs(h)

    return time_series.name, bands, phase, amp, (fmin, fmax)
