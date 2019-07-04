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

"""
DO NOT import this module in the main process, or it will break Linux support.
"""
import string

import args

args.setup_matlab_runtime()  # Don't move this.

import WFT
import matlab

package = WFT.initialize()


def calculate(signal,
              frequency,
              fmin=0,
              fmax=None,
              fstep="auto",
              f0=1,
              padding="predictive",
              cut_edges=False,
              window="Gaussian",
              preprocess=True,
              rel_tolerance=0.01):
    # Set values to floats, to prevent Matlab errors.
    fmin = float(fmin)
    f0 = float(f0)
    rel_tolerance = float(rel_tolerance)
    fmax = fmax or frequency / 2.0  # Set fmax to the Nyquist frequency if it is not specified.

    if not isinstance(fstep, str):
        fstep = float(fstep)

    wft, frequency = package.wft(signal,
                                 frequency,
                                 {
                                     "fmin": fmin,
                                     "fmax": fmax,
                                     "fstep": fstep,
                                     "f0": f0,
                                     "Padding": padding,
                                     "CutEdges": "on" if cut_edges else "off",
                                     "Window": window,
                                     "Preprocess": "on" if preprocess else "off",
                                     "RelTol": rel_tolerance,
                                 },
                                 nargout=2)

    return wft, frequency
