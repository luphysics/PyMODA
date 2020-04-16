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

from typing import Tuple, Union, Dict

import numpy as np
import pymodalib
from numpy import ndarray
from pymodalib.utils.matlab import multi_matlab_to_numpy

from maths.params.TFParams import TFParams, _wft
from maths.signals.TimeSeries import TimeSeries
from processes.mp_utils import process
from utils import args


@process
def _time_frequency(
    time_series: TimeSeries, params: TFParams, return_opt: bool = False
) -> Union[
    Tuple[str, ndarray, ndarray, ndarray, ndarray, ndarray, ndarray, ndarray],
    Tuple[str, ndarray, ndarray, ndarray, ndarray, ndarray, ndarray, ndarray, Dict],
]:
    """
    Performs a wavelet transform or windowed Fourier transform using the MATLAB-packaged libraries.

    :param time_series: the signal to transform
    :param params: the input parameters for the MATLAB package
    :param return_opt: whether to return the options from the transform function

    :return: the name of the input signal; the times associated with the input signal;
    the frequencies produced by the transform; the values of the transform itself; the amplitudes
    of the values of the transform; the powers of the values of the transform; the average amplitudes
    of the transform; and the average powers of the transform.
    """
    wavelet = not params.transform == _wft

    if not wavelet:
        return_opt = False

    if wavelet:
        transform, freq, opt = _wt_func(time_series.signal, params, return_opt)
    else:
        transform, freq = _wft_func(time_series, params)
        opt = {}

    amplitude = np.abs(transform)
    power = np.square(amplitude)
    avg_ampl, avg_pow = avg_ampl_pow(amplitude)

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

    if return_opt:
        return out + (opt,)

    return out


def _wt_func(signal: ndarray, params: TFParams, return_opt: bool):
    args.init()
    impl = "matlab" if not args.python_wt() else "python"

    result = pymodalib.wavelet_transform(
        signal=signal,
        fs=params.fs,
        fmin=params.get_item("fmin"),
        fmax=params.get_item("fmax"),
        resolution=params.get_item("f0"),
        cut_edges=params.get_item("CutEdges"),
        wavelet=params.get_item("Wavelet"),
        padding=params.get_item("Padding"),
        preprocess=params.get_item("Preprocess"),
        rel_tolerance=params.get_item("RelTol"),
        return_opt=return_opt,
        implementation=impl,
    )

    try:
        wt, freq, opt = result
    except ValueError:
        wt, freq = result
        opt = {}

    return wt, freq, opt


def _wft_func(signal, params):
    # Don't move the import statement.
    from maths.algorithms.matlabwrappers import wft

    transform, freq = wft.calculate(signal, params)
    return multi_matlab_to_numpy(transform, freq)


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
