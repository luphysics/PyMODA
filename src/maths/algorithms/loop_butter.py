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
import numpy as np
from scipy.signal import filtfilt, butter


def bandpass_butter(c, n, flp, fhi, fs):
    fnq = fs / 2

    Wn = np.asarray([flp / fnq, fhi / fnq])
    b, a = butter(n, Wn)

    return filtfilt(b, a, c)


def loop_butter(signal_in: np.ndarray, fmin, fmax, fs):
    signal_in = signal_in

    optimal_order = 1
    max_out = np.max(signal_in)

    while max_out < 10 * np.max(signal_in):
        optimal_order += 1

        sig_out = bandpass_butter(signal_in, optimal_order, fmin, fmax, fs)
        max_out = np.max(sig_out)

    optimal_order -= 1
    sig_out = bandpass_butter(signal_in, optimal_order, fmin, fmax, fs)

    return sig_out, optimal_order
