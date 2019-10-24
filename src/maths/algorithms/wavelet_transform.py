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
import pdb
import numpy as np
import scipy.special as spec

# Names of window parameters.
import scipy
import scipy.optimize
import scipy.integrate
from scipy.sparse.linalg.isolve.lsqr import eps
import matplotlib.pyplot as plt

from maths.algorithms.matlab_utils import *

"""
An attempt to convert the Matlab WT algorithm into Python. Not in use.
"""

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

    t1e = None
    t2e = None
    t1h = None
    t2h = None
    f0 = None

    def twf(self,t):
      raise NotImplemented('Twf is not implemented. Alter the has_twf property')

    @property
    def has_twf(self):
      return False

    def __str__(self):
      sbuf = []
      sbuf.append('xi1=%s' % self.xi1)
      sbuf.append('xi2=%s' % self.xi2)
      sbuf.append('t1=%s' % self.t1)
      sbuf.append('t2=%s' % self.t2)
      sbuf.append('C=%s' % self.C)
      sbuf.append('D=%s' % self.D)
      sbuf.append('xi1e=%s' % self.xi1e)
      sbuf.append('xi2e=%s' % self.xi2e)
      sbuf.append('xi1h=%s' % self.xi1h)
      sbuf.append('xi2h=%s' % self.xi2h)
      sbuf.append('t1e=%s' % self.t1e)
      sbuf.append('t2e=%s' % self.t2e)
      sbuf.append('t1h=%s' % self.t1h)
      sbuf.append('t2h=%s' % self.t2h)
      return '\n'.join(sbuf)
class MorseWavelet(WindowParams):
  def __init__(self,a, f0):
    a = float(a)
    self.f0 = float(f0)
    self.q = 30*np.power(f0,2)/a
    self.__B = np.power((np.exp(1)*a/self.q),(self.q/a))
    self.__a = a
    self.__name = 'Morse'
    self.xi1 = 0.
    self.ompeak = np.power((self.q/a),(1./a))
    self.C = (1/2)*(self.__B/a)*spec.gamma(self.q/a)
    self.D = self.C * exp(1 / (2 * self.q ** 2))
    if self.q > 1:
      self.D = (self.ompeak/2)*(self.__B/a)*spec.gamma((self.q-1)/a)

    self.fwtmax = self.fwt(self.ompeak)

  @property
  def name(self):
    return self.__name

  def module(self,xi):
    return np.power(np.abs(self.fwt(xi)), 2)

  def fwt(self,xi):
    if np.isscalar(xi):
      part_log = (-np.inf if xi<=0 else np.log(xi) )
      return np.exp(-np.power(xi,self.__a)+self.q*(part_log + (1/self.__a)*np.log(exp(1)*self.__a/self.q)))

    ind = np.where(xi > 0)
    rv = np.copy(xi)
    rv[np.where(xi <= 0)] = -np.inf
    rv[ind] = np.log(xi[ind])
    return np.exp(-np.power(xi,self.__a)+self.q*(rv + (1/self.__a)*np.log(exp(1)*self.__a/self.q)))

class MorletWavelet(WindowParams):
  def __init__(self,f0):
    self.om0 = 2*np.pi*f0 
    self.__name = 'Morlet'
    self.D = np.inf
    self.f0 = f0

  @property
  def has_twf(self):
    return self.f0 >= 1

  @property
  def name(self):
    return self.__name

  def module(self,xi):
    return np.power(np.abs(self.fwt(xi)), 2)

  def twf(self,t):
    if self.f0 >= 1:
      return (1/np.sqrt(2*np.pi))*(np.exp(1j*self.om0*t)-np.exp(-(self.om0**2)/2))*np.exp(-np.power(t,2)/2)

    raise NotImplemented('Not possible scenario. Fix the has_twf property for f0=%f' % self.__f0)

  def fwt(self,xi):
    if np.isscalar(xi):
      return np.exp(-(1/2)*(self.om0-xi)**2) - np.exp(-(1/2)*( (self.om0**2)+(xi**2)))

    return np.exp( -0.5 * np.power(self.om0-xi,2)) - np.exp ( -0.5*(np.power(self.om0,2) + np.power(xi,2 ) ) )


class LognormWavelet(WindowParams):
  def __init__(self,f0):
    self.q = 2*np.pi*f0
    self.__name = 'Lognorm'
    self.xi1 = 0.
    self.ompeak = 1.
    self.C = np.sqrt(np.pi / 2) / self.q
    self.D = self.C * exp(1 / (2 * self.q ** 2))
    self.f0 = f0

  @property
  def name(self):
    return self.__name

  def module(self,xi):
    return np.power(np.abs(self.fwt(xi)), 2)

  def fwt(self,xi):
    if np.isscalar(xi):
      return np.exp(-(self.q ** 2 / 2) * (-np.inf if xi<=0 else np.log(xi)) ** 2)

    ind = np.where(xi > 0)
    rv = np.copy(xi)
    rv[np.where(xi <= 0)] = -np.inf
    rv[ind] = np.log(xi[ind]) ** 2
    return np.exp(-(self.q ** 2 / 2) * rv )

def wft(signal,
        fs,
        wp,
        fmin=None,
        fmax=None,
        fstep="auto",
        padmode="predictive",
        rel_to_l=0.01,
        preprocess=False,
        disp_mode=True,
        plot_mode=False,
        cut_edges=False,
        nv=None,
        on_error=lambda x: print(f"ERROR: {x}"),
        on_warning=lambda x: print(f"Warning: {x}")):
    p = 1  # WT normalisation.

    fmax = fmax or fs / 2
    L = len(signal)

    if fs <= 0 or not fs:
        on_error("Sampling frequency should be a positive finite number")

    rec_flag = 1

    twf = []
    fwt = wp.fwt
    f0 = wp.f0
    if wp.has_twf:
      twf = wp.twf
    '''
    if window == "Lognorm":
        q = twopi * f0
        wp = LognormWavelet(f0)
        #fwt = lambda xi: np.exp(-(q ** 2 / 2) * log(xi) ** 2)

        #FIX THIS!!
        fwt = wp.fwt#lambda xi: np.exp(-(q ** 2 / 2) * (-np.inf if xi<=0 else np.log(xi)) ** 2)
        if wp.has_twf:
          twf = wp.twf

    # TODO: Implement these later
    elif window == "Morlet":
        pass
    elif window == "Bump":
        pass
    elif window == "Morse":
        pass
    else:
        on_error(f"Invalid window name: {window}")
    '''

    if rec_flag == 1:
        if disp_mode:
            print("Estimating window parameters.i %f" % fs)
        parcalc(rel_to_l, L, wp, fwt, twf, disp_mode, f0, fmax,fs=fs)

    if isempty(fmin):
        fmin = wp.ompeak / twopi * (wp.t2e - wp.t1e) * fs / L

    if fmin > fmax:
        print("WARNING: fmin must be smaller than fmax.")

    if (wp.t2e - wp.t1e) * wp.ompeak / (twopi * fmax) > L / fs:
        print("WARNING: For wavelet function params and signal time-length there are no WT coefficients...")
    elif (wp.t2e - wp.t1e) * wp.ompeak / (twopi * fmin) * fs / L > 1 + 2 * eps:
        print("WARNING: At lowest frequency there are no WT coefficients...")

    nvsim = nv
    wp.nv = nv
    if isempty(nv):
        Nb = 10

        wp.nv = Nb * log(2) / log(wp.xi2h / wp.xi1h)
        nv = ceil(wp.nv)
        print(f"Optimal nv determined to be {nv}")

    freq = 2 ** (arange(ceil(nv * np.log2(fmin)), np.floor(nv * np.log2(fmax))).conj().T / nv)
    SN = len(freq)

    wp.t1e = wp.t1e.reshape(len(wp.t1e))
    coib1 = np.ceil(abs(wp.t1e * fs * wp.ompeak / (twopi * freq)))
    coib2 = np.ceil(abs(wp.t2e * fs * wp.ompeak / (twopi * freq)))

    dflag = int(padmode == "predictive") and fmin < 5 * fs / L

    if preprocess and dflag == 0:
        import preprocessing as preproc
        signal = preproc.preprocess(signal, fs, fmin, fmax)

    NL = 2 ** nextpow2(L + coib1[0] + coib2[0])

    if coib1[0] == 0 and coib2[0] == 0:
        n1 = np.floor((NL - L) / 2)
        n2 = np.ceil((NL - L) / 2)
    else:
        n1 = np.floor((NL - L) * coib1[0] / (coib1[0] + coib2[0]))
        n2 = np.ceil((NL - L) * coib1[0] / (coib1[0] + coib2[0]))

    # TODO: check from here.
    if padmode == "predictive":
        pow = (-(L / fs - np.arange(1, L + 1) / fs)) / (wp.t2h - wp.t1h)
        w = 2 ** pow
        padleft = fcast(
            np.flip(signal),
            fs,
            n1,
            [max([fmin, fs / L]), fmax],
            min([
                np.ceil(SN / 2) + 5,
                np.round(L / 3)
            ]), w)

        padleft = np.flip(padleft)
        padright = fcast(signal, fs, n2, [max([fmin, fs / L]), fmax], min([np.ceil(SN / 2) + 5, np.round(L / 3)]), w)
        dflag = 1
    else:
      padleft = []
      padright = []
      NL = L
      n1 = 0
      n2 = 0

    signal = concat([padleft, signal, padright])

    Nq = np.ceil((NL + 1) / 2)

    ff = concat([
        np.arange(0, Nq),
        -arange(1, NL - Nq)[::-1]
    ]) * fs / NL

    fx = np.fft.fft(signal, np.int(NL), axis=0)
    if preprocess:
        fx[(ff <= max([fmin, fs / L])) & (ff >= fmax)] = 0

        # Windowed Fourier Transform by itself
    WT = np.zeros((SN, L), dtype=np.complex64) * np.NaN
    ouflag = 0
    if (wp.t2e - wp.t1e)*wp.ompeak/(2*np.pi*fmax) > L / fs:
        coib1 = 0
        coib2 = 0

    for sn in range(0, SN):
        freqwf = ff * wp.ompeak / (twopi * freq[sn])
        ii = nonzero((wp.xi1 / twopi < freqwf) & (freqwf < wp.xi2 / twopi))[0]

        if not isempty(fwt):
            fw = fwt(twopi * freqwf[ii]).conj()
            nid = nonzero((isnan(fw)) | (~isfinite(fw)))[0]

            if not isempty(nid):
                fw[nid] = fwt(twopi * freqwf[ii[nid]] + 10 ** -14).conj()
                nid = nonzero((isnan(fw)) | (~isfinite(fw)))[0]
                fw[nid] = 0
                if not isempty(nid):
                    ouflag = 1
                    ouval = twopi * freqwf(nid[0])

        else:
            timewf = (twopi * freq[sn] / wp.ompeak / fs) * concat([
                -arange(0, np.ceil((NL - 1) / 2)) + 1,
                arange(NL + 1 - (np.ceil((NL - 1) / 2) + 1), NL)
            ]).conj().T

            jj = nonzero((timewf > wp.t1) & (timewf < wp.t2))
            tw = np.zeros((NL, 1))
            tw[jj] = twf[timewf[jj]].conj()

            nid = nonzero((isnan(tw)) | (~isfinite(tw)))[0]
            if not isempty(nid):
                tw[nid] = twf[timewf[nid] + 10 ** -14]
                nid = nonzero((isnan(tw)) | (~isfinite(tw)))[0]
                if not isempty(nid):
                    ouflag = 1
                    ouval = timewf[nid[0]]
            fw = 1 / fs * np.fft.fft(tw, axis=0)
            fw = fw[ii]

        cc = zeros(np.int(NL), dtype=np.complex64)
        cc[ii] = fx[ii] * fw[:]

        out = (wp.ompeak / (twopi * freq[sn])) ** (1 - p) * np.fft.ifft(cc, NL, axis=0)

        n1 = np.int(n1)
        n2 = np.int(n2)
        NL = np.int(NL)

        WT[sn, arange(0, L)] = out[n1: NL - n2 + 1]

    if cut_edges:
      icoib = nonzero((L-coib1-coib2) <= 0)[0]
      WT[icoib,:] = np.nan
      ovL = int(np.ceil(np.sum(coib1 + coib2) - L*len(icoib)))
      frn = np.empty((ovL,))*np.nan
      ttn = np.empty((ovL,))*np.nan
      qn = 0
      for fn in range(SN):
        cL = int(coib1[fn] + coib2[fn])
        if cL > 0 and cL < L:
          frn[qn:qn+cL] = fn
          ttn[qn:qn+cL] = concat([np.arange(int(coib1[fn])),np.arange(L-int(coib2[fn]),L)]).T
          qn = qn + cL

      frn = frn[:qn]
      ttn = ttn[:qn]
      WT.ravel()[np.ravel_multi_index([frn.astype(np.int),ttn.astype(np.int)],dims=WT.shape)] = np.nan
    return WT, freq


def parcalc(racc, L, wp, fwt, twf, disp_mode, f0, fmax, wavelet="Lognorm", fs=-1):
    # TODO: function checked
    racc = min([racc, 1 - 10 ** -6])
    ctol = max([racc / 1000, 10 ** -12])  # parameter of numerical accuracy
    MIC = max([10000, 10 * L])  # max interval count
    print('Racc %f ctol %f MIC %f' % (racc,ctol,MIC))

    if fs < 0:
      raise ValueError('FS must be positive')

    if not isempty(fwt):
        wp.fwt = fwt
        if isempty(wp.ompeak):
            wp.ompeak = 1
            if "Morlet" in wavelet:
                wp.ompeak = twopi * f0

            if wp.xi1 > 0 and isfinite(wp.xi2):
                wp.ompeak = sqrt(wp.xi1 * wp.xi2)
            elif isfinite(wp.xi2):
                wp.ompeak = wp.xi2 / 2

            if fwt(wp.ompeak) == 0 or isnan(fwt(wp.ompeak)) or not isfinite(fwt(wp.ompeak)):
                cp1 = wp.ompeak * np.exp(-10 ** -14)
                cp2 = wp.ompeak * np.exp(10 ** -14)
                kk = 1

                while kk < 10 ** 28:
                    cv1 = np.abs(fwt(cp1))
                    cv2 = np.abs(fwt(cp2))
                    kk *= 2

                    if isfinite(cv1) and cv1 > 0:
                        wp.ompeak = cp1
                        break
                    if isfinite(cv2) and cv2 > 0:
                        wp.ompeak = cp2
                        break

                    cp1 *= np.exp(-kk * 10 ** -14)
                    if cp1 <= np.max([wp.xi1, 0]):
                        cp1 = (cp1 * np.exp(kk * 10 ** (-14)) + max([wp.xi1, 0])) / 2

                    cp2 *= np.exp(kk * 10 ** -14)
                    if cp2 >= wp.xi2:
                        cp2 = (cp2 * np.exp(-kk * 10 ** (-14)) + wp.xi2) / 2

                cv = abs(fwt(wp.ompeak))
                while isnan(cv) or cv == 0:
                    if isfinite(wp.xi2):
                        pp = max([wp.xi1, 0]) + (wp.xi2 - max([wp.xi1, 0])) * rand(MIC, 1)
                    else:
                        pp = np.exp(np.arctan(pi * (rand(MIC, 1) - 1 / 2)))

                    cv = max(abs(fwt(pp)))
                    ipeak = np.argmax(abs(fwt(pp)))

                    wp.ompeak = pp[ipeak]

            wp.ompeak = fminsearch(lambda x: -abs(fwt(np.exp(x))), x0=np.log(wp.ompeak), xtol=10 ** -14)
            wp.ompeak = np.exp(wp.ompeak)

        if isempty(wp.fwtmax):
            wp.fwtmax = fwt(wp.ompeak)
            if isnan(wp.fwtmax):
                wp.fwtmax = fwt(wp.ompeak + 10 ** (-14))

        vfun = lambda u: fwt(exp(u)).conj()
        xp = log(wp.ompeak)
        lim1 = -np.inf if wp.xi1 <=0 else log(wp.xi1)
        lim2 = log(wp.xi2)

        # Test admissibility
        if wp.xi1 <= 0:
            AC = fwt(0)
        else:
            AC = 0

        if isnan(AC):
            cx0 = 10 ** -14
            while fwt(cx0) > 10 ** -14:
                cx0 /= 2
            while isnan(fwt(cx0)):
                cx0 *= 2
            AC = fwt(cx0)

        if AC > 10 ** -12:
            print("""--------------------------------------------- Warning! 
            ---------------------------------------------\n Wavelet does not seem to be admissible (its Fourier 
            transform does not vanish at zero frequency)!\n Parameters estimated from its frequency domain form, 
            e.g. integration constant Cpsi (which is \n infinite for non-admissible wavelets), cannot be estimated 
            appropriately (the same concerns the \n number-of-voices ''nv'', when set to ''auto'', so frequency 
            discretization might be also not appropriate).\n It is recommended to use only admissible wavelets.\n 
            ----------------------------------------------------------------------------------------------------\n""")

        QQ, wflag, xx, ss = sqeps(vfun, xp, lim1, lim2, racc, MIC,
                                  [log((wp.ompeak / fmax) * fs / L / 8), log(8 * (wp.ompeak / (fs / L)) * fs)]
                                  )
        wp.xi1e = exp(ss[0, 0])
        wp.xi2e = exp(ss[0, 1])
        wp.xi1h = exp(ss[1, 0])
        wp.xi2h = exp(ss[1, 1])

        if isempty(wp.C):
            wp.C = (QQ[0, 0] + QQ[0, 1]) / 2

        if isempty(wp.D):
            D1, err1, _, _ = quadgk(lambda u: conj(fwt(1 / u)), 1 / wp.ompeak, exp(-xx[0, 0]), 2 * MIC, 0, 10 ** -12)
            D2, err2, _, _ = quadgk(lambda u: -conj(fwt(1 / u)), 1 / wp.ompeak, exp(-xx[0, 1]), 2 * MIC, 0, 10 ** -12)
            D3, err3, _, _ = quadgk(lambda u: conj(fwt(1 / u)), exp(-xx[0, 0]), exp(-xx[3, 0]), 2 * MIC, 0, 10 ** -12)
            D4, err4, _, _ = quadgk(lambda u: -conj(fwt(1 / u)), exp(-xx[0, 1]), exp(-xx[3, 1]), 2 * MIC, 0, 10 ** -12)
            if abs((err1 + err2 + err3 + err4) / (D1 + D2 + D3 + D4)) < 10 ** -4:
                wp.D = (wp.ompeak / 2) * (D1 + D2 + D3 + D4)
            else:
                wp.D = inf

        if wflag == 1:
            print("WARNING")

        if isempty(twf):
            PP, wflag, xx, ss = sqeps(wp.module, wp.ompeak, max([wp.xi1, 0]), wp.xi2, racc, MIC, [0, 8 * (wp.ompeak / (fs / L)) * fs])

            Etot = sum(PP[0, :]) / twopi

            CL = 2 ** nextpow2(MIC / 8)
            CT = CL / (2 * abs(ss[0, 1] - ss[0, 0]))
            CNq = ceil((CL + 1) / 2)
            cxi = (twopi / CT) * arange(CNq - CL - 1, CNq - 1).transpose()

            idm = nonzero(cxi <= max([wp.xi1, 0]))
            idc = nonzero((cxi > max([wp.xi1, 0])) & (cxi < wp.xi2))
            idp = nonzero(cxi >= wp.xi2)

            middle = fwt(cxi[idc])
            Cfwt = vstack([
                zeros((idm[0].size, 1,)),
                middle.reshape(len(middle), 1),
                zeros((idp[0].size, 1,))
            ])

            idnan = isnan(Cfwt).nonzero()

            if ~isempty(idnan):
                idnorm = (~isnan(Cfwt)).nonzero()[0]
                Cfwt[idnan] = interp1(idnorm, Cfwt[idnorm].reshape(len(idnorm)), idnan)

            CL = int(CL)
            CNq = int(CNq)
            Ctwf = ifft((CL / CT) * Cfwt[
                concat([
                    arange(CL - CNq, CL),
                    arange(0, CL - CNq)
                ])
            ], axis=0)

            Ctwf = Ctwf[
                concat([
                    arange(CNq, CL),
                    arange(0, CNq)
                ])
            ]

            Etwf = abs(Ctwf) ** 2
            Efwt = abs(Cfwt) ** 2
            Iest1 = (CT / CL) * sum(abs(Etwf[2:] - 2 * Etwf[1: - 1] + Etwf[:-2])) / 24
            Iest2 = (1 / CT) * sum(abs(Efwt[2:] - 2 * Efwt[1: - 1] + Efwt[:-2])) / 24
            Eest = (CT / CL) * sum(Etwf)
            perr = Inf

            while (abs(Etot - Eest) + Iest1 + Iest2) / Etot <= perr:
                CT /= 2
                perr = (abs(Etot - Eest) + Iest1 + Iest2) / Etot
                CNq = ceil((CL + 1) / 2)
                cxi = twopi / CT * arange(CNq - CL, CNq).conj().T

                idm = nonzero(cxi <= max([wp.xi1, 0]))[0]
                idc = nonzero((cxi > max([wp.xi1, 0])) & (cxi < wp.xi2))[0]
                idp = nonzero(cxi >= wp.xi2)[0]
                Cfwt = asarray(concat([
                        zeros((len(idm), )),
                        fwt(cxi[idc]),
                        zeros((len(idp), ))
                    ]))

                idnan = nonzero(isnan(Cfwt))[0]
                if not isempty(idnan) and not (not is_arraylike(idnan) or all([isempty(i) for i in idnan])):
                    idnorm = nonzero(~isnan(Cfwt))[0]
                    Cfwt[idnan] = interp1(idnan, Cfwt[idnorm].reshape(len(idnorm)), idnan)

                CL = int(CL)
                CNq = int(CNq)
                Ctwf = ifft(CL / CT * Cfwt[
                    concat([
                        arange(CL - CNq, CL),
                        arange(0, CL - CNq)
                    ])
                ], axis=0)

                Ctwf = Ctwf[concat([
                    arange(CNq, CL),
                    arange(0, CNq)]
                )]

                Etwf = abs(Ctwf) ** 2
                Efwt = abs(Cfwt) ** 2

                Iest1 = CT / CL * sum(abs(Etwf[2:] - 2 * Etwf[1:-1] + Etwf[0:-2])) / 24
                Iest2 = 1 / CT * sum(abs(Efwt[2:] - 2 * Efwt[1:-1] + Efwt[0:-2])) / 24
                Eest = CT / CL * sum(Etwf)

            ###END WHILE

            CL = 16*CL
            CT = 2*CT
            CNq = ceil((CL + 1) / 2).astype('int')
            cxi = (2*np.pi) / CT * arange(CNq - CL, CNq).conj().T
            idm = nonzero(cxi <= np.max([wp.xi1,0]))[0]
            idc = nonzero((cxi > np.max([wp.xi1,0])) & (cxi < wp.xi2))[0]
            idp = nonzero(cxi >= wp.xi2)[0]
            Cfwt = asarray(concat([
                    zeros((len(idm), )),
                    fwt(cxi[idc]),
                    zeros((len(idp), ))
                ]))

            idnan = nonzero(isnan(Cfwt))[0]
            if not isempty(idnan):
                    idnorm = nonzero(~isnan(Cfwt))
                    Cfwt[idnan] = interp1(idnorm, Cfwt[idnorm], idnan)


            Ctwf = CL / CT * ifft(Cfwt[
                                         concat([
                                             arange(CL - CNq, CL ),
                                             arange(0, CL - CNq )
                                         ])
                                     ])
            
            Ctwf = Ctwf[concat([np.arange(CNq,CL),np.arange(0,CNq)])]
            Etwf = abs(Ctwf) ** 2
            Efwt = abs(Cfwt) ** 2
            Iest1 = CT / CL * \
                        sum(
                            abs(
                                Etwf[2:] - 2 * Etwf[1:-1] + Etwf[:-2]
                            )
                        ) / 24
            Iest2 = 1 / CT * \
                        sum(
                            abs(
                                Etwf[2:] - 2 * Etwf[1:-1] + Etwf[:-2]
                            )
                        ) / 24

            Eest = CT / CL * sum(Etwf)


            if (abs(Etot - Eest) + Iest1 + Iest1) / Etot > 0.01:
                    print("Warning: cannot accurately invert the specified frequency-domain form....")

            Ctwf = Ctwf[:2 * CNq - 3]
            ct = CT / CL * arange(-(CNq - 2) , CNq - 2 + 1).conj().T
            wp.twf = [Ctwf, ct]
            Ctwf = Ctwf.reshape(len(Ctwf))
            Ctwf = np.multiply(Ctwf,  np.exp(-1j * wp.ompeak * ct))

            if isempty(wp.tpeak):
                ipeak = nonzero(abs(Ctwf) == max(abs(Ctwf)))
                if len(ipeak) == 1:
                    ipeak = ipeak[0]
                    a1 = abs(Ctwf[ipeak - 1])
                    a2 = abs(Ctwf[ipeak])
                    a3 = abs(Ctwf[ipeak + 1])

                    wp.tpeak = ct[ipeak]
                    if abs(a1 - 2 * a2 + a3) > 2 * eps:
                        wp.tpeak = wp.tpeak + 0.5 * (a1 - a3) / (a1 - 2 * a2 + a3) * (CT / CL)

                else:
                    wp.tpeak = mean(ct[ipeak])

            if isempty(wp.twfmax):
                  ipeak = argmin(abs(ct - wp.tpeak))
                  wp.twfmax = interp1(ct[ipeak - 1:ipeak + 2], abs(abs(Ctwf[ipeak - 1:ipeak + 2])), wp.tpeak) # Added +2 since unlike Matlab in Python the last index is not included.

            ct = ct.reshape(len(ct), 1)
            ct = vstack([ct - CT / CL / 2, ct[-1] + CT / CL / 2])
            CS = CT / CL * cumsum(Ctwf)
            CS = vstack([0, CS.reshape(len(CS), 1)]) / CS[-1]
            CS = abs(CS)

            ICS = CT / CL * cumsum(Ctwf[-1::-1]) # Check whether flip is enough
            ICS = ICS[-1::-1]
            ICS = vstack([ICS.reshape(len(ICS), 1), 0]) / ICS[0]
            ICS = abs(ICS)

            xid = nonzero((CS[:-1] < racc / 2) & (CS[1:] >= racc / 2))[0]
            if isempty(xid):
                wp.t1e = ct[0]
            else:
                a1 = CS[xid] - racc / 2
                a2 = CS[xid + 1] - racc / 2
                
                wp.t1e = ct[xid] - a1 * (ct[xid + 1] - ct[xid]) / (a2 - a1)

            xid = nonzero((ICS[:-1] >= racc / 2) & (ICS[1:] < racc / 2))[0] #take the first dimension
            if isempty(xid):
                wp.t2e = ct[-1]
            else:
                xid = xid[-1] #Take the last
                a1 = ICS[xid] - racc / 2
                a2 = ICS[xid + 1] - racc / 2
                wp.t2e = ct[xid] - a1 * (ct[xid + 1] - ct[xid]) / (a2 - a1)

            xid = nonzero((CS[:-1] < .25) & (CS[1:] >= .25))[0]
            if isempty(xid):
                wp.t1h = ct[0]
            else:
                a1 = CS[xid] - .25
                a2 = CS[xid + 1] - .25
                wp.t1h = ct[xid] - a1 * (ct[xid + 1] - ct[xid]) / (a2 - a1)

            xid = nonzero((ICS[:-1] >= .25) & (ICS[1:] < .25))[0]
            if isempty(xid):
                wp.t2h = ct[-1]
            else:
                xid = xid[-1]
                a1 = ICS[xid] - .25
                a2 = ICS[xid + 1] - .25
                wp.t2h = ct[xid] - a1 * (ct[xid + 1] - ct[xid]) / (a2 - a1)

        if not isempty(twf):
            wp.twf = twf
            if isempty(wp.tpeak):
                wp.tpeak = np.nanmax([np.nanmin([0, wp.t2 - abs(wp.t2) / 2]), wp.t1 + abs(wp.t1) / 2])

                if isfinite(wp.t1) and isfinite(wp.t2):
                    wp.tpeak = (wp.t1 + wp.t2) / 2

                if twf(wp.tpeak) == 0 or isnan(twf(wp.tpeak)) or not isfinite(twf(wp.tpeak)):
                    cp1 = wp.tpeak * -10 ** -14
                    cp2 = wp.tpeak * 10 ** -14
                    kk = 1

                    while kk < 10 ** 28:
                        cv1 = abs(twf(cp1))
                        cv2 = abs(twf(cp2))
                        kk *= 2

                        if isfinite(cv1) and cv1 > 0:
                            wp.tpeak = cp1
                            break
                        if isfinite(cv2) and cv2 > 0:
                            wp.tpeak = cp2
                            break

                        cp1 = cp1 - np.exp(-kk * 10 ** -14)
                        if cp1 <= np.max([wp.t1, 0]):
                            cp1 = (cp1 * np.exp(kk * 10 ** (-14)) + max([wp.t1, 0])) / 2

                        cp2 = cp2 + np.exp(kk * 10 ** -14)
                        if cp2 >= wp.t2:
                            cp2 = (cp2 * np.exp(-kk * 10 ** (-14)) + wp.t2) / 2

                    cv = abs(twf(wp.ompeak))
                    while isnan(cv) or cv == 0:
                        if isfinite(wp.t2):
                            pp = max([wp.t1, 0]) + (wp.t2 - max([wp.t1, 0])) * rand(MIC, 1)
                        else:
                            pp = np.exp(np.arctan(pi * (rand(MIC, 1) - 1 / 2)))

                        cv = max(abs(twf(pp)))
                        ipeak = argmax(abs(twf(pp)))

                        wp.tpeak = pp[ipeak]

                wp.tpeak = fminsearch(lambda x: -abs(twf(x)), x0=wp.tpeak, xtol=10 ** -14)

            if isempty(wp.twfmax):
                wp.twfmax = twf(wp.tpeak)
                if isnan(wp.twfmax):
                    wp.twfmax = twf(wp.tpeak + 10 ** -14)

            AC1, ac1_err = quadgk(lambda u: -twf(u), wp.tpeak, xx[0, 0], MIC, 10 ** -16, 0) 
            AC2, ac2_err = quadgk(lambda u: -twf(u), xx[0, 0], xx[3, 0], MIC, 10 ** -16, 0) 
            AC3, ac3_err = quadgk(lambda u: twf(u), wp.tpeak, xx[0, 1], MIC, 10 ** -16, 0) 
            AC4, ac4_err = quadgk(lambda u: twf(u), xx[0, 1], xx[3, 1], MIC, 10 ** -16, 0)

            AC = AC1 + AC2 + AC3 + AC4

            # Accodding to the matlab documentation how the comparison of numbers is implemented.
            # https://stackoverflow.com/questions/26371634/comparison-of-complex-numbers-in-matlab
            if np.real(AC) > 10 ** -8:
                print("WARNING: wavelet does not seem to be admissible.")

            if isempty(fwt):
                compeak = wp.ompeak

                if isempty(compeak):
                    _, _, _, bss = sqeps(lambda u: abs(twf(u)) ** 2, wp.tpeak, wp.t1, wp.t2, 0.01, MIC, [wp.t1, wp.t2])
                    BL = 2 ** (nextpow2(MIC))
                    BNq = ceil((BL + 1) / 2)
                    BT = bss[0, 0]

                    bt = np.linspace(bss[0, 0], bss[0, 1], BL).conj().T
                    bxi = twopi / BT * concat([arange(0, BNq - 1), arange(BNq - BL, -1)]).conj().T

                    Bfwt = fft(twf(bt))
                    ix = nonzero((bxi > max([wp.xi1, 0]) & (bxi < wp.xi2)))

                    imax = argmax(abs(Bfwt[ix]))
                    compeak = bxi[ix[imax]]

                PP, wflag, xx, ss = sqeps(lambda x: abs(twf(x)) ** 2, wp.tpeak, wp.t1, wp.t2, 0.01, MIC, [wp.t1, wp.t2])
                Etot = sum(PP[0, :])

                CL = 2 ** nextpow2(MIC / 8)
                CT = 2 * abs(ss[0, 1] - ss[0, 0])

                CNq = ceil((CL + 1) / 2)
                ct = CT / CL * arange(CNq - CL, CNq - 1).conj().T
                idm = nonzero(ct <= wp.t1)
                idc = nonzero((ct > wp.t1) & (ct < wp.t2))
                idp = nonzero(ct >= wp.t2)

                Ctwf = asarray([
                    zeros((len(idm), 1)),
                    twf(ct[idc]),
                    zeros((len(idp), 1,))
                ])
                idnan = nonzero(isnan(Ctwf))

                if not isempty(idnan):
                    idnorm = nonzero(~isnan(Ctwf))
                    Ctwf[idnan] = interp1(idnorm, Ctwf(idnorm), idnan)

                Cfwt = CT / CL * fft(Ctwf[
                                         concat([
                                             arange(CL - CNq + 1, CL),
                                             arange(1, CL - CNq)
                                         ])
                                     ])

                Cfwt = Cfwt[
                    concat([
                        arange(CNq + 1, CL),
                        arange(1, CNq),
                    ])
                ]

                Etwf = abs(Ctwf) ** 2
                Efwt = abs(Cfwt) ** 2

                Iest1 = CT / CL * \
                        sum(
                            abs(
                                Etwf[2:] - 2 * Etwf[1:-2] + Etwf[1:-3]
                            )
                        ) / 24

                Iest2 = 1 / CT * \
                        sum(
                            abs(
                                Etwf[2:] - 2 * Etwf[1:-2] + Etwf[1:-3]
                            )
                        ) / 24

                Eest = 1 / CT * sum(Efwt)
                perr = inf

                while (abs(Etot - Eest) + Iest1 + Iest2) / Etot <= perr:
                    CT *= 2
                    perr = (abs(Etot - Eest) + Iest1 + Iest1) / Etot
                    CNq = ceil((CL + 1) / 2)
                    ct = CT / CL * arange(CNq - CL, CNq - 1).conj().T

                    idm = nonzero(ct <= max([wp.t1, 0]))
                    idc = nonzero((ct > max([wp.t1, 0])) & (ct < wp.t2))

                    idp = nonzero(ct >= wp.t2)

                    if not isempty(idnan):
                        idnorm = nonzero(~isnan(Ctwf))
                        Ctwf[idnan] = interp1(idnan, Ctwf[idnorm], idnan)

                    Cfwt = CL / CT * fft(
                        Ctwf[concat([arange(CL - CNq + 1, CL), arange(1, CL - CNq)])]
                    )
                    Cfwt = Cfwt[concat([arange(CNq + 1, CL), arange(1, CNq)])]

                    Etwf = abs(Ctwf) ** 2
                    Efwt = abs(Cfwt) ** 2

                    Iest1 = CT / CL * sum(abs(Etwf[3:] - 2 * Etwf[2:-1] + Etwf[1:-2])) / 24
                    Iest2 = 1 / CT * sum(abs(Efwt[3:] - 2 * Efwt[2:-1] + Efwt[1:-2])) / 24
                    Eest = 1 / CT * sum(Efwt)

                CL = 16 * CL
                CT *= 2

                CNq = ceil((CL + 1) / 2)
                ct = CT / CL * arange(CNq - CL, CNq - 1).conj().T

                idm = nonzero(ct <= wp.t1)
                idc = nonzero((ct > wp.t1) & (ct < wp.t2))
                idp = nonzero(ct >= wp.t2)

                Ctwf = asarray([
                    zeros((len(idm), 1)),
                    twf(ct[idc]),
                    zeros((len(idp), 1,))
                ])
                idnan = nonzero(isnan(Ctwf))

                if not isempty(idnan):
                    idnorm = nonzero(~isnan(Ctwf))
                    Ctwf[idnan] = interp1(idnorm, Ctwf(idnorm), idnan)

                Cfwt = CT / CL * fft(Ctwf[
                                         concat([
                                             arange(CL - CNq + 1, CL),
                                             arange(1, CL - CNq)
                                         ])
                                     ])

                Etwf = abs(Ctwf) ** 2
                Efwt = abs(Cfwt[
                               concat([
                                   arange(CNq + 1, CL),
                                   arange(1, CNq)
                               ])
                           ]) ** 2

                Iest1 = CT / CL * \
                        sum(
                            abs(
                                Etwf[2:] - 2 * Etwf[1:-2] + Etwf[1:-3]
                            )
                        ) / 24

                Iest2 = 1 / CT * \
                        sum(
                            abs(
                                Etwf[2:] - 2 * Etwf[1:-2] + Etwf[1:-3]
                            )
                        ) / 24

                Eest = 1 / CT * sum(Efwt)

                if (abs(Etot - Eest) + Iest1 + Iest2) / Etot > 0.01:
                    print("WARNING: Cannot accurately invert the specified time-domain form...")

                Cfwt = Cfwt[1:CNq]
                cxi = twopi / CT * arange(1, CNq - 1).conj().T

                if 2 * abs(CT / CT * sum(Ctwf)) < ctol:
                    Atot = abs(twopi / CT * sum(Cfwt / cxi))
                    cxi0 = cxi[0]
                    Cfwt0 = CT / CL * sum(Ctwf * exp(-1j * cxi0 * ct))
                    axi = NAN * zeros((CL, 1,))
                    Afwt = NAN * zeros((CL, 1,))
                    kn = 1

                    while 2 * abs(Cfwt0) / Atot > ctol:
                        cxi0 /= 2
                        Cfwt0 = CT / CL * sum(Ctwf * exp(-1j * cxi0 * ct))
                        axi[kn] = cxi0
                        Afwt[kn] = Cfwt0
                        kn += 1
                    axi = axi[0:kn - 1]
                    Afwt = Afwt[0:kn - 1]

                else:
                    ix = min([
                        1 + nonzero(np.diff(abs(Cfwt[1:])) <= 0)[0],
                        len(Cfwt)
                    ])
                    cxi0 = interp1(
                        asarray([
                            0,
                            abs(Cfwt[:ix]),
                        ]),
                        asarray([
                            0,
                            cxi[:ix]
                        ]),
                        ctol
                    )
                    axi = []
                    Afwt = []
                C50 = interp1(
                    asarray([0, cxi]),
                    asarray(0, Cfwt),
                    cxi0 / 4
                )

                imxi = argmax(abs(Cfwt))

                bxi1 = linspace(log(cxi0), log(cxi[0]), ceil(2 * CL / 3)).conj().T
                zxi1 = (bxi1[:-2] + bxi1[1:]) / 2

                bxi2 = linspace(log(cxi[0]), log(cxi[imxi]), ceil(2 * CL / 3)).conj().T
                zxi2 = (bxi2[:-2] + bxi2[1:]) / 2

                bxi3 = linspace(log(cxi0), log(cxi[0]), ceil(2 * CL / 3)).conj().T
                zxi3 = (bxi3[:-2] + bxi3[1:]) / 2

                zxi = asarray([zxi1, zxi2, zxi3])
                bxi = asarray([bxi1[:-2], bxi2[:-2], bxi3])
                dbxi = np.diff(bxi)

                Zfwt = interp1(
                    asarray([0, axi, cxi]),
                    asarray([0, Afwt, Cfwt]),
                    exp(zxi)
                )
                wp.fwt = [Zfwt, exp(zxi)]

                # Estimate general parameters
                if isempty(wp.ompeak):
                    ipeak = nonzero(abs(Zfwt) == max(abs(Zfwt)))
                    if len(ipeak) == 1:
                        a1 = abs(Zfwt[ipeak - 1])
                        a2 = abs(Zfwt[ipeak])
                        a3 = abs(Zfwt[ipeak + 1])

                        wp.ompeak = zxi[ipeak]
                        if abs(a1 - 2 * a2 + a3) > 2 * eps:
                            wp.ompeak *= wp.ompeak + 0.5 * (a1 - a3) / (a1 - 2 * a2 + a3) * dbxi[ipeak]

                    else:
                        wp.ompeak = mean(zxi[ipeak])
                    wp.ompeak = exp(wp.ompeak)

                if isempty(wp.fwtmax):
                    ipeak = argmin(abs(cxi - wp.ompeak))
                    wp.fwtmax = interp1(
                        cxi[ipeak - 1:ipeak + 1],
                        abs(Cfwt[ipeak - 1:ipeak + 1]),
                        wp.ompeak
                    )

                if isempty(wp.C):
                    wp.C = 0.5 * sum(Zfwt.conj() * dbxi)
                if isempty(wp.D):
                    wp.D = inf
                    if abs(Zfwt[1] / Zfwt[0]) > exp(zxi[1] - zxi[0]):
                        wp.D = wp.ompeak / 2 * sum(exp(-zxi) * (Zfwt.conj() * dbxi))

                # Calculate cumulative integrals.
                CS = C50 + cumsum(Zfwt * dbxi)
                CS = asarray([C50, CS[:]]) / CS[-1]
                CS = abs(CS)

                ICS = cumsum(np.flipud(Zfwt * dbxi))
                ICS = ICS[-1:0:-1]
                ICS = asarray([
                    ICS[:],
                    0
                ]) / (ICS[2] + C50)
                ICS = abs(ICS)

                # Estimate epsilon supports.
                xid = nonzero((CS[:-2] < racc / 2) & (CS[1:] >= racc / 2))[0]
                if isempty(xid):
                    wp.xi1e = exp(bxi[0])
                else:
                    a1 = CS[xid] - racc / 2
                    a2 = CS[xid + 1] - racc / 2
                    wp.xi1e = exp(bxi[xid]) - a1 * (bxi[xid + 1] - bxi[xid]) / (a2 - a1)

                xid = nonzero((ICS[:-2] < racc / 2) & (ICS[1:] >= racc / 2))[-1]
                if isempty(xid):
                    wp.xi2e = exp(bxi[-1])
                else:
                    a1 = ICS[xid] - racc / 2
                    a2 = ICS[xid + 1] - racc / 2
                    wp.xi2e = exp(bxi[xid]) - a1 * (bxi[xid + 1] - bxi[xid]) / (a2 - a1)

                xid = nonzero((CS[:-2] < .25) & (CS[1:] >= .25))[0]
                if isempty(xid):
                    wp.xi1h = exp(bxi[0])
                else:
                    a1 = CS[xid] - .25
                    a2 = CS[xid + 1] - .25
                    wp.xi1h = exp(bxi[xid]) - a1 * (bxi[xid + 1] - bxi[xid]) / (a2 - a1)

                xid = nonzero((ICS[:-2] >= .25) & (ICS[1:] < .25))[-1]
                if isempty(xid):
                    wp.xi2h = exp(bxi[-1])
                else:
                    a1 = ICS[xid] - .25
                    a2 = ICS[xid + 1] - .25
                    wp.xi2h = exp(bxi[xid]) - a1 * (bxi[xid + 1] - bxi[xid]) / (a2 - a1)

            # Return to the time-domain form
            vfun = lambda u: (twf(u) * exp(-1j * wp.ompeak * u)).conj()
            xp = wp.tpeak
            lim1 = wp.t1
            lim2 = wp.t2

            QQ, wflag, xx, ss = sqeps(vfun, xp, lim1, lim2, racc, MIC,
                                      8 * twopi * fmax / wp.ompeak * L / fs * np.asarray([-1, 1])
                                      )

            wp.t1e = ss[0, 0]
            wp.t2e = ss[0, 1]
            wp.t1h = ss[1, 0]
            wp.t2h = ss[1, 1]

            if wflag == 1:
                print("WARNING: The time-domain wavelet function is not well behaved...")


def sqeps(vfun, xp, lim1, lim2, racc, MIC, nlims):
    wflag = 0  # Indicates issues with integration.
    ctol = np.max([racc / 1000, 10 ** -12])
    nlim1, nlim2 = nlims

    kk = 1
    shp = 0  # Peak shift - changed from 0 because of scipy algorithm behaving differently to Matlab.

    while not np.isfinite(vfun(xp + shp) or isnan(vfun(xp + shp))):
        shp = kk * (10 ** -14)
        #print(shp, vfun(xp + shp))
        kk *= -2

    vmax = vfun(xp + shp)

    if isfinite(lim1):
        tx1 = lim1 - 0.01 * (lim1 - xp)
        qv1 = abs(vfun(tx1) / vmax)
    else:
        qv1 = NAN

    if qv1 < 0.5:
        #x1h = scipy.optimize.fsolve(func=lambda x: abs(vfun(x) / vmax) - 0.5, x0=asarray([xp + shp, tx1],dtype=np.float))  # level2
        x1h = scipy.optimize.brentq(f=lambda x: abs(vfun(x) / vmax) - 0.5, a=xp + shp, b=tx1)  # level2
    elif np.isnan(qv1):
        x1h = scipy.optimize.fsolve(func=lambda x: abs(vfun(xp - np.abs(x)) / vmax) - 0.5, x0=shp or 0.1)  # level2
        x1h = xp - np.abs(x1h)
    else:
        x1h = xp + (lim1 - xp) / 100

    if np.isfinite(lim2):
        tx2 = lim2 - 0.01 * (lim2 - xp)
        qv2 = np.abs(vfun(tx2) / vmax)
    else:
        qv2 = np.NaN

    if qv2 < 0.5:
        x2h = scipy.optimize.brentq(f=lambda u: np.abs(vfun(u) / vmax) - 0.5, a=xp + shp, b=tx2)
    elif np.isnan(qv2):
        x2h = scipy.optimize.fsolve(func=lambda u: np.abs(vfun(xp + np.abs(u)) / vmax) - 0.5, x0=shp or 0.1)
        x2h = xp + np.abs(x2h)
    else:
        x2h = xp + (lim2 - xp) / 100

    if isnan(x1h).all():
        x1h = scipy.optimize.fmin(func=lambda u: np.abs(np.abs(vfun(xp - np.abs(u)) / vmax)) - 0.5, x0=shp,
                                  ftol=10 ** -12)
        x1h = xp - np.abs(x1h) / 100

    if not np.isscalar(x1h): # and len(x1h) > 1:  # Added
        x1h = min(x1h)

    if np.isnan(x2h):
        x2h = scipy.optimize.fmin(func=lambda u: np.abs(np.abs(vfun(xp + np.abs(u)) / vmax) - 0.5), x0=shp,
                                  ftol=10 ** -12)
        x2h = xp + np.abs(x2h) / 100

    if np.isfinite(lim1):
        tx1 = lim1 - 0.01 * (lim1 - xp)
        qv1 = (
                      np.abs(vfun(tx1)) + np.abs(vfun((tx1 + lim1) / 2)) + np.abs(vfun((tx1 + 3 * lim1) / 4))
              ) / np.abs(vmax)
    else:
        qv1 = np.NaN

    if qv1 < 10 ** (-8) / 3:
        x1e = scipy.optimize.brentq(
            f=lambda u: np.abs(vfun(u) / vmax) + np.abs(vfun((u + lim1) / 2) / vmax) + np.abs(
                vfun((u + 3 * lim1) / 4) / vmax) - 10 ** (-8), a=xp + shp, b=tx1)
    elif np.isnan(qv1):
        x1e = scipy.optimize.fsolve(
            func=
            lambda u: (
                    np.abs(vfun(xp - np.abs(u)) / vmax)
                    + np.abs(vfun(xp - np.sqrt(3) * np.abs(u)) / vmax)
                    + np.abs(vfun(xp - np.sqrt(5) * np.abs(u)) / vmax)
                    - 10 ** (-8)
            ),
            x0=shp or 0.1)

        x1e = xp - np.abs(x1e)

    else:
        x1e = xp + (lim1 - xp) / 2

    if not np.isscalar(x1e): #len(x1e) > 1:
        x1e = min(x1e)

    if np.isfinite(lim2):
        tx2 = lim2 - 0.01 * (lim2 - xp)
        qv2 = (abs(vfun(tx2)) + abs(vfun((tx2 + lim2) / 2)) + abs(vfun((tx2 + 3 * lim2) / 4))) / abs(vmax)
    else:
        qv2 = np.NaN

    if qv2 < 10 ^ (-8):
        x2e = scipy.optimize.brentq(
            func=lambda u: np.abs(vfun(u) / vmax) + np.abs(vfun((u + lim2) / 2) / vmax) + np.abs(
                vfun((u + 3 * lim2) / 4) / vmax) - 10 ** (-8), a=xp + shp, b=tx2)
    elif np.isnan(qv2):
        x2e = scipy.optimize.fsolve(
            func=lambda u: abs(vfun(xp + abs(u)) / vmax) + abs(vfun(xp + np.sqrt(3) * abs(u)) / vmax) + abs(
                vfun(xp + np.sqrt(5) * np.abs(u)) / vmax) - 10 ** (-8), x0=shp or 0.1)

        x2e = xp + abs(x2e)

    else:
        x2e = xp + (lim2 - xp) / 2

    if isnan(x1e).all():
        x1e = scipy.optimize.fmin(func=lambda u: abs(abs(vfun(x1h - abs(u)) / vmax) - 10 ** (-8)), x0=0)
        x1e = x1h - abs(x1e)
        lim1 = x1e
        wflag = 1
    if np.isnan(x2e):
        x2e = scipy.optimize.fmin(func=lambda u: abs(abs(vfun(x2h + abs(u)) / vmax) - 10 ** (-8)), x0=0)
        x2e = x2h + abs(x2e)
        lim2 = x2e
        wflag = 1

    ##### Integrate given function to find Q1 and Q2. #####
    Q1 = 0
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

    Q1 += q1m
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
        if not np.isfinite(lim2) and np.isnan(qv):  # avoid overflow
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

    QQ = np.asarray([[Q1, Q2], [-q1m, q2m]], dtype=np.complex64)
    xx = np.asarray((
        [x1e, x2e],
        [x1h, x2h],
        [x1m, x2m],
        [lim1, lim2]
    ), dtype=np.float64)

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

                if nx < lim1:
                    nx = (cx1 + lim1) / 2
                if nx > lim2:
                    nx = (cx1 + lim2) / 2

                pv, _ = quadgk(vfun, cx1, nx, limit=MIC, epsabs=0.1 * abs(ctol * Q), epsrel=0)
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
                pv, _ = quadgk(vfun, cx1, nx, limit=MIC, epsabs=0.1 * abs(ctol * Q), epsrel=0)
                if abs(1 - abs((Q - cq1 - pv) / Q)) < zv:
                    cx2 = nx
                    cq2 = cq1 + pv
                    break
                cx1 = nx
                cq1 = cq1 + pv

        pv, _ = quadgk(vfun, cx1, (cx1 + cx2) / 2, limit=MIC, epsabs=0.1 * abs(ctol * Q), epsrel=0)

        _qfun = lambda u: quadgk(vfun, (cx1 + cx2) / 2, u, limit=int(np.round(MIC / 10)),
                                 epsabs=0.5 * abs(ctol * Q), epsrel=0)[0]

        qfun = lambda x: 1 - abs((Q - (cq1 + pv + _qfun(x))) / Q)

        x0 = scipy.optimize.fsolve(lambda x: abs(qfun(x)) - zv,
                                   x0=(cx1 + cx2) / 2, xtol=10 ** -14)  # Modified to use average of cx1 and cx2.
        return x0

    s1e = fz(racc / 2)
    s2e = fz(1 - racc / 2)
    s1h = fz(0.5 / 2)
    s2h = fz(1 - 0.5 / 2)
    ss = np.asarray([
        [s1e, s2e],
        [s1h, s2h]]
    )

    return QQ, wflag, xx, ss


def fcast(sig, fs, NP, fint, *args):  # line1145
    MaxOrder = len(sig)

    if len(args) > 0:
        MaxOrder = args[0] or MaxOrder

    w = []
    if len(args) > 1:
        w = np.asarray(args[1], dtype=np.float64)

    rw = np.sqrt(w)

    WTol = 10 ** -8  # tolerance for cutting weighting.
    Y = sig[:]
    if not isempty(rw):
        Y = rw * Y

    L = nonzero(np.flipud(rw) / max(rw) >= WTol)[1][-1]

    T = (L + 1) / fs
    t = arange(0, L + 1) / fs

    w = w[-L - 1:]  # level3
    rw = rw[-L - 1:]  # level3
    Y = Y[-L - 1:]  # level3

    MaxOrder = np.min([MaxOrder, np.floor(L + 1 / 3)])

    FTol = 0.01 / T
    rr = (1 + np.sqrt(5)) / 2
    Nq = np.ceil((L + 1) / 2)
    ftfr = np.concatenate([np.arange(0, Nq), -np.flip(np.arange(1, L - Nq + 1))]) * fs / L
    orstd = np.std(Y)

    v = np.zeros(L, dtype=np.float64)
    ic = v
    frq = v
    amp = v
    phi = v
    itn = 0

    while itn < MaxOrder:
        itn += 1
        aftsig = abs(fft(Y, axis=0))

        aftsig = aftsig.reshape(aftsig.shape[1])
        Nq = int(Nq)

        imax = argmax(aftsig[1:Nq - 1])
        imax += 1

        # Forward search
        nf = ftfr[imax]

        FM1 = np.ones((L + 1, 1,), dtype=np.float64)
        FM2 = np.cos(2 * np.pi * nf * t.reshape(len(t), 1))
        FM3 = np.sin(2 * np.pi * nf * t.reshape(len(t), 1))
        FM = hstack([FM1, FM2, FM3])

        if not isempty(rw):
            FM = FM * (rw.T * np.ones((1, 3)))

        nb = backslash(FM, Y.T)  # level3

        s = FM @ nb
        nerr = np.std(Y - s)

        df = FTol
        perr = np.inf
        while nerr < perr:
            if abs(nf - fs / 2 + FTol) < eps:  # level3 eps
                break

            pf = nf
            perr = nerr
            pb = nb
            nf = min([pf + df, fs / 2 - FTol])

            FM1 = np.ones(L + 1, dtype=np.float64)
            FM2 = np.cos(2 * np.pi * nf * t)
            FM3 = np.sin(2 * np.pi * nf * t)
            FM = np.asarray([FM1, FM2, FM3], dtype=np.float64)

            if not isempty(rw):
                FM = FM.T * (rw.T * np.ones((1, 3)))

            nb = backslash(FM, Y.T)  # level3
            nerr = np.std(Y - s)
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
            cb = np.array([np.zeros((len(pb), 1)), pb, nb]).squeeze()
            cf[1] = pf - df / rr / rr
            FM = np.array([np.ones((L+1, )), np.cos(2 * np.pi * cf[1] * t), np.sin(2 * np.pi * cf[1] * t)]).T
            if not isempty(rw):
                FM = FM * (rw.T * np.ones((1, 3)))
            temp_res = np.linalg.lstsq(FM, Y.T,rcond=None)  # level3
            cb[1] = temp_res[0].squeeze()
            cerr[1] = np.std(Y.T - FM * cb[1])

        while (cf[1] - cf[0] > FTol and cf[2] - cf[1] > FTol):
            tf = cf[0] + cf[2] - cf[1]
            FM = [np.ones(L+1, 1), np.cos(2 * np.pi * tf * t), np.sin(2 * np.pi * tf * t)]
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

        if not isempty(rw):
            FM = FM * np.ones((1, 3))

        nb = backslash(FM, Y.T)  # level3

        s = FM @ nb
        nerr = np.std(Y - s)

        df = FTol
        perr = np.inf
        while nerr < perr:
            if abs(nf - FTol) < eps:
                break
            pf = nf
            perr = nerr
            pb = nb
            nf = np.max([pf - df, FTol])

            FM1 = np.ones(L + 1, dtype=np.float64)
            FM2 = np.cos(2 * np.pi * nf * t)
            FM3 = np.sin(2 * np.pi * nf * t)
            FM = np.asarray([FM1, FM2, FM3], dtype=np.float64)

            if not isempty(rw):
                FM = FM.T * (rw.T * np.ones((1, 3)))

            nb = backslash(FM, Y.T)
            nerr = np.std(Y - FM @ nb)
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
            cb = [np.zeros((len(pb), 1)), pb, nb]
            cf[1] = pf - df / rr / rr

            FM1 = np.ones(L + 1, dtype=np.float64)
            FM2 = np.cos(2 * np.pi * nf * t)
            FM3 = np.sin(2 * np.pi * nf * t)
            FM = np.asarray([FM1, FM2, FM3], dtype=np.float64)

            if not isempty(rw):
                FM = FM.T * (rw.T * np.ones((1, 3)))

            cb[1] = backslash(FM, Y.T)  # level3
            cerr[1] = np.std(Y - FM @ cb[1])

        while (cf[2] - cf[1] > FTol and cf[3] - cf[2] > FTol):
            tf = cf[1] + cf[3] - cf[2]
            FM = [np.ones(L, 1), np.cos(2 * np.pi * tf * t), np.sin(2 * np.pi * tf * t)]
            if not isempty(rw):
                FM = FM * (rw * np.ones(1, 3))
            tb = np.linalg.lstsq(FM, Y)
            terr = np.std(Y - FM * tb)

            if terr < cerr[2] and tf < cf[2]:  # TODO: fix all indices
                cf = [cf[1], tf, cf[2]]
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
        amp[itn + 1] = np.sqrt(cb[1] ** 2 + cb[2] ** 2)
        phi[itn + 1] = np.arctan2(-cb[2], cb[1])
        amp[1] = amp[0] + cb[0]
        v[itn] = cerr

        FM1 = np.ones(L + 1, dtype=np.float64)
        FM2 = np.cos(2 * np.pi * nf * t)
        FM3 = np.sin(2 * np.pi * nf * t)
        FM = np.asarray([FM1, FM2, FM3], dtype=np.float64)

        # if not isempty(rw):
        #     temp = rw.reshape(len(rw), 1) * np.ones((1, 3), dtype=np.float64)
        #     FM = FM.transpose() * temp

        if not isempty(rw):
            FM = FM.T * (rw.T * np.ones((1, 3)))
            Y = Y - FM @ cb

        CK = 3 * itn + 1
        cic = L * np.log(cerr) + CK * np.log(L)

        ic[itn] = cic
        if v[itn] / orstd < 2 * eps:
            break
        if itn > 2 and cic > ic[itn - 1] and cic[itn - 1] > ic[itn - 2]:
            break

    frq = frq[1:itn + 1]
    amp = amp[1:itn + 1]
    phi = phi[1:itn + 1]
    v = v[1:itn]
    ic = ic[1:itn]

    fsig = zeros(np.int(NP))
    nt = (np.arange(T, T + (np.int(NP) - 1), 1 / fs) / fs).T

    if (sig.shape[1] if len(sig.shape) > 1 else 1) > sig.shape[0]:
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

    w, f = wft(signal, fs)

    plt.pcolormesh(t, f, np.abs(w))
    plt.show()
