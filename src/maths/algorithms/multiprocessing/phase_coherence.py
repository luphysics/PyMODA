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
from multiprocess import Queue, Process

from maths.algorithms.surrogates import surrogate_calc
from maths.algorithms.wpc import wphcoh, wpc
from maths.num_utils import matlab_to_numpy
from maths.params.PCParams import PCParams
from processes.mp_utils import process


@process
def _wt_surrogate_calc(queue, wt1, surrogate, params, index):
    from maths.algorithms.matlabwrappers import wt

    transform, freq = wt.calculate(surrogate, params)
    wt_surrogate = matlab_to_numpy(transform)

    surr_avg, _ = wphcoh(wt1, wt_surrogate)
    queue.put((index, surr_avg))


@process
def _phase_coherence(queue, signal_pair, params: PCParams):
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

    tpc_surr = list(range(surr_count))
    processes = []
    queues = []

    # Create processes for surrogates.
    for i in range(surr_count):
        q = Queue()
        queues.append(q)

        processes.append(
            Process(target=_wt_surrogate_calc, args=(q, wt1, surrogates[i], params, i))
        )

    # Start processes for surrogates.
    for p in processes:
        p.start()

    # Calculate phase coherence.
    tpc, pc, pdiff = wpc(wt1, wt2, freq, fs)

    # Wait for processes to calculate surrogate results.
    # This is fine since we're not running on the main process.
    for p in processes:
        p.join()

    # After all processes finished, get all surrogate results.
    for q in queues:
        index, result = q.get()
        tpc_surr[index] = result

    if len(tpc_surr) > 0:
        tpc_surr = np.mean(tpc_surr, axis=0)

    # Put all results, including phase coherence and surrogates,
    # in the queues to be returned to the GUI.
    queue.put((signal_pair, tpc, pc, pdiff, tpc_surr))
