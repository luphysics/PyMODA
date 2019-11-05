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
from typing import Tuple

import numpy as np
from multiprocess.pool import Pool
from numpy import ndarray

from maths.algorithms.surrogates import surrogate_calc
from maths.algorithms.wpc import wphcoh, wpc
from maths.num_utils import matlab_to_numpy
from maths.params.PCParams import PCParams
from maths.signals.TimeSeries import TimeSeries
from processes.mp_utils import process


@process
def _wt_surrogate_calc(args: tuple):
    from maths.algorithms.matlabwrappers import wt

    wt1, surrogate, params, index = args

    transform, freq = wt.calculate(surrogate, params)
    wt_surrogate = matlab_to_numpy(transform)

    surr_avg, _ = wphcoh(wt1, wt_surrogate)
    return index, surr_avg


@process
def _phase_coherence(
    signal_pair: Tuple[TimeSeries, TimeSeries], params: PCParams
) -> Tuple[Tuple[TimeSeries, TimeSeries], ndarray, ndarray, ndarray, ndarray]:
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
    args = [(wt1, surrogates[i], params, i) for i in range(surr_count)]
    surr_results = pool.map(_wt_surrogate_calc, args)

    tpc_surr = [None for _ in range(surr_count)]
    for (index, result) in surr_results:
        tpc_surr[index] = result

    if len(tpc_surr) > 0:
        tpc_surr = np.mean(tpc_surr, axis=0)

    # Calculate phase coherence.
    tpc, pc, pdiff = wpc(wt1, wt2, freq, fs)

    return signal_pair, tpc, pc, pdiff, tpc_surr
