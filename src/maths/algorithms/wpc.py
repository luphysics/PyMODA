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

STATUS: Finished. Surrogates may need improvements.
"""
from typing import Tuple

import numpy as np
from numpy import ndarray


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


def wphcoh(wt1: ndarray, wt2: ndarray) -> Tuple[ndarray, ndarray]:
    """
    Time-averaged wavelet phase coherence.

    :param wt1: wavelet transform of first signal
    :param wt2: wavelet transform of second signal
    :return: [1D array] phase coherence; [1D array] phase difference
    """
    FN = min(wt1.shape[0], wt2.shape[0])

    wt1 = wt1[:FN, :]
    wt2 = wt2[:FN, :]

    phi1 = np.angle(wt1)
    phi2 = np.angle(wt2)

    phexp = np.exp(1j * (phi1 - phi2))

    phcoh = np.zeros((FN, 1), np.float64) * np.NaN
    phdiff = np.zeros((FN, 1), np.float64) * np.NaN

    for fn in range(FN):
        cphexp = phexp[fn, :]
        cphexp = cphexp[~np.isnan(cphexp)]

        wt1_i = wt1[fn]
        wt2_i = wt2[fn]

        NL = 0
        l = min(wt1.shape[1], wt2.shape[1])
        for j in range(l):
            NL += 0 == wt1_i[j] == wt2_i[j]

        CL = cphexp.shape[0]
        if CL > 0:
            phph = np.mean(cphexp) - NL / CL
            phcoh[fn] = np.abs(phph)
            phdiff[fn] = np.angle(phph)

    return phcoh, phdiff


def tlphcoh(
    wt1: ndarray, wt2: ndarray, freq: ndarray, fs: float, wsize: int = 10
) -> ndarray:
    """
    Time-localized phase coherence.

    :param wt1: Wavelet transform of the first signal
    :param wt2: Wavelet transform og the second signal with the same shape as wt1
    :param freq: Frequencies at which the wavelet transforms wt1 and wt2 were calculated
    :param fs: Sampling frequency
    :param wsize: Window size, default is 10 samples
    :return: [2D array] time-localized wavelet phase coherence with the same shape as wt1
    """
    NF, L = wt1.shape

    ipc = np.exp(1j * np.angle(wt1 * wt2.conj()))
    zpc = ipc.copy()
    zpc[np.isnan(zpc)] = 0

    zeros = np.zeros((NF, 1), np.complex64)
    csum = np.cumsum(zpc, axis=1)

    cum_pc = np.hstack((zeros, csum))
    tpc = np.zeros((NF, L), np.complex64) * np.NaN

    for fn in range(NF):
        cs = ipc[fn, :]
        cumcs = cum_pc[fn, :]

        f = np.nonzero(~np.isnan(cs))[0]
        window = np.round(wsize / freq[fn] * fs)
        window += 1 - np.mod(window, 2)

        hw = np.floor(window / 2)

        if len(f) >= 2:
            tn1 = f[0]
            tn2 = f[-1]
            if window <= tn2 - tn1:
                window = np.int(window)
                hw = np.int(hw)

                locpc = (
                    np.abs(
                        cumcs[tn1 + window : tn2 + 1 + 1]
                        - cumcs[tn1 : tn2 - window + 1 + 1]
                    )
                    / window
                )
                tpc[fn, tn1 + hw : tn2 - hw + 1] = locpc

    return tpc  # TODO: implement 'under_sample' from matlab version
