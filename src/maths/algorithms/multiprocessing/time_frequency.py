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
from numpy import ndarray

from maths.num_utils import matlab_to_numpy
from maths.params.TFParams import TFParams, _wft
from maths.signals.TimeSeries import TimeSeries
from processes.mp_utils import process


@process
def _time_frequency(
    time_series: TimeSeries, params: TFParams
) -> Tuple[str, ndarray, ndarray, ndarray, ndarray, ndarray, ndarray, ndarray]:
    """
    Performs a wavelet transform or windowed Fourier transform using the MATLAB-packaged libraries.

    :param time_series: the signal to transform
    :param params: the input parameters for the MATLAB package

    :return: the name of the input signal; the times associated with the input signal;
    the frequencies produced by the transform; the values of the transform itself; the amplitudes
    of the values of the transform; the powers of the values of the transform; the average amplitudes
    of the transform; and the average powers of the transform.
    """
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
    avg_ampl, avg_pow = avg_ampl_pow(amplitude)

    return (
        time_series.name,
        time_series.times,
        freq,
        transform,
        amplitude,
        power,
        avg_ampl,
        avg_pow,
    )


def avg_ampl_pow(amplitude) -> Tuple[ndarray, ndarray]:
    length = len(amplitude)

    avg_ampl = np.empty(length, dtype=np.float64)
    avg_pow = np.empty(length, dtype=np.float64)

    for i in range(length):
        arr = amplitude[i]
        row = arr[np.isfinite(arr)]

        avg_ampl[i] = np.mean(row)
        avg_pow[i] = np.mean(np.square(row))

    return avg_ampl, avg_pow
