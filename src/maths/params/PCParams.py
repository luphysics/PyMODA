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
from typing import Dict

from maths.params.TFParams import TFParams, _wft
from maths.signals.Signals import Signals
from utils.decorators import override
from utils.dict_utils import sanitise


class PCParams(TFParams):
    def __init__(
        self,
        signals: Signals,
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
        # Parameters not passed to Matlab.
        surr_enabled=False,
        surr_count=0,
        surr_method="RP",
        surr_preproc=False,
    ):
        if not surr_enabled:
            surr_count = 0

        self.surr_count = surr_count
        self.surr_method = surr_method
        self.surr_preproc = surr_preproc

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

    @override
    def items_to_save(self) -> Dict:
        tf = super().items_to_save()

        out = {"surr_count": self.surr_count, "surr_type": self.surr_method, **tf}
        return sanitise(out)
