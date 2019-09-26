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

from multiprocess import Queue

from maths.algorithms.matlab_utils import *
from maths.num_utils import matlab_to_numpy
from maths.params.BAParams import BAParams
from maths.signals.SignalPairs import SignalPairs
from maths.signals.TimeSeries import TimeSeries


def _bispectrum_analysis(queue: Queue, sig1: TimeSeries, sig2: TimeSeries, params: BAParams) -> None:
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

    d = params.get()
    nv = d["nv"]
    ns = params.surr_count
    preprocess = d["Preprocess"]

    if sigcheck != 0:
        if not preprocess:
            bispxxx = bispec_wav_new.calculate(sig1list, sig1list, params)
            bispxxx = np.abs(bispxxx[0])

            bispppp = bispec_wav_new.calculate(sig2list, sig2list, params)
            bispppp = np.abs(bispppp[0])

            bispxpp, freq, wopt, wt1, wt2 = bispec_wav_new.calculate(sig1list, sig2list, params)
            bispxpp = np.abs(bispxpp)

            bisppxx = bispec_wav_new.calculate(sig2list, sig1list, params)
            bisppxx = np.abs(bispppp[0])

            if ns > 0:
                for j in range(ns):
                    surr1 = wav_surrogate.calculate(sig1list, "IAAFT2", 1)
                    surr2 = wav_surrogate.calculate(sig2list, "IAAFT2", 1)

                    params.set_item("num", 1)
                    surrxxx[:, :, j] = abs(bispec_wav_new.calculate(surr1, surr1, params))

                    params.set_item("num", 2)
                    surrppp[:, :, j] = abs(bispec_wav_new.calculate(surr2, surr2, params))

                    params.set_item("num", 3)
                    surrxpp[:, :, j] = abs(bispec_wav_new.calculate(surr1, surr2, params))

                    params.set_item("num", 4)
                    surrpxx[:, :, j] = abs(bispec_wav_new.calculate(surr2, surr1, params))

        else:
            bispxxx = bispec_wav_new.calculate(sig1list, sig1list, params)
            bispxxx = matlab_to_numpy(bispxxx)
            bispxxx = np.abs(bispxxx)

            bispppp = bispec_wav_new.calculate(sig2list, sig2list, params)
            bispppp = matlab_to_numpy(bispppp)
            bispppp = np.abs(bispppp)

            bispxpp, freq, wopt, wt1, wt2 = bispec_wav_new.calculate(sig1list, sig2list, params)[:5]
            bispxpp = matlab_to_numpy(bispxpp)
            bispxpp = np.abs(bispxpp)

            bisppxx = bispec_wav_new.calculate(sig2list, sig1list, params)
            bisppxx = matlab_to_numpy(bisppxx)
            bisppxx = np.abs(bisppxx)

            if ns > 0:
                for j in range(ns):
                    surr1 = wav_surrogate.calculate(sig1list, "IAAFT2", 1)
                    surr2 = wav_surrogate.calculate(sig2list, "IAAFT2", 1)

                    params.set_item("num", 1)
                    surrxxx[:, :, j] = abs(bispec_wav_new.calculate(surr1, surr1, params))

                    params.set_item("num", 2)
                    surrppp[:, :, j] = abs(bispec_wav_new.calculate(surr2, surr2, params))

                    params.set_item("num", 3)
                    surrxpp[:, :, j] = abs(bispec_wav_new.calculate(surr1, surr2, params))

                    params.set_item("num", 4)
                    surrpxx[:, :, j] = abs(bispec_wav_new.calculate(surr2, surr1, params))

    else:
        raise Exception("sigcheck = 0. This case is not implemented yet.")  # TODO

    freq = matlab_to_numpy(freq)

    queue.put((
        name,
        freq,
        bispxxx,
        bispppp,
        bispxpp,
        bisppxx,
        surrxxx,
        surrppp,
        surrxpp,
        surrpxx,
    ))
