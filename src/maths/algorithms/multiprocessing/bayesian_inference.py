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

from typing import List, Tuple

import numpy as np
import scipy
from numpy import ndarray
from scipy.signal import hilbert

from gui.windows.bayesian.ParamSet import ParamSet
from maths.algorithms.bayesian import bayes_main, dirc, CFprint
from maths.algorithms.loop_butter import loop_butter
from maths.algorithms.matlab_utils import sort2d
from maths.algorithms.surrogates import surrogate_calc
from maths.signals.TimeSeries import TimeSeries
from processes.mp_utils import process


@process
def _dynamic_bayesian_inference(
    signal1: TimeSeries, signal2: TimeSeries, params: ParamSet
) -> Tuple[
    str,
    ndarray,
    ndarray,
    ndarray,
    ndarray,
    ndarray,
    ndarray,
    ndarray,
    ndarray,
    ndarray,
    ndarray,
    ndarray,
]:
    sig1 = signal1.signal
    sig2 = signal2.signal

    fs = signal1.frequency
    interval1, interval2 = params.freq_range1, params.freq_range2
    bn = params.order

    bands1, _ = loop_butter(sig1, *interval1, fs)
    phi1 = np.angle(hilbert(bands1))

    bands2, _ = loop_butter(sig2, *interval2, fs)
    phi2 = np.angle(hilbert(bands2))

    p1 = phi1
    p2 = phi2

    win = params.window
    ovr = params.overlap
    pr = params.propagation_const
    signif = params.confidence_level

    ### Bayesian inference ###

    tm, cc = bayes_main(phi1, phi2, win, 1 / fs, ovr, pr, 0, bn)

    from maths.algorithms.matlab_utils import zeros, mean

    N, s = cc.shape
    s -= 1

    cpl1 = zeros(N)
    cpl2 = zeros(N)

    q21 = zeros((s, s, N))
    q12 = zeros(q21.shape)

    for m in range(N):
        cpl1[m], cpl2[m], _ = dirc(cc[m, :], bn)
        _, _, q21[:, :, m], q12[:, :, m] = CFprint(cc[m, :], bn)

    cf1 = q21
    cf2 = q12

    mcf1 = np.squeeze(mean(q21, 2))
    mcf2 = np.squeeze(mean(q12, 2))

    ns = params.surr_count
    surr1, _ = surrogate_calc(phi1, ns, "CPP", 0, fs)
    surr2, _ = surrogate_calc(phi2, ns, "CPP", 0, fs)

    cc_surr: List[ndarray] = []
    scpl1 = zeros((ns, len(cc)))
    scpl2 = scpl1.copy()

    for n in range(ns):
        _, _cc_surr = bayes_main(surr1[n, :], surr2[n, :], win, 1 / fs, ovr, pr, 1, bn)
        cc_surr.append(_cc_surr)

        for idx in range(len(_cc_surr)):
            scpl1[n, idx], scpl2[n, idx], _ = dirc(_cc_surr[idx], bn)

    alph = signif
    alph = 1 - alph / 100

    if scpl1.size > 0:
        if np.floor((ns + 1) * alph) == 0:
            surr_cpl1 = np.max(scpl1)
            surr_cpl2 = np.max(scpl2)
        else:
            K = np.floor((ns + 1) * alph)
            K = np.int(K)

            s1 = sort2d(scpl1, descend=True)
            s2 = sort2d(scpl2, descend=True)

            surr_cpl1 = s1[K, :]
            surr_cpl2 = s2[K, :]
    else:
        surr_cpl1 = None
        surr_cpl2 = None

    return (
        signal1.name,
        tm,
        p1,
        p2,
        cpl1,
        cpl2,
        cf1,
        cf2,
        mcf1,
        mcf2,
        surr_cpl1,
        surr_cpl2,
    )


if __name__ == "__main__":
    try:
        data = scipy.io.loadmat("../bayes.mat")
    except FileNotFoundError:
        import sys

        print("Error: file does not exist.")
        sys.exit(1)

    phi1, phi2, win, fs, ovr, pr, bn = (
        data["phi1"],
        data["phi2"],
        data["win"][0, 0],
        data["fs"][0, 0],
        data["ovr"][0, 0],
        data["pr"][0, 0],
        data["bn"][0, 0],
    )
    tm, cc = bayes_main(phi1, phi2, win, 1 / fs, ovr, pr, 0, bn)

    data["py1"] = tm
    data["py2"] = cc

    scipy.io.savemat("../bayes.mat", data)
