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
from typing import Union

import numpy as np
from nptyping import Array
from numpy.random import permutation as randperm

from maths.signals.TimeSeries import TimeSeries

_RP = "RP"
_FT = "FT"
_AAFT = "AAFT"
_IAFFT1 = "IAAFT1"
_IAFFT2 = "IAAFT2"
_WIAFFT = "WIAAFT"
_tshift = "tshift"
_CPP = "CPP"


def surrogate_calc(time_series: Union[TimeSeries, Array], N, method, pp, fs):
    """
    Calculates surrogates.

    :param time_series: the original signal as a TimeSeries
    :param N: the number of surrogates
    :param method: the required surrogate type
    :param pp: whether to perform preprocessing
    :param fs: the sampling frequency
    :return: the surrogate signal(s) and params
    """
    if isinstance(time_series, TimeSeries):
        sig = time_series.signal
    else:
        sig = time_series

    surr = np.empty((N, len(sig)), dtype=np.float64)  # TODO: check this

    params = Params()
    origsig = sig
    params.origsig = origsig
    params.method = method
    params.numsurr = N
    params.fs = fs

    if pp:
        sig, time, ks, ke = preprocessing(sig, fs)
        params.preprocessing = True
        params.cutsig = sig
        params.sigstart = ks
        params.sigend = ke
    else:
        time = np.linspace(0, len(sig), len(sig) / fs)
        params.preprocessing = False

    L = len(sig)
    L2 = np.int(np.ceil(L / 2))

    params.time = time

    if method == _RP:
        for k in range(N):
            surr[k, :] = sig[randperm(L)]

    elif method == _FT:
        b = 2 * np.pi

        # Note: removed 'eta' parameter from function.
        eta = b * np.random.rand(N, L2 - 1)

        ftsig = np.fft.fft(sig, axis=0)
        ftrp = np.zeros((N, len(ftsig),), dtype=np.complex64)
        ftrp[:, 0] = ftsig[0]

        F = ftsig[1:L2]
        F = np.tile(F, (N, 1,))

        ftrp[:, 1:L2] = np.multiply(F, np.exp(np.complex(0, 1) * eta))
        ftrp[:, 1 + L - L2:L] = np.conj(np.fliplr(ftrp[:, 1:L2]))

        surr = np.fft.ifft(ftrp, axis=0)
        surr = np.real(surr)

        params.rphases = eta

    elif method == _AAFT:
        b = 2 * np.pi
        eta = b * np.random.rand(N, L2 - 1)

        val = np.sort(sig)
        ind = np.argsort(sig)
        rankind = np.empty(ind.shape, dtype=np.int)
        rankind[ind] = np.arange(0, L)

        gn = np.sort(np.random.randn(N, len(sig)), 1)
        for j in range(N):
            gn[j, :] = gn[j, rankind]

        ftgn = np.fft.fft(gn, axis=0)
        F = ftgn[:, 1:L2]

        surr = np.zeros((N, len(sig)), dtype=np.complex)
        surr[:, 0] = gn[:, 0]
        surr[:, 1:L2] = np.multiply(F, np.exp(np.complex(0, 1) * eta))
        surr[:, 1 + L - L2:L] = np.conj(np.fliplr(surr[:, 1:L2]))
        surr = np.fft.ifft(surr, axis=0)

        ind2 = np.argsort(surr, axis=1)
        rrank = np.zeros((1, L), dtype=np.int)
        for k in range(N):
            rrank[:, ind2[k, :]] = np.arange(0, L)
            surr[k, :] = val[rrank]

        surr = np.real(surr)

    # TODO: add later
    elif method == _IAFFT1:
        pass
    elif method == _IAFFT2:
        pass
    elif method == _WIAFFT:
        pass
    elif method == _tshift:
        pass
    elif method == _CPP:
        signal = np.mod(sig, 2 * np.pi)

        dcpoints = np.nonzero((signal[1:] - signal[:-1]) < -np.pi)
        NC = len(dcpoints) - 1

        if NC > 0:
            cycles = np.zeros(NC)

            for k in range(NC):
                cycles[k] = signal[dcpoints[k] + 1: dcpoints[k + 1]]

            stcycle = signal[:dcpoints[0]]
            endcycle = signal[dcpoints[k + 1] + 1:]

            for sn in range(N):
                surr[sn, :] = np.unwrap(np.hstack([
                    stcycle, cycles[np.random.permutation(NC), endcycle]
                ]))

        else:
            for sn in range(N):
                surr[sn, :] = np.unwrap(signal)

    params.type = method
    params.numsurr = N
    if pp:
        params.preprocessing = True
        params.cutsig = sig
        params.sigstart = ks
        params.sigend = ke
    else:
        params.preprocessing = False

    params.time = time
    params.fs = fs

    return surr, params


def preprocessing(sig, fs):
    sig -= np.mean(sig)
    t = np.linspace(0, len(sig), len(sig) / fs)
    L = len(sig)
    p = 10

    K1 = np.round(L / 100)
    k1 = sig[:K1]
    K2 = np.round(L / 10)
    k2 = sig[:K2]

    if len(k1) <= p:
        p = len(k1) - 1

    d = np.zeros(len(k1) - p, len(k2) - p)

    for j in range(len(k1) - p):
        for k in range(len(k2) - p):
            d[j, k] = np.sum(np.abs(k1[j:j + p]) - k2[k:k + p])

    v, I = np.min(np.abs(d), [], 2)
    _, I2 = np.min(v)

    kstart = I2
    kend = I[I2] + len(sig[:-k2])
    cutsig = sig[kstart:kend]
    t2 = t[kstart:kend]

    return cutsig, t2, kstart, kend


class Params:

    def __init__(self):
        self.origsig = None
        self.numsurr = None
        self.fs = None
        self.method = None
