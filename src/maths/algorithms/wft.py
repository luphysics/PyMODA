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

from maths.algorithms.matlab_utils import isempty, backslash, twopi, nextpow2, isnan, find, quadgk

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
    # TODO: Implement these later!
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

    coib1 = np.ceil(abs(wp.t1e * fs))
    coib2 = np.ceil(abs(wp.t2e * fs))

    if wp.t2e - wp.t1e > L / fs:
        print("No WFT coefficients in cone of influence")
        cut_edges = False

    fstepsim = fstep
    wp.fstep = fstep
    if fstep == "auto":
        Nb = 10
        wp.fstep = (wp.xi2h - wp.xi1h) / (twopi * Nb)
        c10 = np.floor(np.log10(wp.fstep))
        fdig = np.floor(wp.fstep / 10 ** c10)
        fstep = np.floor(wp.fstep / 10 ** c10) * 10 ** c10

    freq = (np.ceil(fmin / fstep) * np.arange(fstep, np.floor(fmax / fstep) * fstep, fstep)).transpose()
    SN = len(freq)

    """Skipped some code (mostly unnecessary?)"""

    if preprocess:
        X = np.arange(1, len(signal) + 1).transpose() / fs
        XM = np.ones((len(X), len(X)), dtype=np.float64)
        for pn in range(1, 4):
            CX = X ** pn
            XM[pn] = (CX - np.mean(CX)) / np.std(CX)
            signal -= XM * (np.linalg.pinv(XM) * signal)

            fx = np.fft.fft(signal, L)
            Nq = np.ceil((L + 1) / 2)
            ff = np.asarray(
                np.arange(0, Nq),
                -np.fliplr(np.arange(1, L - Nq + 1))

            ) * fs / L
            # Filter signal
            fx[find(ff, lambda i: np.abs(i) <= max(fmin, fs / L))] = 0
            fx[find(ff, lambda i: abs(i) >= fmax)] = 0
            signal = np.fft.ifft(fx)

    NL = 2 * nextpow2(L + coib1[0] + coib2[0])
    if coib1[0] == 0 and coib2[0] == 0:
        n1 = np.floor((NL - L) / 2)
        n2 = np.ceil((NL - L) / 2)
    else:
        n1 = np.floor((NL - L) * coib1[0] / (coib1[0] + coib2[0]))
        n1 = np.ceil((NL - L) * coib1[0] / (coib1[0] + coib2[0]))

    # Windowed Fourier Transform by itself
    WFT = np.zeros(SN, L) * np.NaN
    ouflag = 0
    if wp.t2e - wp.t1e > L / fs:
        coib1 = 0
        coib2 = 0

    for sn in range(0, SN):
        freqwf = freq[sn] - ff  # TODO: add later
        ii = find(freqwf, lambda i: wp.xi1 / twopi < i < wp.xi2 / twopi)

        if not isempty(fwt):
            fw = fwt(twopi * freqwf[ii])
            nid = find(fw, lambda x: isnan(x) or not np.isfinite(x))
            if not isempty(nid):
                fw[nid] = fwt(twopi * freqwf[ii[nid]] + 10 ** -14)
                nid = find(fw, lambda x: isnan(x) or not np.isfinite(x))
                fw[nid] = 0
                if not isempty(nid):
                    ouflag = 1
                    ouval = twopi * freqwf(nid[0])

        else:
            timewf = 1 / fs * np.asarray(-np.arange(1, np.ceil((NL - 1) / 2)),
                                         np.arange(NL + 1 - (np.ceil((NL - 1) / 2) + 1, NL)))
            jj = None  # TODO
            tw = np.zeros(NL, 1)
            tw[jj] = twf(timewf(jj)) * np.exp(np.complex(0, -1 * twopi * freq[sn] * timewf[jj]))
            nid = find(fw, lambda x: isnan(x) or not np.isfinite(x))
            if not isempty(nid):
                tw[nid] = twf(timewf(nid) + 10 ** -14)
                nid = find(fw, lambda x: isnan(x) or not np.isfinite(x))
                if not isempty(nid):
                    ouflag = 1
                    ouval = timewf(nid[0])
            fw = 1 / fs * np.fft.fft(tw)
            fw = fw[ii]

        cc = np.zeros(NL, 1)
        cc[ii] = fx[ii] * fw
        out = np.fft.ifft(cc, NL)
        WFT[sn, np.arange(1, L)] = out[1 + n1, NL - n2]

        # Code for plotting.

        return WFT,


def parcalc(racc, L, wp, fwt, twf, disp_mode):
    racc = min(racc, 0.5 - 10 ** -10)
    # level0
    ctol = max(racc / 1000, 10 ** -12)  # parameter of numerical accuracy
    MIC = max(10000, 10 * L)  # max interval count

    nt = (1 / (4 * fs)) * np.arange(-8 * L + 1, 8 * L).transpose()  # level1 should be hermitian conjugate?
    nt = nt[wp.t1 < nt][nt < wp.t2]

    nxi = 2 * np.pi * 4 * fs / (16 * L - 1) * np.arange(-8 * L + 1, 8 * L).transpose()
    nxi = nxi[nxi > wp.xi1][nxi < wp.xi2]

    if not isempty(fwt):
        wp.fwt = fwt
        if isempty(wp.ompeak):
            values = np.abs(fwt(nxi))
            ipeak = values.argmax()  # level2
            wp.ompeak = np.mean(nxi[ipeak])
            wp.ompeak = scipy.optimize.fmin(func=lambda x: -np.abs(fwt(x)), x0=wp.ompeak)  # level1

        if isempty(wp.fwtmax):
            wp.fwtmax = fwt(wp.ompeak)
            if np.isnan(wp.fwtmax):
                wp.twfmax = fwt[wp.ompeak + 10 ** -14]

        if np.abs(wp.ompeak) > 10 ** -12:
            print("Warning")
            fwt = lambda xi: fwt[xi + wp.ompeak]
            if not isempty(twf):
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

        if isempty(wp.C):
            if not twf:  # level0
                wp.C = np.pi * twf(0)
                if np.isnan(wp.C):
                    wp.C = np.pi * twf(10 ** -14)
            else:
                wp.C = (QQ[0, 0] + QQ[0, 1]) / 2

        if wflag == 1 and not disp_mode:
            print("Freq domain window not well behaved")
        if isempty(wp.omg):
            px1 = np.min(wp.ompeak - xx[0, 0], xx[0, 1] - wp.ompeak)
            px2 = np.min(wp.ompeak - xx[3, 0], xx[3, 1] - wp.ompeak)
            [Y1, errY1] = quadgk(lambda u: u * fwt(wp.ompeak + u) - u * fwt(wp.ompeak - u), 0, px1, limit=2 * MIC,
                                 epsabs=0, epsrel=10 ** -12)
            [Y2, errY2] = quadgk(lambda u: u * fwt(wp.ompeak + u) - u * fwt(wp.ompeak - u), px1, px2, limit=2 * MIC,
                                 epsabs=0, epsrel=10 ** -12)
            [Y3, errY3] = quadgk(lambda u: -u * fwt(wp.ompeak - u), px2, wp.ompeak - xx[3, 0], limit=2 * MIC, epsabs=0,
                                 epsrel=10 ** -12)
            [Y4, errY4] = quadgk(lambda u: u * fwt(wp.ompeak + u), px2, xx[3, 1] - wp.ompeak, limit=2 * MIC, epsabs=0,
                                 epsrel=10 ** -12)
            if np.abs((errY1 + errY2 + errY3 + errY4) / (Y1 + Y2 + Y3 + Y4)) < 10 ** -4:
                wp.omg = wp.ompeak + (Y1 + Y2 + Y3 + Y4) / (2 * wp.C)
            else:
                wp.omg = np.inf

        if isempty(twf):
            PP, wflag, xx, ss = sqeps(lambda x: np.abs(fwt(x)) ** 2, wp.ompeak, wp.xi1, wp.xi2, racc, MIC,
                                      np.asarray([-1, 1], dtype=np.float64) * 8 * twopi * fs)
            Etot = np.sum(PP[0]) / twopi

            CL = 2 ** (nextpow2(MIC / 8))
            CT = CL / (2 * abs(ss[0, 1] - ss[0, 0]))
            CNq = np.ceil((CL + 1) / 2)
            cxi = (twopi / CT) * np.arange(CNq - CL, CNq - 2).transpose()
            idm = find(cxi, lambda i: i <= wp.xi1)
            idc = find(cxi, lambda i: wp.xi1 < i < wp.xi2)
            idp = find(cxi, lambda i: i >= wp.xi2)

            Cfwt = np.asarray(np.zeros(len(idm), 1), fwt(cxi[idc]), np.zeros(len(idp), 1))
            idnan = find(Cfwt, lambda i: isnan(i))

            if not isempty(idnan):
                idnorm = find(Cfwt, lambda i: not isnan(i))
                Cfwt[idnan] = scipy.interpolate.interp1d(idnorm, Cfwt(idnorm), idnan, 'spline', 'extrap')

            Ctwf = np.fft.ifft(
                (CL / CT) * Cfwt[np.asarray(np.arange(CL - CNq + 1, CL + 1), np.arange(1, CL - CNq + 1))])
            Ctwf = Ctwf[np.asarray(np.arange(CNq + 1, CL + 1), np.arange(1, CNq + 1))]

            Etwf = np.abs(Ctwf) ** 2
            Efwt = np.abs(Cfwt) ** 2

            Iest1 = CT / CL * np.sum(np.abs(Etwf[3:] - 2 * Etwf[2:-1] + Etwf[2:-1] + Etwf[:-2])) / 24
            Iest2 = 1 / CL * np.sum(np.abs(Etwf[3:] - 2 * Etwf[2:-1] + Etwf[2:-1] + Etwf[:-2])) / 24
            Eest = CT / CL * np.sum(Etwf)
            perr = np.inf

            while (np.abs(Etot - Eest) + Iest1 + Iest2) / Etot < perr:
                CT /= 2
                perr = (np.abs(Etot - Eest) + Iest1 + Iest2) / Etot

                CNq = np.ceil((CL + 1) / 2)
                cxi = (twopi / CT) * np.arange(CNq - CL, CNq - 2).transpose()

                idm = find(cxi, lambda i: i <= wp.xi1)
                idc = find(cxi, lambda i: wp.xi1 < i < wp.xi2)
                idp = find(cxi, lambda i: i >= wp.xi2)

                idnan = find(Cfwt, lambda i: isnan(i))

                if not isempty(idnan):
                    idnorm = find(Cfwt, lambda i: not isnan(i))
                    Cfwt[idnan] = scipy.interpolate.interp1d(idnorm, Cfwt(idnorm), idnan, 'spline', 'extrap')

                Ctwf = np.fft.ifft(
                    (CL / CT) * Cfwt[np.asarray(np.arange(CL - CNq + 1, CL + 1), np.arange(1, CL - CNq + 1))])
                Ctwf = Ctwf[np.asarray(np.arange(CNq + 1, CL + 1), np.arange(1, CNq + 1))]

                Etwf = np.abs(Ctwf) ** 2
                Efwt = np.abs(Cfwt) ** 2

                Iest1 = CT / CL * np.sum(np.abs(Etwf[3:] - 2 * Etwf[2:-1] + Etwf[2:-1] + Etwf[:-2])) / 24
                Iest2 = 1 / CL * np.sum(np.abs(Etwf[3:] - 2 * Etwf[2:-1] + Etwf[2:-1] + Etwf[:-2])) / 24
                Eest = CT / CL * np.sum(Etwf)

            CL = 16 * CL
            CT *= 2

            CNq = np.ceil((CL + 1) / 2)
            cxi = (twopi / CT) * np.arange(CNq - CL, CNq - 2).transpose()

            idm = find(cxi, lambda i: i <= wp.xi1)
            idc = find(cxi, lambda i: wp.xi1 < i < wp.xi2)
            idp = find(cxi, lambda i: i >= wp.xi2)

            idnan = find(Cfwt, lambda i: isnan(i))

            if not isempty(idnan):
                idnorm = find(Cfwt, lambda i: not isnan(i))
                Cfwt[idnan] = scipy.interpolate.interp1d(idnorm, Cfwt(idnorm), idnan, 'spline', 'extrap')

            Ctwf = np.fft.ifft(
                (CL / CT) * Cfwt[np.asarray(np.arange(CL - CNq + 1, CL + 1), np.arange(1, CL - CNq + 1))])
            Ctwf = Ctwf[np.asarray(np.arange(CNq + 1, CL + 1), np.arange(1, CNq + 1))]

            Etwf = np.abs(Ctwf) ** 2
            Efwt = np.abs(Cfwt) ** 2

            Iest1 = CT / CL * np.sum(np.abs(Etwf[3:] - 2 * Etwf[2:-1] + Etwf[2:-1] + Etwf[:-2])) / 24
            Iest2 = 1 / CL * np.sum(np.abs(Etwf[3:] - 2 * Etwf[2:-1] + Etwf[2:-1] + Etwf[:-2])) / 24
            Eest = CT / CL * np.sum(Etwf)

            if (abs(Etot - Eest) + Iest1 + Iest2) / Etot > 0.01:
                print("Warning: Cannot accurately invert the specified...")

            Ctwf = Ctwf[:2 * CNq - 2]
            ct = CT / CL * np.arange(-(CNq - 2), CNq - 1).transpose()

            wp.twf = [Ctwf, ct]

            if isempty(wp.tpeak):
                pass
                # TODO: add later

    if not isempty(twf):
        wp.twf = twf
        if isempty(wp.tpeak):
            values = np.abs(twf(nt))
            ipeak = values.argmax()  # level2
            wp.tpeak = np.mean(nt[ipeak])
            wp.tpeak = scipy.optimize.fmin(lambda x: -np.abs(twf(x)), wp.tpeak)

        if isempty(fwt):
            PP, wflag, xx, ss = sqeps(lambda x: abs(twf(x)) ** 2, wp.tpeak, wp.t1, wp.t2, racc, MIC,
                                      np.array([-1, 1]) * 8 * (2 * np.pi * fs))
            Etot = np.sum(PP[1])

            CL = 2 ** nextpow2(MIC / 8)
            CT = 2 * abs(ss[1, 2] - ss[1, 1])

            CNq = np.ceil((CL + 1) / 2)
            ct = (CT / CL) * np.arange(CNq - CL, CNq).transpose()
            idm = find(ct, lambda x: x <= wp.t1)
            idc = find(ct, lambda x: wp.t1 < x < wp.t2)
            idp = find(ct, lambda x: x >= wp.t2)

            Ctwf = [np.zeros(len(idm), 1), twf(ct(idc)), np.zeros(len(idp), 1)]
            idnan = find(Ctwf, lambda i: np.isnan(i))

            if not isempty(idnan):
                idnorm = find(Ctwf, lambda x: not isnan(x))
                Ctwf[idnan] = scipy.interpolate.interp1d(idnorm, Ctwf(idnorm), idnan, 'spline', 'extrap')

            Cfwt = (CT / CL) * np.fft.fft(Ctwf([np.arange(CL - CNq + 1, CL - CNq, CL, 1)]))
            Cfwt = Cfwt(np.arange(CNq + 1, CNq, CL, 1))

            Etwf = abs(Ctwf) ** 2
            Efwt = abs(Ctwf) ** 2

            Iest1 = (CT / CL) * sum(abs(Etwf[3:] - 2 * Etwf[2: -1] + Etwf[1: -2])) / 24
            Iest2 = (1 / CL) * sum(abs(Etwf[3:] - 2 * Etwf[2: -1] + Etwf[1: -2])) / 24

            Eest = (1 / CT) * sum(Efwt)
            perr = np.inf

            while (abs(Etot - Eest) + Iest1 + Iest2) / Etot <= perr:
                CT = CT * 2
                perr = (abs(Etot - Eest) + Iest1 + Iest2) / Etot

                CNq = np.ceil((CL + 1) / 2)
                ct = ((CT / CL) * (CNq - np.arange(CL, CNq))).transpose()
                idm = find(ct <= wp.t1)
                idc = find(ct > wp.t1 & ct < wp.t2)
                idp = find(ct >= wp.t2)

                Ctwf = [np.zeros(len(idm), 1), twf(ct(idc)), np.zeros(len(idp), 1)]
                idnan = find(Ctwf, lambda x: isnan(x))

                if not isempty(idnan):
                    idnorm = find(Ctwf, lambda x: not isnan(x))
                    Ctwf[idnan] = scipy.interpolate.interp1d(idnorm, Ctwf(idnorm), idnan, 'spline', 'extrap')

                Cfwt = (CT / CL) * np.fft.fft(Ctwf(np.arange(CL - CNq + 1, CL - CNq, CL, 1)))
                Cfwt = Cfwt(np.arange(CNq + 1, CNq, CL, 1))

                Etwf = abs(Ctwf) ** 2
                Efwt = abs(Ctwf) ** 2

                Iest1 = (CT / CL) * sum(abs(Etwf[3:] - 2 * Etwf[2: -1] + Etwf[1: -2])) / 24
                Iest2 = (1 / CL) * sum(abs(Etwf[3:] - 2 * Etwf[2: -1] + Etwf[1: -2])) / 24
                Eest = (1 / CT) * sum(Efwt)

            CL = 16 * CL
            CT = CT * 2

            CNq = np.ceil((CL + 1) / 2)
            ct = ((CT / CL) * (CNq - np.arange(CL, CNq))).transpose()
            idm = find(ct <= wp.t1)
            idc = find(ct > wp.t1 & ct < wp.t2)
            idp = find(ct >= wp.t2)

            Ctwf = [np.zeros(len(idm), 1), twf(ct(idc)), np.zeros(len(idp), 1)]
            idnan = find(Ctwf, lambda x: isnan(x))

            if not isempty(idnan):
                idnorm = find(Ctwf, lambda x: not isnan(x))
                Ctwf[idnan] = scipy.interpolate.interp1d(idnorm, Ctwf(idnorm), idnan, 'spline', 'extrap')

            Cfwt = (CT / CL) * np.fft.fft(Ctwf(np.arange(CL - CNq + 1, CL - CNq, CL, 1)))
            Cfwt = Cfwt(np.arange(CNq + 1, CNq, CL, 1))

            Etwf = abs(Ctwf) ** 2
            Efwt = abs(Ctwf) ** 2

            Iest1 = (CT / CL) * sum(abs(Etwf[3:] - 2 * Etwf[2: -1] + Etwf[1: -2])) / 24
            Iest2 = (1 / CL) * sum(abs(Etwf[3:] - 2 * Etwf[2: -1] + Etwf[1: -2])) / 24
            Eest = (1 / CT) * sum(Efwt)

            if (abs(Etot - Eest) + Iest1 + Iest2) / Etot > 0.01:
                print("Cannot accurately ...")

            Cfwt = Cfwt[1:2 * CNq - 3]
            cxi = ((twopi / CT) * -np.arange(CNq - 2, CNq - 2)).transpose()
            wp.fwt = np.asarray(Cfwt, cxi)

            if isempty(wp.ompeak):
                values = np.abs(fwt(nxi))
                ipeak = values.argmax()  # level2
                if len(ipeak) == 1:
                    a1 = abs(Cfwt[ipeak - 1])
                    a2 = abs(Cfwt[ipeak])
                    a3 = abs(Cfwt[ipeak + 1])

                    wp.ompeak = cxi[ipeak]
                    if abs(a1 - 2 * a2 + a3) > 2 * eps:  # quadratic interp
                        wp.ompeak = wp.ompeak + 1 / 2 * (a1 - a3) / (a1 - 2 * a2 + a3) * (twopi / CT)

                else:
                    wp.ompeak = np.mean(cxi[ipeak])

            if isempty(wp.fwtmax):
                _, ipeak = min(abs(cxi - wp.ompeak))
                wp.fwtmax = scipy.interpolate.interp1d(cxi[ipeak - 1:ipeak + 1], abs(Cfwt[ipeak - 1:ipeak + 1]),
                                                       wp.ompeak, "spline")

            if isempty(wp.C):
                wp.C = twopi / 2 * twf(0)
                if isnan(wp.C):
                    wp.C = twopi / 2 * twf(10 ** -14)
            if isempty(wp.omg):
                wp.omg = sum((twopi / CT) * cxi * Cfwt / (2 * wp.C))

            cxi = np.arange(cxi - np.pi, cxi[-1] + np.pi / CT, cxi[-1])
            CS = (twopi / CT) * np.cumsum(Cfwt)
            CS = np.asarray([0], CS) / abs(CS[-1])
            CS = abs(CS)

            ICS = (twopi / CT) * np.cumsum(Cfwt[::-1])  # level3
            ICS = ICS[::-1]
            ICS = np.asarray(ICS, []) / ICS[0]
            ICS = abs(ICS)

            xid = np.asarray()  # TODO: add later
            xid = find(CS[:-2], lambda i: i < racc / 2)
            a = CS[:-1]
            b = CS[2:]
            if a.any(a < racc / 2) and b.any(b > racc / 2):
                wp.x1e = cxi[0]
            else:
                a1 = CS[xid] - racc / 2
                a2 = CS[xid + 1] - racc / 2
                wp.x1e = cxi[xid] - a1 * (cxi[xid + 1] - cxi[xid]) / (a2 - a1)

            xid = np.asarray()  # TODO: add later
            if isempty(xid):
                wp.xi2e = cxi[-1]
            else:
                a1 = ICS[xid] - racc / 2
                a2 = ICS[xid + 1] - racc / 2
                wp.xi1e = cxi[xid] - a1 * (cxi[xid + 1] - cxi[xid]) / (a2 - a1)

            xid = np.asarray()  # TODO: add later
            if isempty(xid):
                wp.xi1h = cxi[0]
            else:
                a1 = CS[xid] - 0.25
                a2 = CS[xid + 1] - 0.25
                wp.xi1h = cxi[xid] - a1 * (cxi[xid + 1] - cxi[xid]) / (a2 - a1)

            xid = np.asarray()  # TODO: add later
            if isempty(xid):
                wp.xi2h = cxi[-1]
            else:
                a1 = ICS[xid] - 0.25
                a2 = ICS[xid + 1] - 0.25
                wp.xi2h = cxi[xid] - a1 * (cxi[xid + 1] - cxi[xid]) / (a2 - a1)

            if abs(wp.ompeak) > 10 ** -12:
                wp.xi1 = wp.xi1 - wp.ompeak
                wp.xi2 = wp.xi2 - wp.ompeak
                wp.xi1e = wp.xi1e - wp.ompeak
                wp.xi2e = wp.xi2e - wp.ompeak
                wp.xi1h = wp.xi1h - wp.ompeak
                wp.xi2h = wp.xi2h - wp.ompeak
                wp.omg = wp.omg - wp.ompeak

                twf = lambda t: twf(t) * np.exp(np.complex(-1 * wp.ompeak * t))
                wp.twf = twf

                Ctwf = [np.zeros(len(idm), 1), twf(ct(idc)), np.zeros(len(idp), 1)]
                idnan = find(Ctwf, lambda x: isnan(x))

                if not isempty(idnan):
                    idnorm = find(Ctwf, lambda x: not isnan(x))
                    Ctwf[idnan] = scipy.interpolate.interp1d(idnorm, Ctwf(idnorm), idnan, 'spline', 'extrap')

                Cfwt = (CT / CL) * np.fft.fft(Ctwf(np.arange(CL - CNq + 1, CL - CNq, CL, 1)))
                Cfwt = Cfwt(np.arange(CNq + 1, CNq, CL, 1))

                wp.fwt = np.asarray(Cfwt, cxi)
                wp.ompeak = 0

        if isempty(wp.twfmax):
            wp.twfmax = twf(wp.tpeak)
            if isnan(wp.twfmax):
                wp.twfmax = twf(wp.tpeak + 10 ** -14)

        vfun = twf
        xp = wp.tpeak
        lim1 = wp.t1
        lim2 = wp.t2

        QQ, wflag, xx, ss = sqeps(vfun, xp, lim1, lim2, racc, MIC, np.array([-1, 1]) * 8 * (2 * np.pi * fs))
        wp.t1e = ss[0, 0]
        wp.t2e = ss[0, 1]
        wp.t1h = ss[1, 0]
        wp.t2h = ss[1, 1]
        if wflag == 1:
            print("Time domain window not well behaved...")


def sqeps(vfun, xp, lim1, lim2, racc, MIC, nlims):
    wflag = 0
    ctol = np.max([racc / 1000, 10 ** -12])
    nlim1 = nlims[0]
    nlim2 = nlims[1]

    kk = 1
    shp = 0.01  # Peak shift - changed from 0 because of scipy algorithm behaving differently to Matlab.

    while np.isnan(vfun(xp + shp) or not np.isfinite(vfun(xp + shp))):
        shp = kk * 10 ** -14
        kk *= -2
        print("Possible incorrect implementation here.")
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
        qv1 = (np.abs(vfun(tx1)) + np.abs(vfun((tx1 + lim1) / 2)) + np.abs(vfun((tx1 + 3 * lim1) / 4))) / np.abs(
            vmax)
    else:
        qv1 = np.NaN

    if qv1 < 10 ** (-8) / 3:
        x1e = scipy.optimize.fsolve(
            func=lambda u: np.abs(vfun(u) / vmax) + np.abs(vfun((u + lim1) / 2) / vmax) + np.abs(
                vfun((u + 3 * lim1) / 4) / vmax) - 10 ^ (-8), x0=[xp + shp, tx1])
    elif np.isnan(qv1):
        x1e = scipy.optimize.fsolve(
            func=
            lambda u: (
                    np.abs(vfun(xp - np.abs(u)) / vmax)
                    + np.abs(vfun(xp - np.sqrt(3) * np.abs(u)) / vmax)
                    + np.abs(vfun(xp - np.sqrt(5) * np.abs(u)) / vmax)
                    - 10 ** (-8)
            ),
            x0=shp)

        x1e = xp - np.abs(x1e)

    else:
        x1e = xp + (lim1 - xp) / 2

    if np.isfinite(lim2):
        tx2 = lim2 - 0.01 * (lim2 - xp)
        qv2 = (abs(vfun(tx2)) + abs(vfun((tx2 + lim2) / 2)) + abs(vfun((tx2 + 3 * lim2) / 4))) / abs(vmax)
    else:
        qv2 = np.NaN

    if qv2 < 10 ^ (-8):
        x2e = scipy.optimize.fsolve(
            func=lambda u: np.abs(vfun(u) / vmax) + np.abs(vfun((u + lim2) / 2) / vmax) + np.abs(
                vfun((u + 3 * lim2) / 4) / vmax) - 10 ** (-8), x0=[xp + shp, tx2])
    elif np.isnan(qv2):
        x2e = scipy.optimize.fsolve(
            func=lambda u: abs(vfun(xp + abs(u)) / vmax) + abs(vfun(xp + np.sqrt(3) * abs(u)) / vmax) + abs(
                vfun(xp + np.sqrt(5) * np.abs(u)) / vmax) - 10 ** (-8), x0=shp)

        x2e = xp + abs(x2e)

    else:
        x2e = xp + (lim2 - xp) / 2

    if np.isnan(x1e):
        x1e = scipy.optimize.fmin(func=lambda u: abs(abs(vfun(x1h - abs(u)) / vmax) - 10 ** (-8)), x0=0)
        x1e = x1h - abs(x1e)
        lim1 = x1e
        wflag = 1
    if np.isnan(x2e):
        x2e = scipy.optimize.fmin(func=lambda u: abs(abs(vfun(x2h + abs(u)) / vmax) - 10 ** (-8)), x0=0)
        x2e = x2h + abs(x2e)
        lim2 = x2e
        wflag = 1

    # Integrate given function to find Q1 and Q2.
    Q1 = 0  # line1003
    Q2 = 0

    qv, eb = quadgk(vfun, xp, x1e, limit=MIC, epsabs=0, epsrel=0.1 * ctol)
    qv, eb = quadgk(vfun, xp, x1e, limit=MIC, epsabs=0.1 * abs(ctol * (Q1 + qv)), epsrel=0)

    x1m = x1e
    q1m = qv

    if abs(eb / (Q1 + qv)) > ctol:
        wflag = 1
        qv, eb = quadgk(vfun, xp, x1e, limit=MIC, epsabs=0, epsrel=0.1 * ctol)
        qv, eb = quadgk(vfun, xp, x1e, limit=MIC, epsabs=0.1 * abs(ctol * (Q1 + qv)), epsrel=0)
        x1m = x1h
        q1m = qv
        if abs(eb / (Q1 + qv)) <= ctol:
            while True:
                qv, eb = quadgk(vfun, xp, max([xp + (x1m - xp) * 2, x1e]), limit=MIC, epsabs=0,
                                epsrel=0.1 * ctol)
                qv, eb = quadgk(vfun, xp, max([xp + (x1m - xp) * 2, x1e]), limit=MIC,
                                epsabs=0.1 * abs(ctol * (Q1 + qv)), epsrel=0)
                if abs(eb / (Q1 + qv)) > ctol:
                    break
                x1m = max([xp + (x1m - xp) * 2, x1e])
                q1m = qv
        else:
            while abs(eb / (Q1 + qv)) > ctol:
                x1m = xp + (x1m - xp) / 2
                qv, eb = quadgk(vfun, xp, x1m, limit=MIC, epsabs=0, epsrel=0.1 * ctol)
                qv, eb = quadgk(vfun, xp, x1m, limit=MIC, epsabs=0.1 * abs(ctol * (Q1 + qv)),
                                epsrel=0)
                q1m = qv
        qv, eb = quadgk(vfun, xp, x1e, limit=MIC, epsabs=0.1 * abs(ctol * (Q1 + qv)), epsrel=0)
        if abs(eb) < 0.5 * abs(qv):
            Q1 = Q1 + qv

    Q1 = Q1 + q1m
    if wflag == 0:
        qv, eb = quadgk(vfun, x1e, lim1, limit=MIC, epsabs=0.1 * abs(ctol * Q1), epsrel=0)
        if not np.isfinite(lim1) and np.isnan(qv):
            lim1 = x1e
            while not np.isnan(vfun(2 * lim1)):
                lim1 = 2 * lim1
            qv, eb = quadgk(vfun, x1e, lim1, limit=MIC, epsabs=0.1 * abs(ctol * Q1), epsrel=0)
        if abs(eb / Q1) > ctol:
            wflag = 1
            qv, eb = quadgk(vfun, x1e, max([min([8 * x1e, nlim1]), lim1]), limit=MIC,
                            epsabs=0.1 * abs(ctol * Q1), epsrel=0)
        if abs(eb) < 0.5 * abs(qv):
            Q1 = Q1 + qv

    Q1 = -Q1
    qv, eb = quadgk(vfun, xp, x2e, limit=MIC, epsabs=0, epsrel=0.1 * ctol)
    qv, eb = quadgk(vfun, xp, x2e, limit=MIC, epsabs=0.1 * abs(ctol * (Q2 + qv)), epsrel=0)
    x2m = x2e
    q2m = qv
    if abs(eb / (Q2 + qv)) > ctol:
        wflag = 1
        qv, eb = quadgk(vfun, xp, x2e, limit=MIC, epsabs=0, epsrel=0.1 * ctol)
        qv, eb = quadgk(vfun, xp, x2e, limit=MIC, epsabs=0.1 * abs(ctol * (Q2 + qv)), epsrel=0)

        x2m = x2h
        q2m = qv
        if abs(eb / (Q2 + qv)) <= ctol:
            while True:
                qv, eb = quadgk(vfun, xp, min([xp + (x2m - xp) * 2, x2e]), limit=MIC, epsabs=0,
                                epsrel=0.1 * ctol)
                qv, eb = quadgk(vfun, xp, min([xp + (x2m - xp) * 2, x2e]), limit=MIC,
                                epsabs=0.1 * abs(ctol * (Q2 + qv)), epsrel=0)
                if abs(eb / (Q2 + qv)) > ctol:
                    break
                x2m = min([xp + (x2m - xp) * 2, x2e])
                q2m = qv

        else:
            while abs(eb / (Q2 + qv)) > ctol:
                x2m = xp + (x2m - xp) / 2
                qv, eb = quadgk(vfun, xp, x2m, limit=MIC, epsabs=0, epsrel=0.1 * ctol)
                qv, eb = quadgk(vfun, xp, x2m, limit=MIC, epsabs=0.1 * abs(ctol * (Q2 + qv)),
                                epsrel=0)
                q2m = qv
        qv, eb = quadgk(vfun, x2m, x2e, limit=MIC, epsabs=0.1 * abs(ctol * (Q2 + qv)), epsrel=0)
        if abs(eb) < 0.5 * abs(qv):
            Q2 += qv

    Q2 += q2m
    if wflag == 0:
        qv, eb = quadgk(vfun, x2e, lim2, limit=MIC, epsabs=0.1 * abs(ctol * Q2), epsrel=0)
        if not np.isfinite(lim2) and np.isnan(qv):
            lim2 = x2e
            while not np.isnan(vfun(2 * lim2)):
                lim2 = 2 * lim2
            qv, eb = quadgk(vfun, x2e, lim2, limit=MIC, epsabs=0.1 * abs(ctol * Q2), epsrel=0)
        if abs(eb / Q2) > ctol:
            wflag = 1
            qv, eb = quadgk(vfun, x2e,
                            min([max([8 * x2e, nlim2]), lim2]),
                            limit=MIC,
                            epsabs=0.1 * abs(ctol * Q2),
                            epsrel=0)
            if abs(eb) < 0.5 * abs(qv):
                Q2 = Q2 + qv

        QQ = np.asarray([[Q1, Q2], [-q1m, q2m]], dtype=np.float64)
        xx = np.asarray([[x1e, x2e],
                         [x1h, x2h],
                         [x1m, x2m],
                         [lim1, lim2]], dtype=np.float64)

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
                    [pv, _] = quadgk(vfun, cx1, nx, limit=MIC, epsabs=0.1 * abs(ctol * Q), epsrel=0)
                    if abs(1 - abs((Q - cq1 - pv) / Q)) >= zv:
                        cx2 = nx
                        cq2 = cq1 + pv
                        break
                    cx1 = nx
                    cq1 = cq1 + pv
            else:
                while True:
                    nx = xp + rb * (cx1 - xp)
                    if nx < lim1:
                        nx = (cx1 + lim1) / 2
                    if nx > lim2:
                        nx = (cx1 + lim2) / 2
                    [pv, _] = quadgk(vfun, cx1, nx, limit=MIC, epsabs=0.1 * abs(ctol * Q), epsrel=0)
                    if abs(1 - abs((Q - cq1 - pv) / Q)) >= zv:
                        cx2 = nx
                        cq2 = cq1 + pv
                        break
                    cx1 = nx
                    cq1 = cq1 + pv

            [pv, _] = quadgk(vfun, cx1, (cx1 + cx2) / 2, limit=MIC, epsabs=0.1 * abs(ctol * Q), epsrel=0)
            qfun = lambda x: 1 - abs((Q - (cq1 + pv +
                                           quadgk(vfun, (cx1 + cx2) / 2, x, limit=MIC // 10,
                                                  epsabs=0.5 * abs(ctol * Q), epsrel=0)[0])
                                      ) / Q)
            x0 = scipy.optimize.fsolve(lambda x: abs(qfun(x)) - zv,
                                       x0=(cx1 + cx2) / 2)  # Modified to use average of cx1 and cx2.
            return x0

        s1e = fz(racc / 2)
        s2e = fz(1 - racc / 2)
        s1h = fz(0.5 / 2)
        s2h = fz(1 - 0.5 / 2)
        ss = np.asarray([[s1e, s2e],
                         [s1h, s2h]], dtype=np.float64)

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
            if itn > 2 and cic > ic[itn - 1] > ic[itn - 2]:
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
    fs = 20
    t = np.arange(0, 50, 1 / fs)
    signal = np.cos(twopi * 3 * t + 0.75 * np.sin(twopi * t / 5))

    wft(signal, fs)
