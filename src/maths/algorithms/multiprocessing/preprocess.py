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
from numpy import ndarray

from maths.algorithms import preprocessing
from processes.mp_utils import process


@process
def _preprocess(sig: ndarray, fs: float, fmin: float, fmax: float) -> ndarray:
    """
    Performs preprocessing on a signal

    :param queue: the queue to put the output in
    :param sig: the signal as a 1D array
    :param fs: the sampling frequency
    :param fmin: the minimum frequency
    :param fmax: the maximum frequency
    """
    return preprocessing.preprocess(sig, fs, fmin, fmax)
