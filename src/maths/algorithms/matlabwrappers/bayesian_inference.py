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

from gui.windows.bayesian.ParamSet import ParamSet
from maths.signals.TimeSeries import TimeSeries
from processes.mp_utils import process
from numpy import ndarray
from maths.num_utils import matlab_to_numpy


@process
def _moda_dynamic_bayesian_inference(
    signal1: TimeSeries, signal2: TimeSeries, params: ParamSet
):
    """
    UNUSED.

    Uses the MATLAB-packaged function to perform Bayesian inference.
    Unused because it causes a serious error on Linux. Check the Python implementation
    of Bayesian inference instead (`bayesian.py`).
    """
    import full_bayesian
    import matlab

    package = full_bayesian.initialize()

    sig1 = matlab.double(signal1.signal.tolist())
    sig2 = matlab.double(signal2.signal.tolist())

    int11, int12 = sorted(params.freq_range1)
    int21, int22 = sorted(params.freq_range2)

    fs = signal1.frequency
    win = params.window
    pr = params.propagation_const
    ovr = params.overlap
    bn = params.order
    ns = params.surr_count
    signif = params.confidence_level

    result = package.full_bayesian(
        sig1,
        sig2,
        float(int11),
        float(int12),
        float(int21),
        float(int22),
        fs,
        win,
        pr,
        ovr,
        bn,
        ns,
        signif,
    )
    out = []
    for item in result:
        try:
            if not isinstance(item, ndarray):
                item = matlab_to_numpy(item)
        except:
            pass

        out.append(item)

    return (signal1.name, *out)
