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
from multiprocess import Queue

from maths.params.BAParams import BAParams
from maths.signals.SignalPairs import SignalPairs

from maths.algorithms.matlab_utils import *


def _bispectrum_analysis(queue: Queue, params: BAParams):
    from maths.algorithms import bispec_wav_new

    signals: SignalPairs = params.signals
    sig1, sig2 = signals.get_pair_by_index(0)
    sig1 = sig1.signal.tolist()
    sig2 = sig2.signal.tolist()

    bispxxx = []
    bispppp = []
    bispxpp = []
    bisppxx = []
    surrxxx = []
    surrppp = []
    surrxpp = []
    surrpxx = []

    sigcheck = np.sum(np.abs(signals[0] - signals[1]))

    d = params.get()
    nv = d["nv"]
    ns = params.surr_count
    preprocess = d["Preprocess"]

    if sigcheck != 0:
        if preprocess:
            bispxxx = bispec_wav_new.calculate(sig1, sig1, params)
            bispxxx = np.abs(bispxxx[0])

            bispppp = bispec_wav_new.calculate(sig2, sig2, params)
            bispppp = np.abs(bispppp[0])

            bispxpp, freq, wopt, wt1, wt2 = bispec_wav_new.calculate(sig1, sig2, params)
            bispxpp = np.abs(bispxpp)

            bisppxx = bispec_wav_new.calculate(sig2, sig1, params)
            bisppxx = np.abs(bispppp[0])

            if ns > 0:
                for j in range(ns):
                    surrxxx[:, :, j] = abs() # TODO: continue here
