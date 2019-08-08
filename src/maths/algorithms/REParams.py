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
from maths.Signals import Signals
from maths.algorithms.TFParams import TFParams, _wft


class REParams(TFParams):

    def __init__(self, signals: Signals,
                 fmin=0,
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
                 method=2,
                 param=None,
                 normalize=False,
                 path_opt=True,
                 max_iterations=20,
                 cache_file=None
                 ):
        super().__init__(signals,
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
                         transform)

        # Add params not used in TFParams.
        self.data["Method"] = method

        if param:
            self.data["Param"] = param  # Not tested, may not work.

        self.data["Normalize"] = normalize
        self.data["PathOpt"] = path_opt
        self.data["MaxIter"] = max_iterations

        if cache_file:
            self.data["CachedDataLocation"] = cache_file
