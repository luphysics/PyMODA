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
from scipy.signal import hilbert

from maths.algorithms.loop_butter import loop_butter
from maths.signals.TimeSeries import TimeSeries


def _bandpass_filter(queue, time_series: TimeSeries, fmin, fmax, fs):
    bands, _ = loop_butter(time_series.signal, fmin, fmax, fs)
    h = hilbert(bands)

    phase = np.angle(h)
    amp = np.abs(h)

    queue.put((
        time_series.name,
        bands,
        phase,
        amp,
        (fmin, fmax),
    ))
