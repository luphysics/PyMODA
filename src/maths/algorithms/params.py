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
from maths.TimeSeries import TimeSeries

# Keys for the dictionary that is supplied to the Matlab function.
_fmin = "fmin"
_fmax = "fmax"
_fstep = "fstep"
_f0 = "f0"
_padding = "Padding"
_cut_edges = "CutEdges"
_window = "Window"
_preprocess = "Preprocess"
_rel_tolerance = "RelTol"


class WFTParams:

    def __init__(self,
                 time_series: TimeSeries,
                 fmin=0,
                 fmax=None,
                 fstep="auto",
                 f0=1,
                 padding="predictive",
                 cut_edges=False,
                 window="Gaussian",
                 preprocess=True,
                 rel_tolerance=0.01):
        self.time_series = time_series
        self.fs = float(time_series.frequency)

        self.data = {
            _fmin: float(fmin),
            _fmax: float(fmax) if fmax else self.fs / 2.0,
            _f0: float(f0),
            _rel_tolerance: float(rel_tolerance),
            _fstep: fstep if isinstance(fstep, str) else float(fstep),
            _padding: padding,
            _cut_edges: "on" if cut_edges else "off",
            _window: window,
            _preprocess: "on" if preprocess else "off",
        }

    def get(self) -> dict:
        """Get the parameters to supply to the wft function."""
        return self.data