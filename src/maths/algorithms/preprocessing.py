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

from maths.TimeSeries import TimeSeries


def preprocess(time_series: TimeSeries, fs, fmin, fmax) -> np.ndarray:
    # TODO: fix
    return time_series.signal

    sig = time_series.signal
    L = len(sig)

    # Detrending
    X = np.arange(0, len(sig)).transpose() / fs
    XM = np.ones((len(X), 4,), dtype=np.complex)
    for pn in range(1, 4):
        CX = X ** pn
        XM[:, pn] = (CX - np.mean(CX)) / np.std(CX)

        sig -= XM * (np.linalg.pinv(XM) * sig)

    # Filtering
    fx = np.fft.fft(sig, L)
    Nq = np.ceil((L + 1) / 2)

    ff = np.asarray(
        np.arange(0, Nq),
        -np.fliplr(np.arange(1, L - Nq + 1))
    ) * fs / L

    ff = ff[:]
    fx[np.abs(ff) <= np.max([fmin, fs / L]) or np.abs(ff) >= fmax] = 0

    sig = np.fft.ifft(fx)
    return sig
