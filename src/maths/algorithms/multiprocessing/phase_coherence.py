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
import warnings
from typing import Tuple

import numpy as np
import pymodalib
from multiprocess.pool import Pool
from numpy import ndarray

from maths.algorithms.surrogates import surrogate_calc
from maths.algorithms.wpc import wphcoh, wpc
from maths.params.PCParams import PCParams
from maths.signals.TimeSeries import TimeSeries
from processes.mp_utils import process


@process
def _wt_surrogate_calc(
        wt_signal: ndarray, surrogate: ndarray, params: PCParams
) -> ndarray:
    """
    Calculates the phase coherence between a signal and a surrogate.

    :param wt_signal: the wavelet transform of the signal
    :param surrogate: the values of the surrogate (not the wavelet transform)
    :param params: the params object with parameters to pass to the wavelet transform function
    :return: [1D array] the wavelet phase coherence between the signal and the surrogate
    """
    wt_surrogate, _ = pymodalib.wavelet_transform(surrogate, params.fs, **params.get(), Display="off")

    surr_avg, _ = wphcoh(wt_signal, wt_surrogate)
    return surr_avg


@process
def _phase_coherence(
        signal_pair: Tuple[TimeSeries, TimeSeries], params: PCParams
) -> Tuple[Tuple[TimeSeries, TimeSeries], ndarray, ndarray, ndarray, ndarray]:
    """
    Function which uses `wpc` to calculate phase coherence for a single pair of signals. The signals must have
    their wavelet transforms attached in their `output_data` member variable.

    :param signal_pair: tuple containing 2 signals
    :param params: the params object with parameters for the function
    :return:
    [tuple] the pair of signals;
    [2D array] the time-localised phase coherence;
    [1D array] phase coherence;
    [1D array] phase difference;
    [1D array] time-localised phase coherence of surrogates
    """
    s1, s2 = signal_pair

    wt1 = s1.output_data.values
    wt2 = s2.output_data.values

    freq = s1.output_data.freq
    fs = s1.frequency

    # Calculate surrogates.
    surr_count = params.surr_count
    surr_method = params.surr_method
    surr_preproc = params.surr_preproc
    surrogates, _ = surrogate_calc(s1, surr_count, surr_method, surr_preproc, fs)

    # Calculate surrogates.
    pool = Pool()
    args = [(wt1, surrogates[i], params) for i in range(surr_count)]
    tpc_surr = pool.starmap(_wt_surrogate_calc, args)

    if len(tpc_surr) > 0:
        tpc_surr = np.mean(tpc_surr, axis=0)

    # Calculate phase coherence.
    tpc, pc, pdiff = wpc(wt1, wt2, freq, fs)

    return signal_pair, tpc, pc, pdiff, tpc_surr
