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

# Names of window parameters.
import scipy

fwtmax = "fwtmax"
twfmax = "twfmax"
C = "C"
omg = "omg"
xi1 = "xi1"
xi2 = "xi2"
ompeak = "ompeak"
t1 = "t1"
t2 = "t2"
tpeak = "tpeak"

gaussian = "Gaussian"
hann = "Hann"
blackman = "Blackman"
exp = "exp"
rect = "rect"
kaiser = "kaiser"


def wft(signal,
        fs,
        on_error=lambda x: print(f"ERROR: {x}"),
        on_warning=lambda x: print(f"Warning: {x}"),
        window="Gaussian",
        f0=1,
        fmin=0,
        fmax=None,
        fstep="auto",
        padmode="predictive",
        rel_to_l=0.01,
        preprocess=True,
        disp_mode=True,
        plot_mode=False,
        cut_edges=False):
    fmax = fmax or fs / 2
    L = len(signal)

    if fs <= 0 or not fs:
        on_error("Sampling frequency should be a positive finite number")

    rec_flag = 1  # What is this for?
    window_params = {}

    if rec_flag == 1:
        window_params = {
            fwtmax: [],
            twfmax: [],
            C: [],
            omg: [],
            xi1: -np.inf,
            xi2: np.inf,
            t1: -np.inf,
            t2: np.inf,
            ompeak: [],
            tpeak: [],
        }

    fwt = []
    twf = []

    if window == gaussian:
        fwt = lambda xi: np.exp(-(f0 ** 2 / 2) * xi ** 2)
        twf = lambda t: 1 / (f0 * np.sqrt(2 * np.pi)) * np.exp(-t ** 2 / (2 * f0 ** 2))
        window_params[ompeak] = 0
        window_params[C] = np.pi * twf(0)
        window_params[omg] = 0
        window_params[tpeak] = 0
    # Implement these later!
    elif window == hann:
        pass
    elif window == blackman:
        pass
    elif window == exp:
        pass
    elif window == rect:
        pass
    elif kaiser in window:
        pass
    else:
        on_error(f"Invalid window name: {window}")

    if rec_flag == 1:
        if disp_mode:
            print("Estimating window parameters.")
            parcalc(rel_to_l, L, window_params, fwt, twf)


def parcalc(racc, L, wp, fwt, twf):
    racc = min(racc, 0.5 - 10 ** -10)
    # level0
    ctol = max(racc / 1000, 10 ** -12)  # parameter of numerical accuracy
    MIC = max(10000, 10 * L)  # max interval count

    nt = (1 / (4 * fs)) * np.arange(-8 * L + 1, 8 * L).transpose()
    nt = nt[wp[t1] < nt][nt < wp[t2]]

    nxi = 2 * np.pi * 4 * fs / (16 * L - 1) * np.arange(-8 * L + 1, 8 * L).transpose()
    nxi = nxi[nxi > wp[xi1]][nxi < wp[xi2]]

    if fwt:
        wp[fwt] = fwt
        if not wp[ompeak]:
            ipeak = indices(fwt, lambda x: np.abs(x[nxi]) == max(np.abs(x[nxi])))
            wp[ompeak] = np.mean(nxi[ipeak])
            wp[ompeak] = scipy.optimize.fmin(func=lambda x: -np.abs(fwt[x]), x0=wp[ompeak])  # level1

        if not wp[fwtmax]:
            wp[fwtmax] = fwt[wp[ompeak]]
            if np.isnan(wp[fwtmax]):
                wp[twfmax] = fwt[wp[ompeak] + 10 ** -14]

        if np.abs(wp[ompeak]) > 10 ** -12:
            print("Warning")
            fwt = lambda xi: fwt[xi + wp[ompeak]]
            if twf:
                twf = lambda t: twf[t] * np.exp(-1 * np.complex(0, -1) * wp[ompeak] * t)
            wp[xi1] = wp[xi1] - wp[ompeak]
            wp[xi2] = wp[xi2] - wp[ompeak]
            wp[fwt] = fwt
            wp[ompeak] = 0

        vfun = lambda u: fwt(u)
        xp = wp[ompeak]
        lim1 = wp[xi1]
        lim2 = wp[xi2]

        QQ, wflag, xx, ss = sqeps(vfun,xp, lim1, lim2,racc,MIC, np.array(-1,1) * 8*(2*np.pi*fs))


def sqeps(vfun, xp, lims, racc, MIC, nlims):
    pass


def indices(array, function):
    return [i for (i, val) in enumerate(array) if function(val)]


if __name__ == "__main__":
    """Test the function if this file is run directly."""
    signal = np.arange(0, 100, 0.1)
    fs = 100

    wft(signal, fs)
