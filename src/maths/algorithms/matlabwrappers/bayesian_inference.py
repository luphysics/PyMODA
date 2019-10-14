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

from gui.windows.bayesian.ParamSet import ParamSet
from maths.signals.TimeSeries import TimeSeries
from processes import mp_utils


def _moda_dynamic_bayesian_inference(queue: Queue, signal1: TimeSeries, signal2: TimeSeries, params: ParamSet):
    mp_utils.setup_matlab_runtime()

    import full_bayesian
    import matlab
    package = full_bayesian.initialize()

    sig1 = matlab.double(signal1.signal.tolist())
    sig2 = matlab.double(signal2.signal.tolist())

    int1 = list(params.freq_range1)
    int2 = list(params.freq_range2)

    fs = signal1.frequency
    win = params.window
    pr = params.propagation_const
    ovr = params.overlap
    bn = params.order
    ns = params.surr_count
    signif = params.confidence_level

    result = package.full_bayesian(sig1, sig2, *int1, *int2, fs, win, pr, ovr, bn, ns, signif)

    queue.put((signal1.name, *result))
