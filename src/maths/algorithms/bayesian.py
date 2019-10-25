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

"""
Translation of the MODA Bayesian inference algorithm into Python.

STATUS: Finished, but not working. Current issue: `filtfilt` in `loop_butter` is
not giving accurate results.
"""


def bayes_main(ph1, ph2, win, h, ovr, pr, s, bn):
    win /= h

    w = ovr * win
    ps = ph2 - ph1
    pw = win * h * pr

    M = 2 + 2 * ((2 * bn + 1) ** 2 - 1)
    L = 2

    M = np.int(M)
    Cpr = zeros((int(M / L), L))
    XIpr = zeros((M, M))

    if max(ph1) < twopi + 0.1:
        ph1 = np.unwrap(ph1)
        ph2 = np.unwrap(ph2)

    if len(ph1.shape) > 1:
        m, n = ph1.shape
    else:
        m = ph1.shape[0]
        n = 1

    if m < n:
        ph1 = ph1.conj().T
        ph2 = ph2.conj().T

    s = np.int(ceil((len(ps) - win) / w))
    e = zeros((s, s, s))

    w = np.int(w)
    win = np.int(win)

    r = np.int(np.floor((len(ps) - win) / w)) + 1
    cc = zeros((r, Cpr.size))
    for i in range(r):
        phi1 = ph1[i * w : i * w + win]
        phi2 = ph2[i * w : i * w + win]

        Cpt, XIpt, E = bayesPhs(
            Cpr, XIpr, h, 500, 1e-5, phi1.conj().T, phi2.conj().T, bn
        )

        XIpr, Cpr = Propagation_function_XIpt(Cpt, XIpt, pw)

        e[i, :, :] = E
        cc[i, :] = concat([Cpt[:, i] for i in range(Cpt.shape[1])])

    tm = arange(win / 2, len(ph1) - win / 2, w) * h

    return tm, cc, e


def Propagation_function_XIpt(Cpt, XIpt, p):
    Cpr = Cpt

    Inv_Diffusion = zeros((len(XIpt), len(XIpt)))
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
    bn = np.int(bn)
    K = np.int(K)

    p = zeros((K, len(phi1)))

    p[0, :] = 1
    br = 1

    for i in range(1, bn + 1):
        p[br, :] = sin(i * phi1)
        p[br + 1, :] = cos(i * phi1)

        br += 2

    for i in range(1, bn + 1):
        p[br, :] = sin(i * phi2)
        p[br + 1, :] = cos(i * phi2)
        br += 2

    for i in range(1, bn + 1):
        for j in range(1, bn + 1):
            p[br, :] = sin(i * phi1 + j * phi2)
            p[br + 1, :] = cos(i * phi1 + j * phi2)
            br += 2

            p[br, :] = sin(i * phi1 - j * phi2)
            p[br + 1, :] = cos(i * phi1 - j * phi2)
            br += 2

    return p


def calculateV(phi1, phi2, K, bn, mr):
    bn = np.int(bn)
    K = np.int(K)
    v = zeros((K, len(phi1)))

    br = 1

    if mr == 1:
        for i in range(1, bn + 1):
            v[br, :] = i * cos(i * phi1)
            v[br + 1, :] = -i * sin(i * phi1)

            br += 2

        for i in range(1, bn + 1):
            v[br, :] = 0
            v[br + 1, :] = 0
            br += 2

        for i in range(1, bn + 1):
            for j in range(1, bn + 1):
                v[br, :] = i * cos(i * phi1 + j * phi2)
                v[br + 1, :] = -i * sin(i * phi1 + j * phi2)
                br += 2

                v[br, :] = i * cos(i * phi1 - j * phi2)
                v[br + 1, :] = -i * sin(i * phi1 - j * phi2)
                br += 2
    else:
        for i in range(1, bn + 1):
            v[br, :] = 0
            v[br + 1, :] = 0

            br += 2

        for i in range(1, bn + 1):
            v[br, :] = i * cos(i * phi2)
            v[br + 1, :] = -i * sin(i * phi2)

            br += 2

        for i in range(1, bn + 1):
            for j in range(1, bn + 1):
                v[br, :] = j * cos(i * phi1 + j * phi2)
                v[br + 1, :] = -j * sin(i * phi1 + j * phi2)
                br += 2

                v[br, :] = -j * cos(i * phi1 - j * phi2)
                v[br + 1, :] = j * sin(i * phi1 - j * phi2)
                br += 2

    return v


def calculateE(c, phiT, L, h, p):
    E = zeros((L, L))

    mul = np.matmul(c, p)
    sub = phiT - mul
    E += np.matmul(sub, sub.conj().T)
    E = (h / len(phiT[0, :])) * E

    return E


def calculateC(E, p, v1, v2, Cpr, XIpr, M, L, phiT, h):
    K = M / L
    invr = np.linalg.inv(E)

    K = np.int(K)
    M = np.int(M)

    XIpt = zeros((M, M))
    Cpt = zeros(Cpr.shape)

    mul = matmul(p, p.conj().T)

    XIpt[:K, :K] = XIpr[:K, :K] + h * invr[0, 0] * mul
    XIpt[:K, K : 2 * K] = XIpr[:K, K : 2 * K] + h * invr[0, 1] * mul
    XIpt[K : 2 * K, :K] = XIpr[K : 2 * K, :K] + h * invr[1, 1] * mul
    XIpt[K : 2 * K, K : 2 * K] = XIpr[K : 2 * K, K : 2 * K] + h * invr[1, 1] * mul

    # Evaluate from temp r.
    r = zeros((K, L))
    ED = backslash(E, phiT)

    sum_v1 = sum(v1, axis=1)
    # sum_v1 = sum_v1.reshape(len(sum_v1), 1)

    r[:, 0] = (
        matmul(XIpr[:K, :K], Cpr[:, 0])
        + matmul(XIpr[:K, K : 2 * K], Cpr[:, 1])
        + h * (matmul(p, ED[0, :].conj().T) - 0.5 * sum_v1)
    )

    r[:, 1] = (
        matmul(XIpr[K : 2 * K, :K], Cpr[:, 0])
        + matmul(XIpr[K : 2 * K, K : 2 * K], Cpr[:, 1])
        + h * (matmul(p, ED[1, :].conj().T) - 0.5 * sum_v1)
    )

    C = backslash(XIpt, concat([r[:, 0], r[:, 1]])).conj().T
    Cpt[:, 0] = C[:K]
    Cpt[:, 1] = C[K : 2 * K]

    return Cpt, XIpt


def dirc(c, bn):
    q1 = zeros((bn * 8,))
    q2 = zeros(q1.shape)
    iq1 = 0
    iq2 = 0
    br = 1
    K = np.int(len(c) / 2)

    if is_arraylike(c[0]):
        c = c[0]

    for ii in range(bn):
        q1[iq1] = c[br]
        iq1 = iq1 + 1
        q1[iq1] = c[br + 1]
        iq1 = iq1 + 1
        q2[iq2] = c[K + br]
        iq2 = iq2 + 1
        q2[iq2] = c[K + br + 1]
        iq2 = iq2 + 1
        br = br + 2

    for ii in range(bn):
        q1[iq1] = c[br]
        iq1 = iq1 + 1
        q1[iq1] = c[br + 1]
        iq1 = iq1 + 1
        q2[iq2] = c[K + br]
        iq2 = iq2 + 1
        q2[iq2] = c[K + br + 1]
        iq2 = iq2 + 1
        br = br + 2

    for jj in range(bn):
        for ii in range(bn):
            q1[iq1] = c[br]
            iq1 = iq1 + 1
            q1[iq1] = c[br + 1]
            iq1 = iq1 + 1
            q2[iq2] = c[K + br]
            iq2 = iq2 + 1
            q2[iq2] = c[K + br + 1]
            iq2 = iq2 + 1
            br = br + 2

    cpl1 = np.linalg.norm(q1)
    cpl2 = np.linalg.norm(q2)
    drc = (cpl2 - cpl1) / (cpl1 + cpl2)

    return cpl1, cpl2, drc


def CFprint(cc, bn):
    t1 = arange(0, twopi, 0.13)
    t2 = arange(0, twopi, 0.13)

    q1 = zeros((len(t1), len(t1)))
    q1[: len(t1), : len(t1)] = 0

    q2 = np.copy(q1)

    u = cc
    K = np.int(len(u) / 2)

    for i1 in range(len(t1)):
        for j1 in range(len(t2)):
            br = 1

            for ii in range(1, bn + 1):
                q1[i1, j1] = (
                    q1[i1, j1] + u[br] * sin(ii * t1[i1]) + u[br + 1] * cos(ii * t1[i1])
                )
                q2[i1, j1] = (
                    q2[i1, j1]
                    + u[K + br] * sin(ii * t2[j1])
                    + u[K + br + 1] * cos(ii * t2[j1])
                )

                br += 2

            for ii in range(1, bn + 1):
                q1[i1, j1] = (
                    q1[i1, j1] + u[br] * sin(ii * t2[j1]) + u[br + 1] * cos(ii * t2[j1])
                )
                q2[i1, j1] = (
                    q2[i1, j1]
                    + u[K + br] * sin(ii * t1[i1])
                    + u[K + br + 1] * cos(ii * t1[i1])
                )

                br += 2

            for ii in range(1, bn + 1):
                for jj in range(1, bn + 1):
                    q1[i1, j1] = (
                        q1[i1, j1]
                        + u[br] * sin(ii * t1[i1] + jj * t2[j1])
                        + u[br + 1] * cos(ii * t1[i1] + jj * t2[j1])
                    )

                    q2[i1, j1] = (
                        q2[i1, j1]
                        + u[K + br] * sin(ii * t1[i1] + jj * t2[j1])
                        + u[K + br + 1] * cos(ii * t1[i1] + jj * t2[j1])
                    )

                    br += 2

                    q1[i1, j1] = (
                        q1[i1, j1]
                        + u[br] * sin(ii * t1[i1] - jj * t2[j1])
                        + u[br + 1] * cos(ii * t1[i1] - jj * t2[j1])
                    )

                    q2[i1, j1] = (
                        q2[i1, j1]
                        + u[K + br] * sin(ii * t1[i1] - jj * t2[j1])
                        + u[K + br + 1] * cos(ii * t1[i1] - jj * t2[j1])
                    )

                    br += 2

    return t1, t2, q1, q2
