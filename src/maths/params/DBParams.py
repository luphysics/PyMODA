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
from maths.params.PCParams import PCParams
from maths.params.TFParams import _wft
from maths.signals.Signals import Signals


class DBIParams(PCParams):

    def __init__(self,
                 signals: Signals,
                 fmin=0,
                 fmax=None,
                 fstep="auto",
                 f0=1,
                 padding="predictive",
                 cut_edges=False,
                 window="Gaussian",  # Just for WFT.
                 wavelet="Lognorm",  # Just for WT.
                 preprocess=True,
                 rel_tolerance=0.01,
                 transform=_wft,

                 # Added in BAParams.
                 fc: float = None,
                 nv: float = None,

                 # Added in PCParams.
                 surr_enabled=False,
                 surr_count=0,
                 surr_method="RP",
                 surr_preproc=False):
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
                         transform,

                         surr_enabled,
                         surr_count,
                         surr_method,
                         surr_preproc)

        self.data["nv"] = nv
        self.data["fc"] = fc
