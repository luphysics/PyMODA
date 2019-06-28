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
import scipy.optimize
import scipy.integrate
from scipy.optimize import fsolve

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


class WindowParams:
    fwtmax = None
    twfmax = None
    C = None
    omg = None
    ompeak = None
    tpeak = None
    xi1 = -np.inf
    xi2 = np.inf
    t1 = -np.inf
    t2 = np.inf

    xi1e = None
    xi2e = None
    xi1h = None
    xi2h = None


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

    wp = WindowParams()

    fwt = []
    twf = []

    if window == gaussian:
        fwt = lambda xi: np.exp(-(f0 ** 2 / 2) * xi ** 2)
        twf = lambda t: 1 / (f0 * np.sqrt(2 * np.pi)) * np.exp(-t ** 2 / (2 * f0 ** 2))
        wp.ompeak = 0
        wp.C = np.pi * twf(0)
        wp.omg = 0
        wp.tpeak = 0
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
            parcalc(rel_to_l, L, wp, fwt, twf, disp_mode)


def parcalc(racc, L, wp, fwt, twf, disp_mode):
    racc = min(racc, 0.5 - 10 ** -10)
    # level0
    ctol = max(racc / 1000, 10 ** -12)  # parameter of numerical accuracy
    MIC = max(10000, 10 * L)  # max interval count

    nt = (1 / (4 * fs)) * np.arange(-8 * L + 1, 8 * L).transpose()  # level1 should be hermitian conjugate?
    nt = nt[wp.t1 < nt][nt < wp.t2]

    nxi = 2 * np.pi * 4 * fs / (16 * L - 1) * np.arange(-8 * L + 1, 8 * L).transpose()
    nxi = nxi[nxi > wp.xi1][nxi < wp.xi2]

    if fwt:
        wp.fwt = fwt
        if not wp.ompeak:
            values = np.abs(fwt(nxi))
            ipeak = values.argmax()  # level2
            wp.ompeak = np.mean(nxi[ipeak])
            wp.ompeak = scipy.optimize.fmin(func=lambda x: -np.abs(fwt(x)), x0=wp.ompeak)  # level1

        if not wp.fwtmax:
            wp.fwtmax = fwt(wp.ompeak)
            if np.isnan(wp.fwtmax):
                wp.twfmax = fwt[wp.ompeak + 10 ** -14]

        if np.abs(wp.ompeak) > 10 ** -12:
            print("Warning")
            fwt = lambda xi: fwt[xi + wp.ompeak]
            if twf:
                twf = lambda t: twf[t] * np.exp(-1 * np.complex(0, -1) * wp.ompeak * t)
            wp.xi1 = wp.xi1 - wp.ompeak
            wp.xi2 = wp.xi2 - wp.ompeak
            wp.fwt = fwt
            wp.ompeak = 0

        vfun = lambda u: fwt(u)
        xp = wp.ompeak
        lim1 = wp.xi1
        lim2 = wp.xi2

        QQ, wflag, xx, ss = sqeps(vfun, xp, lim1, lim2, racc, MIC, np.array([-1, 1]) * 8 * (2 * np.pi * fs))
        wp.xi1e = ss[0, 0]
        wp.x2e = ss[0, 1]
        wp.xi1h = ss[1, 0]
        wp.xi2h = ss[1, 1]

        if wp.C:
            if not twf:  # level0
                wp.C = np.pi * twf(0)
                if np.isnan(wp.C):
                    wp.C = np.pi * twf(10 ** -14)
            else:
                wp.C = (QQ[0, 0] + QQ[0, 1]) / 2

        if wflag == 1 and not disp_mode:
            print("Freq domain window not well behaved")
        if not wp.omg:
            px1 = np.min(wp.ompeak - xx[0, 0], xx[0, 1] - wp.ompeak)
            px2 = np.min(wp.ompeak - xx[3, 0], xx[3, 1] - wp.ompeak)
            # TODO: add this block later

        if not twf:
            # Don't even think about it...
            pass

    if twf:
        wp.twf = twf
        if not wp.tpeak:
            values = np.abs(twf(nt))
            ipeak = values.argmax()  # level2
            wp.tpeak = np.mean(nt[ipeak])
            wp.tpeak = scipy.optimize.fmin(lambda x: -np.abs(twf(x)), wp.tpeak)


def sqeps(vfun, xp, lim1, lim2, racc, MIC, nlims):
    wflag = 0
    ctol = np.max([racc / 1000, 10 ** -12])
    nlim1 = nlims[0]
    nlim2 = nlims[1]

    kk = 1
    shp = 0  # Peak shift

    while np.isnan(vfun(xp + shp) or not np.isfinite(vfun(xp + shp))):
        shp = kk * 10 ** -14
        kk *= -2
    vmax = vfun(xp + shp)

    if np.isfinite(lim1):
        tx1 = lim1 - 0.01 * (lim1 - xp)
        qv1 = np.abs(vfun(tx1) / vmax)
    else:
        qv1 = np.NaN

    if qv1 < 0.5:
        x1h = scipy.optimize.fsolve(func=lambda x: np.abs(vfun(x) / vmax) - 0.5, x0=[xp + shp, tx1])  # level2
    elif np.isnan(qv1):
        x1h = scipy.optimize.fsolve(func=lambda x: np.abs(vfun(xp - np.abs(x)) / vmax) - 0.5, x0=shp)  # level2
        x1h = xp - np.abs(x1h)
    else:
        x1h = xp + (lim1 - xp) / 100

    if np.isfinite(lim2):
        tx2 = lim2 - 0.01 * (lim2 - xp)
        qv2 = np.abs(vfun(tx2) / vmax)
    else:
        qv2 = np.NaN
    if qv2 < 0.5:
        x2h = scipy.optimize.fsolve(func=lambda u: np.abs(vfun(u) / vmax) - 0.5, x0=[xp + shp, tx2])
    elif np.isnan(qv2):
        x2h = scipy.optimize.fsolve(func=lambda u: np.abs(vfun(xp + np.abs(u)) / vmax) - 0.5, x0=shp)
        x2h = xp + np.abs(x2h)
    else:
        x2h = xp + (lim2 - xp) / 100

    if np.isnan(x1h):
        x1h = scipy.optimize.fsolve(func=lambda u: np.abs(np.abs(vfun(xp - np.abs(u)) / vmax) - 0.5, x0=shp))
        x1h = xp - np.abs(x1h) / 100
    if np.isnan(x2h):
        x2h = scipy.optimize.fmin(func=lambda u: np.abs(np.abs(vfun(xp + np.abs(u)) / vmax) - 0.5), x0=shp)
        x2h = xp + np.abs(x2h) / 100

    if np.isfinite(lim1):
        tx1 = lim1 - 0.01 * (lim1 - xp)
        qv1 = (np.abs(vfun(tx1)) + np.abs(vfun((tx1 + lim1) / 2)) + np.abs(vfun((tx1 + 3 * lim1) / 4))) / np.abs(vmax)
    else:
        qv1 = np.NaN

    if qv1 < 10 ** (-8) / 3:
        x1e = scipy.optimize.fsolve(
            func=lambda u: np.abs(vfun(u) / vmax) + np.abs(vfun((u + lim1) / 2) / vmax) + np.abs(
                vfun((u + 3 * lim1) / 4) / vmax) - 10 ^ (-8), x0=[xp + shp, tx1])
    elif np.isnan(qv1):
        x1e = scipy.optimize.fsolve(
            lambda u: np.abs(vfun(xp - np.abs(u)) / vmax) + np.abs(vfun(xp - np.sqrt(3) * np.abs(u)) / vmax) +
                      np.abs(vfun(xp - np.sqrt(5) * np.abs(u)) / vmax) - 10 ^ (-8), x0=shp)

        x1e = xp - np.abs(x1e)

    else:
        x1e = xp + (lim1 - xp) / 2

    if np.isfinite(lim2):
        tx2 = lim2 - 0.01 * (lim2 - xp);
        qv2 = (abs(vfun(tx2)) + abs(vfun((tx2 + lim2) / 2)) + abs(vfun((tx2 + 3 * lim2) / 4))) / abs(vmax)
    else:
        qv2 = np.NaN

    if qv2 < 10 ^ (-8):
        x2e = scipy.optimize.fsolve(
            func=lambda u: np.abs(vfun(u) / vmax) + np.abs(vfun((u + lim2) / 2) / vmax) + np.abs(
                vfun((u + 3 * lim2) / 4) / vmax) - 10 ^ (-8), x0=[xp + shp, tx2])
    elif np.isnan(qv2):
        x2e = scipy.optimize.fsolve(
            func=lambda u: abs(vfun(xp + abs(u)) / vmax) + abs(vfun(xp + np.sqrt(3) * abs(u)) / vmax) + abs(
                vfun(xp + np.sqrt(5) * np.abs(u)) / vmax) - 10 ** (-8), x0=shp)

        x2e = xp + abs(x2e)

    else:
        x2e = xp + (lim2 - xp) / 2

    if np.isnan(x1e):
        x1e = scipy.optimize.fmin(func=lambda u: abs(abs(vfun(x1h - abs(u)) / vmax) - 10 ^ (-8)), x0=0)
        x1e = x1h - abs(x1e)
        lim1 = x1e
        wflag = 1
    if np.isnan(x2e):
        x2e = scipy.optimize.fmin(func=lambda u: abs(abs(vfun(x2h + abs(u)) / vmax) - 10 ^ (-8)), x0=0)
        x2e = x2h + abs(x2e)
        lim2 = x2e
        wflag = 1

    # Integrate given function to find Q1 and Q2.
    Q1 = 0  # line1003
    Q2 = 0

    qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x1e, MIC, 0, 0.1 * ctol)

    x1m = x1e
    q1m = qv

    if abs(eb / (Q1 + qv)) > ctol:
        wflag = 1
        qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x1e, MIC, 0, 0.1 * ctol)
        qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x1e, MIC, 0.1 * abs(ctol * (Q1 + qv)), 0)
        x1m = x1h
        q1m = qv
        if abs(eb / (Q1 + qv)) <= ctol:
            while True:
                qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, max([xp + (x1m - xp) * 2, x1e]), MIC, 0, 0.1 * ctol)
                qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, max([xp + (x1m - xp) * 2, x1e]), MIC,
                                                       0.1 * abs(ctol * (Q1 + qv)), 0)
                if abs(eb / (Q1 + qv)) > ctol:
                    break
                x1m = max([xp + (x1m - xp) * 2, x1e])
                q1m = qv
        else:
            while abs(eb / (Q1 + qv)) > ctol:
                x1m = xp + (x1m - xp) / 2
                qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x1m, MIC, 0, 0.1 * ctol)
                qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x1m, MIC, 0.1 * abs(ctol * (Q1 + qv)), 0)
                q1m = qv
        qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x1e, MIC, 0.1 * abs(ctol * (Q1 + qv)), 0)
        if abs(eb) < 0.5 * abs(qv):
            Q1 = Q1 + qv

    Q1 = Q1 + q1m
    if wflag == 0:
        qv, eb, _, _, _ = scipy.integrate.quad(vfun, x1e, lim1, MIC, 0.1 * abs(ctol * Q1), 0)
        if not np.isfinite(lim1) and np.isnan(qv):
            lim1 = x1e
            while not np.isnan(vfun(2 * lim1)):
                lim1 = 2 * lim1
            qv, eb, _, _, _ = scipy.integrate.quad(vfun, x1e, lim1, MIC, 0.1 * abs(ctol * Q1), 0)
        if abs(eb / Q1) > ctol:
            wflag = 1
            qv, eb, _, _, _ = scipy.integrate.quad(vfun, x1e, max([min([8 * x1e, nlim1]), lim1]), MIC,
                                                   0.1 * abs(ctol * Q1), 0)
        if abs(eb) < 0.5 * abs(qv):
            Q1 = Q1 + qv

    Q1 = -Q1
    qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x2e, MIC, 0, 0.1 * ctol)
    qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x2e, MIC, 0.1 * abs(ctol * (Q2 + qv)), 0)
    x2m = x2e
    q2m = qv
    if abs(eb / (Q2 + qv)) > ctol:
        wflag = 1
        qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x2e, MIC, 0, 0.1 * ctol)
        qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x2e, MIC, 0.1 * abs(ctol * (Q2 + qv)), 0)

        x2m = x2h
        q2m = qv
        if abs(eb / (Q2 + qv)) <= ctol:
            while True:
                qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, min([xp + (x2m - xp) * 2, x2e]), MIC, 0, 0.1 * ctol)
                qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, min([xp + (x2m - xp) * 2, x2e]), MIC,
                                                       0.1 * abs(ctol * (Q2 + qv)), 0)
                if abs(eb / (Q2 + qv)) > ctol:
                    break
                x2m = min([xp + (x2m - xp) * 2, x2e])
                q2m = qv

        else:
            while abs(eb / (Q2 + qv)) > ctol:
                x2m = xp + (x2m - xp) / 2
                qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x2m, MIC, 0, 0.1 * ctol)
                qv, eb, _, _, _ = scipy.integrate.quad(vfun, xp, x2m, MIC, 0.1 * abs(ctol * (Q2 + qv)), 0)
                q2m = qv
        qv, eb, _, _, _ = scipy.integrate.quad(vfun, x2m, x2e, MIC, 0.1 * abs(ctol * (Q2 + qv)), 0)
        if abs(eb) < 0.5 * abs(qv):
            Q2 += qv

    Q2 += q2m
    if wflag == 0:
        qv, eb, _, _, _ = scipy.integrate.quad(vfun, x2e, lim2, MIC, 0.1 * abs(ctol * Q2), 0)
        if not np.isfinite(lim2) and np.isnan(qv):
            lim2 = x2e
            while not np.isnan(vfun(2 * lim2)):
                lim2 = 2 * lim2
            qv, eb, _, _, _ = scipy.integrate.quad(vfun, x2e, lim2, MIC, 0.1 * abs(ctol * Q2), 0)
        if abs(eb / Q2) > ctol:
            wflag = 1
            qv, eb, _, _, _ = scipy.integrate.quad(vfun, x2e, min([max([8 * x2e, nlim2]), lim2]), MIC,
                                                   0.1 * abs(ctol * Q2), 0)
        if abs(eb) < 0.5 * abs(qv):
            Q2 = Q2 + qv

    QQ = np.asarray([Q1, Q2], [-q1m, q2m])
    xx = np.asarray([x1e, x2e],
                    [x1h, x2h],
                    [x1m, x2m],
                    [lim1, lim2])

    Q = Q1 + Q2

    def fz(zv):
        if zv < abs(Q1 / Q):
            cx1 = x1m
            cq1 = Q1 + q1m
            ra = np.exp(-1 / 2)
            rb = np.exp(1 / 2)
        else:
            cx1 = x2m
            cq1 = Q1 + q2m
            ra = np.exp(1 / 2)
            rb = np.exp(-1 / 2)

        if abs(1 - abs((Q - cq1) / Q)) < zv:
            while True:
                nx = xp + ra * (cx1 - xp)
                if nx < lim1: nx = (cx1 + lim1) / 2
                if nx > lim2: nx = (cx1 + lim2) / 2
                [pv, _] = scipy.integrate.quad(vfun, cx1, nx, MIC, 0.1 * abs(ctol * Q), 0)
                if abs(1 - abs((Q - cq1 - pv) / Q)) >= zv:
                    cx2 = nx
                    cq2 = cq1 + pv
                    break
                cx1 = nx
                cq1 = cq1 + pv
        else:
            while True:
                nx = xp + rb * (cx1 - xp)
                if nx < lim1: nx = (cx1 + lim1) / 2
                if nx > lim2: nx = (cx1 + lim2) / 2
                [pv, _] = scipy.integrate.quad(vfun, cx1, nx, MIC, 0.1 * abs(ctol * Q), 0)
                if abs(1 - abs((Q - cq1 - pv) / Q)) >= zv:
                    cx2 = nx
                    cq2 = cq1 + pv
                    break
                cx1 = nx
                cq1 = cq1 + pv

        [pv, _] = scipy.integrate.quad(vfun, cx1, (cx1 + cx2) / 2, MIC, 0.1 * abs(ctol * Q), 0)
        qfun = lambda x: 1 - abs((Q - (cq1 + pv +
                                       scipy.integrate.quad(vfun, (cx1 + cx2) / 2, x, MIC, 0.1 * abs(ctol * Q), 0)[0])
                                  ) / Q)
        x0 = scipy.optimize.fsolve(lambda x: abs(qfun(x)) - zv, x0=[cx1, cx2])
        return x0

    s1e = fz(racc / 2)
    s2e = fz(1 - racc / 2)
    s1h = fz(0.5 / 2)
    s2h = fz(1 - 0.5 / 2)
    ss = np.asarray([s1e, s2e],
                    [s1h, s2h])

    return QQ, wflag, xx, ss


if __name__ == "__main__":
    """Test the function if this file is run directly."""
    signal = np.arange(0, 100, 0.1)
    fs = 100

    wft(signal, fs)
