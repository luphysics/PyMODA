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

from maths.multiprocessing import mp_utils
from maths.num_utils import matlab_to_numpy
from maths.params.REParams import REParams
from maths.signals.TimeSeries import TimeSeries


def _ridge_extraction(queue, time_series: TimeSeries, params: REParams):
    mp_utils.setup_matlab_runtime()
    import ridge_extraction
    import matlab

    package = ridge_extraction.initialize()

    d = params.get()
    result = package.ridge_extraction(1,
                                      matlab.double(time_series.signal.tolist()),
                                      params.fs,
                                      d["fmin"],
                                      d["fmax"],
                                      d["CutEdges"],
                                      d["Preprocess"],
                                      d["Wavelet"],
                                      nargout=6)

    transform, freq, iamp, iphi, ifreq, filtered_signal = result

    transform = matlab_to_numpy(transform)
    freq = matlab_to_numpy(freq)

    iamp = matlab_to_numpy(iamp)
    iamp = iamp.reshape(iamp.shape[1])

    iphi = matlab_to_numpy(iphi)
    iphi = iphi.reshape(iphi.shape[1])

    ifreq = matlab_to_numpy(ifreq)
    ifreq = ifreq.reshape(ifreq.shape[1])

    filtered_signal = matlab_to_numpy(filtered_signal)
    filtered_signal = filtered_signal.reshape(filtered_signal.shape[1])

    amplitude = np.abs(transform)
    powers = np.square(amplitude)

    length = len(amplitude)

    avg_ampl = np.empty(length, dtype=np.float64)
    avg_pow = np.empty(length, dtype=np.float64)

    for i in range(length):
        arr = amplitude[i]
        row = arr[np.isfinite(arr)]

        avg_ampl[i] = np.mean(row)
        avg_pow[i] = np.mean(np.square(row))

    queue.put((
        time_series.name,
        time_series.times,
        freq,
        transform,
        amplitude,
        powers,
        avg_ampl,
        avg_pow,
        (d["fmin"], d["fmax"]),
        filtered_signal,
        iphi,
        ifreq,
    ))