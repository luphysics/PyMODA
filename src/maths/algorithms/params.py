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
        """
        Constructor which takes the desired parameters and converts
        them into floats if necessary (to prevent Matlab errors).

        :param time_series: the signal data as a time-series
        :param fmin: the minimum frequency
        :param fmax: the maximum frequency
        :param fstep: the frequency step
        :param f0: the window resolution parameter, which determines the
        trade-off between the time and frequency resolutions
        :param padding: the padding to use when computing the transform
        :param cut_edges: whether the transform should be computed only in
        the cone of influence
        :param window: the window type to use - Gaussian, Hann, Blackman, Exp,
        Rect or Kaiser-a.
        :param preprocess: whether to perform preprocessing on the signal
        :param rel_tolerance: relative tolerance, specifying the cone of influence
        """
        # Set default values. These aren't assigned in the declaration above
        # because it's helpful for the window to be able to supply None
        # without requiring knowledge of the default values.
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
        """Get the parameters to supply to the wft function as a dictionary."""
        return self.data

    @staticmethod
    def create(time_series, **kwargs):
        out = {}
        for key, value in kwargs.items():
            if value:
                out[key] = value

        return WFTParams(time_series, **out)
