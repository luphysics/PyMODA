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
from numpy.random import permutation as randperm
from time import time as t

from maths.TimeSeries import TimeSeries

_RP = "RP"
_FT = "FT"
_AAFT = "AAFT"
_IAFFT1 = "IAAFT1"
_IAFFT2 = "IAAFT2"
_WIAFFT = "WIAAFT"
_tshift = "tshift"


def surrogate_calc(time_series: TimeSeries, N, method, pp, fs):
    """
    Calculates surrogates.

    :param sig: the original signal as a TimeSeries
    :param N: the number of surrogates
    :param method: the required surrogate type
    :param pp: whether to perform preprocessing
    :param fs: the sampling frequency
    :return: the surrogate signal(s) and params
    """
    sig = time_series.signal
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
    L2 = np.ceil(L / 2)

    params.time = time

    if method == _RP:
        for k in range(0, N):
            surr[k, :] = sig[randperm(L)]

    # TODO: add later
    elif method == _FT:
        pass
    elif method == _AAFT:
        pass
    elif method == _IAFFT1:
        pass
    elif method == _IAFFT2:
        pass
    elif method == _WIAFFT:
        pass
    elif method == _tshift:
        pass

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
