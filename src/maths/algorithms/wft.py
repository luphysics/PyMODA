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
    fmax = fmax or frequency / 2  # Set fmax to the Nyquist frequency if it is not specified.

    wft, frequency = package.wft(signal, frequency, nargout=2)

    return wft, frequency
