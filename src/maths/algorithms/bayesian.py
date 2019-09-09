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
from maths.algorithms.matlab_utils import *


def bayes_main(ph1, ph2, win, h, ovr, pr, s, bn):
    cc = []
    win /= h

    w = ovr * win
    ps = ph2 - ph1
    pw = win * h * pr

    M = 2 + 2 * ((2 * bn + 1) ** 2 - 1)
    L = 2

    Cpr = zeros((M / L, L,))
    XIpr = zeros(M)

    if (max(ph1) < twopi + 0.1):
        ph1 = np.unwrap(ph1)
        ph2 = np.unwrap(ph2)

    m, n = ph1.shape
    if m < n:
        ph1 = ph1.conj().T
        ph2 - ph2.conj().T

    s = ceil((len(ps) - win) / w)
    e = zeros((s, s, s,))

    for i in range(len(np.floor((len(ps) - win) / w))):
        phi1 = ph1[i * w: i * w * win]
        phi2 = ph2[i * w: i * w * win]

        Cpt, XIpt, E = bayesPhs(Cpr, XIpr, h, 500, 1e-5, phi1.conj().T, phi2.conj().T, bn)

        XIpr, Cpr = Propagation_function_XIpt(Cpt, XIpt, pw)

        e[i, :, :] = E
        cc[i, :] = Cpt[:]

    tm = arange(win / 2, len(ph1) - win / 2, w) * h

    return tm, cc, e


def Propagation_function_XIpt(Cpt, XIpt, p):
    Cpr = Cpt

    Inv_Diffusion = zeros((len(XIpt), len(XIpt),))
    invXIpt = np.linalg.inv(XIpt)

    for i in range(len(Cpt[:])):
        Inv_Diffusion[i, i] = p ** 2 * invXIpt[i, i]

    XIpr = np.linalg.inv(invXIpt + Inv_Diffusion)

    return XIpr, Cpr


def bayesPhs(Cpr, XIpr, h, max_loops, eps, phi1, phi2, bn):
    phi1S = (phi1[1:] + phi1[:-1]) / 2
    phi2S = (phi2[1:] + phi2[:-1]) / 2

    phi1T = (phi1[1:] - phi1[:-1]) / h
    phi2T = (phi2[1:] - phi2[:-1]) / h

    phiT = asarray([phi1T, phi2T])

    L = 2
    M = 2 + 2 * ((2 * bn + 1) ** 2 - 1)
    K = M / L

    p = calculateP(phi1S, phi2S, K, bn)
    v1 = calculateV(phi1S, phi2S, K, bn, 1)
    v2 = calculateV(phi1S, phi2S, K, bn, 2)

    C_old = Cpr
    Cpt = Cpr

    for loop in range(max_loops):
        E = calculateE(Cpt.conj().T, phiT, L, h, p)
        Cpt, XIpt = calculateC(E, p, v1, v2, Cpr, XIpr, M, L, phiT, h)

        if sum((C_old - Cpt) * (C_old - Cpt) / (Cpt ** 2)) < eps:
            return Cpt, XIpt, E

        C_old = Cpt

    return Cpt, XIpt, E


def calculateP(phi1, phi2, K, bn):
    p = zeros((bn, bn,))

    p[K, len(phi1)] = 0

    p[0, :] = 1
    br = 1

    for i in range(1, bn + 1):
        p[br, :] = sin(i * phi1)
        p[br + 1, :] = cos(i * phi1)

        br += 2

    for i in range(1, bn):
        p[br, :] = sin(i * phi2)
        p[br + 1, :] = cos(i * phi2)
        br += 2

    for i in range(1, bn):
        for j in range(1, bn):
            p[br + 1, :] = sin(i * phi1 + j * phi2)
            p[br + 2, :] = cos(i * phi1 + j * phi2)
            br = br + 2

            p[br + 1, :] = sin(i * phi1 - j * phi2)
            p[br + 2, :] = cos(i * phi1 - j * phi2)
            br = br + 2

    return p


def calculateV(phi1, phi2, K, bn, mr):
    v = zeros((bn, bn,))

    v[K, len(phi1)] = 0
    br = 1

    if mr == 1:
        for i in range(1,bn):
            pass # TODO: continue later

    return v
