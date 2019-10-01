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
import math
from math import nan

from multiprocess import Queue, Process

from maths.algorithms.matlab_utils import *
from maths.num_utils import matlab_to_numpy
from maths.params.BAParams import BAParams
from maths.signals.SignalPairs import SignalPairs
from maths.signals.TimeSeries import TimeSeries


def _bispectrum_analysis(queue: Queue,
                         sig1: TimeSeries,
                         sig2: TimeSeries,
                         params: BAParams) -> None:
    from maths.algorithms.matlabwrappers import bispec_wav_new, wav_surrogate

    name = sig1.name
    sig1 = sig1.signal
    sig2 = sig2.signal

    sig1list = sig1.tolist()
    sig2list = sig2.tolist()

    surrxxx = []  # TODO: set dimensions
    surrppp = []
    surrxpp = []
    surrpxx = []

    sigcheck = np.sum(np.abs(sig1 - sig2))

    fs = params.fs
    preprocess = params.preprocess

    ns = params.surr_count or 0
    nv = params.nv

    fmax = params.fmax or fs / 2
    fmin = params.fmin or math.nan
    f0 = params.f0 or 1

    params = {
        "nv": nv,
        "fmin": fmin,
        "fmax": fmax,
        "f0": f0,
    }

    # Note: attempted to calculate bispec_wav_new in a process each. Did not work
    # due to some strange problem with the Matlab runtime. Processes would
    # hang at the `package.initialize()` stage for unknown reasons.
    if sigcheck != 0:
        if not preprocess:  # TODO: check this block.
            bispxxx, _, _, _ = bispec_wav_new.calculate(sig1list, sig1list, fs, params)
            bispppp, _, _, _ = bispec_wav_new.calculate(sig2list, sig2list, fs, params)
            bispxpp, freq, wt1, wt2 = bispec_wav_new.calculate(sig1list, sig2list, fs, params)
            bisppxx, _, _, _ = bispec_wav_new.calculate(sig2list, sig1list, fs, params)

            if ns > 0:
                for j in range(ns):
                    surr1 = wav_surrogate.calculate(sig1list, "IAAFT2", 1)
                    surr2 = wav_surrogate.calculate(sig2list, "IAAFT2", 1)

                    surrxxx[:, :, j] = abs(bispec_wav_new.calculate(surr1, surr1, fs, params))
                    surrppp[:, :, j] = abs(bispec_wav_new.calculate(surr2, surr2, fs, params))
                    surrxpp[:, :, j] = abs(bispec_wav_new.calculate(surr1, surr2, fs, params))
                    surrpxx[:, :, j] = abs(bispec_wav_new.calculate(surr2, surr1, fs, params))

        else:
            bispxxx, _, _, _ = bispec_wav_new.calculate(sig1list, sig1list, fs, params)
            bispppp, _, _, _ = bispec_wav_new.calculate(sig2list, sig2list, fs, params)
            bispxpp, freq, wt1, wt2 = bispec_wav_new.calculate(sig1list, sig2list, fs, params)
            bisppxx, _, _, _ = bispec_wav_new.calculate(sig2list, sig1list, fs, params)

            if ns > 0:
                for j in range(ns):
                    surr1 = wav_surrogate.calculate(sig1list, "IAAFT2", 1)
                    surr2 = wav_surrogate.calculate(sig2list, "IAAFT2", 1)

                    surrxxx[:, :, j] = abs(bispec_wav_new.calculate(surr1, surr1, fs, params))
                    surrppp[:, :, j] = abs(bispec_wav_new.calculate(surr2, surr2, fs, params))
                    surrxpp[:, :, j] = abs(bispec_wav_new.calculate(surr1, surr2, fs, params))
                    surrpxx[:, :, j] = abs(bispec_wav_new.calculate(surr2, surr1, fs, params))

    else:
        raise Exception("sigcheck == 0. This case is not implemented yet.")  # TODO

    freq = matlab_to_numpy(freq)
    queue.put((
        name,
        freq,
        wt1,
        wt2,
        bispxxx,
        bispppp,
        bispxpp,
        bisppxx,
        surrxxx,
        surrppp,
        surrxpp,
        surrpxx,
    ))
