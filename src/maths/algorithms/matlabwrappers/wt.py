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
from typing import Union, Tuple, Dict

from numpy import ndarray

from maths.params.TFParams import TFParams
from maths.signals.TimeSeries import TimeSeries


def calculate(
    signal: Union[TimeSeries, ndarray], params: TFParams, return_opt: bool = False
) -> Union[Tuple[ndarray, ndarray], Tuple[ndarray, ndarray, Dict]]:
    """
    Calculates the wavelet transform using the MATLAB-packaged function.

    :param signal: the signal to perform the transform on
    :param params: the params object containing parameters to pass to the MATLAB function
    :param return_opt: whether to return a 3rd value, the options used to calculate the wavelet transform ('wopt' in the MATLAB function)
    :return: [2D array] the wavelet transform; [1D array] the frequencies
    """
    import WT
    import matlab

    package = WT.initialize()

    if isinstance(signal, TimeSeries):
        signal = signal.signal

    kwargs = {**params.get(), "python": True}

    wt, frequency, opt = package.wt(
        matlab.double([signal.tolist()]), params.fs, kwargs, nargout=3
    )

    ### Uncomment next line to test the pure Python version of the wavelet transform. ###
    # wt, frequency = wavelet_transform.wt(signal, params.fs , LognormWavelet(f0=params.fs))

    if not return_opt:
        return wt, frequency

    return wt, frequency, opt
