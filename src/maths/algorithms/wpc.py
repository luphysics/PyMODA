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
Wavelet phase coherence algorithm.
"""
import numpy as np


def wpc(signals, params):
    pass


def wphcoh(wt1, wt2):
    """
    Wavelet phase coherence.

    :param wt1:
    :param wt2:
    :return:
    """
    FN = min(wt1.shape[0], wt2.shape[0])

    wt1 = wt1[:FN]
    wt2 = wt1[:FN]

    phi1 = np.angle(wt1)
    phi2 = np.angle(wt2)

    phexp = np.exp(np.complex(0, 1) * (phi1 - phi2))

    phcoh = np.zeros((1, FN)) * np.NaN
    phdiff = np.zeros((1, FN)) * np.NaN

    for fn in range(FN):
        cphexp = phexp[fn]
        cphexp = cphexp[~np.isnan(cphexp)]

        wt1_i = wt1[fn]
        wt2_i = wt2[fn]

        NL = 0
        l = min(wt1.shape[1], wt2.shape[1])
        for j in range(l):
            NL += (wt1_i[fn][j] == 0 == wt2_i[fn][j])

        CL = len(cphexp)
        if CL > 0:
            phph = np.mean(cphexp) - NL / CL
            phcoh[fn] = np.abs(phph)
            phdiff[fn] = np.angle(phph)

    return phcoh, phdiff


def tlphcoh(wt1, wt2, freq, fs, wsize=10):
    """
    Time-localized phase coherence.

    :param wt1:
    :param wt2:
    :param freq:
    :param fs:
    :param wsize:
    :return:
    """
    NF, L = wt1.shape

    ipc = np.exp(np.complex(0, 1) * np.angle(wt1 * np.conj(wt2)))
    zpc = ipc
    zpc[np.isnan(zpc)] = 0

    zeros = np.zeros(NF, np.complex64)
    csum = np.cumsum(zpc, 1)
    print(csum.shape)

    np.hstack() # TODO: add this code
    cum_pc = np.asarray([zeros, csum], np.complex64)
    tpc = np.zeros(NF, L) * np.NaN

    for fn in range(NF):
        cs = ipc[fn]
        cumcs = cum_pc[fn]

        f = cs[~np.isnan(cs)]
        tn1 = f[0]
        tn2 = f[-1]

        window = np.round(wsize / freq[fn] * fs)
        window = window + 1 - np.mod(window, 2)
        hw = np.floor(window / 2)

        if len(tn1 + tn2) > 0 and window <= tn2 - tn1:
            locpc = np.abs(cumcs[tn1 + window:tn2 + 1] - cumcs[tn1:tn2 - window + 1]) / window
            tpc[fn, tn1 + hw:tn2 - hw] = locpc

    return tpc
