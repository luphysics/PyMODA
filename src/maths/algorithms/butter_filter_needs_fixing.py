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
from scipy import signal


# x - time series
# n - order of filter
# flp - lowpass corner frequency of filter
# fhi - hipass corner frequency
# fs - sampling frequency
# d - zero phase filter data

import numpy as np
import matplotlib.pyplot as plt


def butterworth(x, n, flp, fhi, fs):
    fnq = 1 / 2 * fs  # nyquist frequency

    Wn = np.array([flp/fnq, fhi/fnq])  # cutoff frequency
    w = Wn.tolist()

    # b, a, _ = signal.butter(n, Wn)  # filter coefficients

    d = signal.filtfilt(b, a, x)  # filtered signal
    return d


flp = 10
fhi = 20
fnq = 100

Wn = np.array([flp/fnq, fhi/fnq])
w = Wn.tolist()

print(type(w))

# if __name__ == "__main__":
#     t = np.linspace(0, 1, 1000, False)  # 1 second
#     sig = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 20 * t)
#     b = butterworth(sig, 4, 5, 15, 1000)
#     plt.plot(t, b)
#     plt.show()
