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

from maths.params.TFParams import TFParams, _wft, _fmin, _fmax
from maths.signals.Signals import Signals
from utils.decorators import deprecated


class REParams(TFParams):
    def __init__(
        self,
        signals: Signals,
        fmin=None,
        fmax=None,
        fstep="auto",
        f0=1,
        padding="predictive",
        cut_edges=False,
        window="Gaussian",
        wavelet="Lognorm",
        preprocess=True,
        rel_tolerance=0.01,
        transform=_wft,
        # Added in REParams.
        method=2,
        param=None,
        normalize=False,
        path_opt=True,
        max_iterations=20,
        cache_file=None,
        intervals=None,
    ):
        super().__init__(
            signals,
            fmin,
            fmax,
            fstep,
            f0,
            padding,
            cut_edges,
            window,
            wavelet,
            preprocess,
            rel_tolerance,
            transform,
        )

        self.intervals = intervals

        # Add params not used in TFParams.
        self.data["Method"] = method

        if param:
            self.data["Param"] = param  # Not tested, may not work.

        self.data["Normalize"] = normalize
        self.data["PathOpt"] = path_opt
        self.data["MaxIter"] = max_iterations

        if cache_file:
            self.data["CachedDataLocation"] = cache_file

        if fmin is None:
            self.delete(_fmin)
        else:
            self.data[_fmin] = fmin

        if fmax is None:
            self.delete(_fmax)
        else:
            self.data[_fmax] = fmax

        self.data["Display"] = "off"

    @deprecated
    def set_cache_file(self, file: str) -> None:
        self.data["CachedDataLocation"] = file
