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
import matplotlib.pyplot as plt


def fourier(x, fs):
    L = len(x)
    Y = np.divide(np.fft.fft(x, L), L)
    Y = Y[0:int(L / 2 + 1)]
    P = 2 * np.power(abs(Y), 2)
    f = fs / 2 * np.linspace(0, 1, int(L / 2 + 1))
    return P, f


if __name__ == "__main__":
    fs = 500
    t = np.arange(0, 20, 1 / fs)
    sig = np.sin(2 * np.pi * t) + np.sin(2 * np.pi * t * 6)
    Y, P = fourier(sig, fs)

    plt.plot(P, Y)
    plt.show()
