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


from maths.params.TFParams import TFParams, _f0, _fmin
from maths.signals.TimeSeries import TimeSeries


def calculate(time_series: TimeSeries, params: TFParams):
    """
    Calculates the windowed Fourier transform using the MATLAB-packaged function.

    :param time_series: the signal to perform the transform on
    :param params: the params object containing parameters to pass to the MATLAB function
    :return: [2D array] the windowed Fourier transform; [1D array] the frequencies
    """

    import WFT
    import matlab

    package = WFT.initialize()

    signal_matlab = matlab.double([time_series.signal.tolist()])

    """
    The value passed for 'f0' should actually be that of 'fr' in the case
    of WFT. In the Matlab version this is handled before passing the value 
    to the function, so we'll do the same.
    
    When the value has been left blank, there is no problem because this
    case is handled by the Matlab function.
    """
    params_dict = params.get()

    f0 = params_dict.get(_f0)
    fmin = params_dict.get(_fmin)

    if f0 is not None and fmin is not None and fmin != 0:
        params_dict[_f0] = f0 / fmin

    wft, frequency = package.transform(signal_matlab, params.fs, params_dict, nargout=2)

    return wft, frequency
