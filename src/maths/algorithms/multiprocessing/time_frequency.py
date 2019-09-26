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

import time

import numpy as np
from multiprocess import Queue

from maths.num_utils import matlab_to_numpy
from maths.params.TFParams import TFParams, _wft
from maths.signals.TimeSeries import TimeSeries


def _time_frequency(queue: Queue, time_series: TimeSeries, params: TFParams):
    """Should not be called in the main process."""
    # Don't move the import statements.
    from maths.algorithms.matlabwrappers import wft
    from maths.algorithms.matlabwrappers import wt

    if params.transform == _wft:
        func = wft
    else:
        func = wt

    transform, freq = func.calculate(time_series, params)
    transform = matlab_to_numpy(transform)
    freq = matlab_to_numpy(freq)

    amplitude = np.abs(transform)

    power = np.square(amplitude)
    length = len(amplitude)

    avg_ampl = np.empty(length, dtype=np.float64)
    avg_pow = np.empty(length, dtype=np.float64)

    for i in range(length):
        arr = amplitude[i]
        row = arr[np.isfinite(arr)]

        avg_ampl[i] = np.mean(row)
        avg_pow[i] = np.mean(np.square(row))

    print(f"Started putting items in queue at time: {time.time():.1f} seconds.")

    out = (
        time_series.name,
        time_series.times,
        freq,
        transform,
        amplitude,
        power,
        avg_ampl,
        avg_pow,
    )

    if queue:
        queue.put(out)
    else:
        return out
