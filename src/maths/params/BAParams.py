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
from maths.signals.Signals import Signals


class BAParams:
    def __init__(
        self,
        signals: Signals,
        fmin: float,
        fmax: float,
        f0: float,
        preprocess: bool,
        nv: float,
        surr_count: int,
        alpha: float,
        opt: dict,
    ):
        self.signals = signals
        self.fmin = fmin
        self.fmax = fmax
        self.f0 = f0
        self.preprocess = preprocess
        self.nv = nv
        self.surr_count = surr_count
        self.alpha = alpha
        self.fs = signals.frequency

        # The MATLAB algorithm returns a struct, `opt`, which is converted to this dict.
        self.opt = opt
