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
from scipy.sparse.linalg.isolve.lsqr import eps

from maths.algorithms.matlab_utils import isempty, backslash, twopi

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


def fcast(sig, fs, NP, fint, **kwargs):  # line1145
    MaxOrder = len(sig)
    if len(kwargs) > 3:
        MaxOrder = kwargs.get("maxorder") or MaxOrder
    w = []
    if len(kwargs) > 4:
        w = kwargs.get("w") or w
    rw = np.sqrt(w)
    # ignore DispMode

    WTol = 10 ** -8  # tolerance for cutting weighting.
    Y = sig[:]
    if not isempty(rw):
        Y = rw * Y

    L = 200  # TODO: add this. line1153
    T = L / fs
    t = np.arange(0, L - 2) / fs

    w = w[-L:]  # level3
    rw = rw[-L:]  # level3
    Y = Y[-L:]  # level3

    MaxOrder = min([MaxOrder, np.floor(L / 3)])

    FTol = 1 / T / 100
    rr = (1 + np.sqrt(5)) / 2
    Nq = np.ceil((L + 1) / 2)
    ftfr = [np.arange(0, Nq), -np.fliplr(np.arange(1, L - Nq + 1))] * fs / L
    orstd = np.std(Y)

    v = np.zeros(L, 1)
    ic = v
    frq = v
    amp = v
    phi = v
    itn = 0

    # Skipped if DispMode

    while itn < MaxOrder:
        itn += 1
        aftsig = abs(np.fft.fft(Y))
        _, imax = max(aftsig[2:Nq])
        imax += 1

        # Forward search
        nf = ftfr[imax]
        FM = np.asarray(np.ones(L, 1), np.cos(2 * np.pi * nf * t), np.sin(2 * np.pi * nf * t))
        if not isempty(rw):
            FM = FM * (rw * np.ones(1, 3))
        nb = np.linalg.lstsq(FM, Y)  # level3
        nerr = np.std(Y - FM * nb)

        df = FTol
        perr = np.inf
        while nerr < perr:
            if abs(nf - fs / 2 + FTol) < eps:  # level3 eps
                break
            pf = nf
            perr = nerr
            pb = nb
            nf = min([pf + df, fs / 2 - FTol])
            FM = [np.ones(L, 1), np.cos(2 * np.pi * nf * t), np.sin(2 * np.pi * nf * t)]
            if ~isempty(rw):
                FM = FM * (rw * np.ones(1, 3))
            nb = np.linalg.lstsq(FM, Y)
            nerr = np.std(Y - FM * nb)
            df = df * rr

        # Use golden section search to find exact minimum
        if nerr < perr:
            cf = [nf, nf, nf]
            cerr = [nerr, nerr, nerr]
            cb = [nb, nb, nb]

        elif abs(nf - pf - FTol) < eps:
            cf = [pf, pf, pf]
            cerr = [perr, perr, perr]
            cb = [pb, pb, pb]

        else:
            cf = [0, pf, nf]
            cerr = [0, perr, nerr]
            cb = [np.zeros(len(pb), 1), pb, nb]
            cf[1] = pf - df / rr / rr
            FM = [np.ones(L, 1), np.cos(2 * np.pi * cf[1] * t), np.sin(2 * np.pi * cf[1] * t)]
            if not isempty(rw):
                FM = FM * (rw * np.ones(1, 3))
            cb[1] = np.linalg.lstsq(FM, Y)  # level3
            cerr[1] = np.std(Y - FM * cb[1])

        while (cf[2] - cf[1] > FTol and cf[3] - cf[2] > FTol):
            tf = cf[1] + cf[3] - cf[2]
            FM = [np.ones(L, 1), np.cos(2 * np.pi * tf * t), np.sin(2 * np.pi * tf * t)]
            if not isempty(rw):
                FM = FM * (rw * np.ones(1, 3))
            tb = np.linalg.lstsq(FM, Y)
            terr = np.std(Y - FM * tb)

            if terr < cerr[2] and tf < cf[2]:  # TODO: fix all indices
                cf = [cf(1), tf, cf(2)]
                cerr = [cerr(1), terr, cerr(2)]
                cb = [cb[1], tb[:], cb[:2]]
            if terr < cerr[2] and tf > cf[2]:
                cf = [cf[2], tf, cf[3]]
                cerr = [cerr[2], terr, cerr[3]]
                cb = [cb[2], tb[:], cb[:3]]
            if terr > cerr[2] and tf < cf[2]:
                cf = [tf, cf(2), cf(3)]
                cerr = [terr, cerr[2], cerr[3]]
                cb = [tb[:], cb[2], cb[3]]
            if terr > cerr[2] and tf > cf[2]:
                cf = [cf[1], cf[2], tf]
                cerr = [cerr[1], cerr[2], terr]
                cb = [cb[1], cb[2], tb[:]]

        # Forward values.
        fcf = cf[1]
        fcb = cb[1]  # level2
        fcerr = cerr[1]

        # Backward search

        vf = ftfr[imax]
        FM = [np.ones(L, 1), np.cos(twopi * nf * t), np.sin(twopi * nf * t)]
        if not isempty(rw):
            FM = FM * np.ones(1, 3)

        nb = backslash(FM, Y)
        nerr = np.std(Y - FM * nb)

        df = FTol
        perr = np.inf
        while nerr < perr:
            if abs(nf - FTol) < eps:
                break
            pf = nf
            perr = nerr
            pb = nb
            nf = max([pf - df, FTol])
            FM = [np.ones(L, 1), np.cos(twopi * nf * t), np.sin(twopi * nf * t)]
            if not isempty(rw):
                FM = FM * np.ones(1, 3)
            nb = backslash(FM, Y)
            nerr = np.std(Y - FM * nb)
            df = df * rr

        # TODO: fix repeating code
        # Use golden section search to find exact minimum
        if nerr < perr:
            cf = [nf, nf, nf]
            cerr = [nerr, nerr, nerr]
            cb = [nb, nb, nb]

        elif abs(nf - pf - FTol) < eps:
            cf = [pf, pf, pf]
            cerr = [perr, perr, perr]
            cb = [pb, pb, pb]

        else:
            cf = [0, pf, nf]
            cerr = [0, perr, nerr]
            cb = [np.zeros(len(pb), 1), pb, nb]
            cf[1] = pf - df / rr / rr
            FM = [np.ones(L, 1), np.cos(2 * np.pi * cf[1] * t), np.sin(2 * np.pi * cf[1] * t)]
            if not isempty(rw):
                FM = FM * (rw * np.ones(1, 3))
            cb[1] = np.linalg.lstsq(FM, Y)  # level3
            cerr[1] = np.std(Y - FM * cb[1])

        while (cf[2] - cf[1] > FTol and cf[3] - cf[2] > FTol):
            tf = cf[1] + cf[3] - cf[2]
            FM = [np.ones(L, 1), np.cos(2 * np.pi * tf * t), np.sin(2 * np.pi * tf * t)]
            if not isempty(rw):
                FM = FM * (rw * np.ones(1, 3))
            tb = np.linalg.lstsq(FM, Y)
            terr = np.std(Y - FM * tb)

            if terr < cerr[2] and tf < cf[2]:  # TODO: fix all indices
                cf = [cf(1), tf, cf(2)]
                cerr = [cerr(1), terr, cerr(2)]
                cb = [cb[1], tb[:], cb[:2]]
            if terr < cerr[2] and tf > cf[2]:
                cf = [cf[2], tf, cf[3]]
                cerr = [cerr[2], terr, cerr[3]]
                cb = [cb[2], tb[:], cb[:3]]
            if terr > cerr[2] and tf < cf[2]:
                cf = [tf, cf(2), cf(3)]
                cerr = [terr, cerr[2], cerr[3]]
                cb = [tb[:], cb[2], cb[3]]
            if terr > cerr[2] and tf > cf[2]:
                cf = [cf[1], cf[2], tf]
                cerr = [cerr[1], cerr[2], terr]
                cb = [cb[1], cb[2], tb[:]]
        bcf = cf[2]
        bcb = cb[2]
        bcerr = cerr[2]

        # Assign values and subtract
        if fcerr < bcerr:
            cf = fcf
            cb = fcb
            cerr = fcerr
        else:
            cf = bcf
            cb = bcb
            cerr = bcerr

        frq[itn + 1] = cf
        amp[itn + 1] = np.sqrt(cb(2) ^ 2 + cb(3) ^ 2)
        phi[itn + 1] = np.atan2(-cb(3), cb(2))
        amp[1] = amp[0] + cb[0]
        v[itn] = cerr

        FM = [np.ones(L, 1), np.cos(twopi * nf * t), np.sin(twopi * nf * t)]
        if not isempty(rw):
            FM = FM * (rw * np.ones(1, 3))
            Y -= FM * cb

        CK = 3 * itn + 1
        cic = L * np.log(cerr) + CK * np.log(L)

        ic[itn] = cic
        if v[itn] / orstd < 2 * eps:
            break
        if itn > 2 and cic > ic[itn - 1] and ic[itn - 1] > ic[itn - 2]:
            break

        frq = frq[1:itn + 1]
        amp = amp[1:itn + 1]
        phi = phi[1:itn + 1]
        v = v[1:itn]
        ic = ic[1:itn]

        fsig = np.zeros(NP, 1)
        nt = (np.arange(T, T + (NP - 1), 1 / fs) / fs).transpose()

        if np.size(sig, 2) > np.size(sig, 1):
            fsig = fsig.transpose()
            nt = nt.transpose()
        for k in range(1, len(frq)):
            if frq[k] > fint(1) and frq(k) < fint(2):
                fsig = fsig + amp(k) * np.cos(twopi * frq(k) * nt + phi(k))
            else:
                fsig = fsig + amp(k) * np.cos(twopi * frq(k) * (T - 1 / fs) + phi(k))

        return fsig


def aminterp(X, Y, Z, XI, YI, method):
    ZI = np.zeros(np.size(Z, 1), len(XI)) * np.NaN
    xstep = np.mean(np.diff(XI))
    xind = 1 + np.floor((1 / 2) + (X - XI(1)) / xstep)
    xpnt = np.asarray([0], [0], [0])  # level3 TODO: add later

    if method == "max":
        for xn in range(1, len(xpnt)):
            xid1 = xpnt[xn - 1] + 1
            xid2 = xpnt[xn]
            ZI[xind[xid1]] = np.max(Z[xid1:xid2], 2)
    else:
        for xn in range(1, len(xpnt)):
            xid1 = xpnt[xn - 1] + 1
            xid2 = xpnt[xn + 1]
            ZI[xind[xid1]] = np.mean(Z[xid1:xid2], 2)
    Z = ZI

    ZI = np.zeros(len(YI), np.size(Z, 2)) * np.NaN
    ystep = np.mean(np.diff(YI))
    yind = 1 + np.floor((1 / 2) + (Y - YI(1)) / ystep)
    ypnt = [[0], [0], [0]]  # level3 TODO: add later

    if method == "max":
        for yn in range(1, len(ypnt)):
            yid1 = ypnt[yn - 1] + 1
            yid2 = ypnt[yn]
            ZI[yind[yid1]] = np.max(Z[yid1:yid2], 2)
    else:
        for yn in range(1, len(ypnt)):
            yid1 = xpnt[yn - 1] + 1
            yid2 = xpnt[yn + 1]
            ZI[yind[yid1]] = np.mean(Z[yid1:yid2], 2)

    return ZI


if __name__ == "__main__":
    """Test the function if this file is run directly."""
    signal = np.arange(0, 100, 0.1)
    fs = 100

    wft(signal, fs)
