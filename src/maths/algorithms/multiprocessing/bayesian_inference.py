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

import pymodalib
from numpy import ndarray

from gui.windows.bayesian.ParamSet import ParamSet
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

    interval1, interval2 = params.freq_range1, params.freq_range2

    fs = signal1.frequency
    bn = params.order

    win = params.window
    ovr = params.overlap
    pr = params.propagation_const
    signif = params.confidence_level

    result = pymodalib.bayesian_inference(
        sig1,
        sig2,
        fs=fs,
        interval1=interval1,
        interval2=interval2,
        surrogates=params.surr_count,
        window=win,
        overlap=ovr,
        order=bn,
        propagation_const=pr,
        signif=signif,
    )

    return (signal1.name, *result)
