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
_wavelet = "Wavelet"

_wft = "wft"
_wt = "wt"


class TFParams:
    """
    A class which is used to hold the parameters for the WT and WFT functions in
    the time-frequency window. When the calculation begins, an instance of this
    parameters object should be created using the current settings (and therefore
    not susceptible to issues when settings are edited in the window
    during the calculation).

    The params object holds a dictionary of data params which are passed to the
    Matlab functions as **kwargs. It also contains the time series and sampling
    frequency.
    """

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
                 transform=_wft):
        """
        Constructor which takes the desired parameters and converts
        them into floats if necessary (to prevent Matlab errors).

        :param signals: the signal data
        :param fmin: the minimum frequency
        :param fmax: the maximum frequency
        :param fstep: the frequency step
        :param f0: the window resolution parameter, which determines the
        trade-off between the time and frequency resolutions
        :param padding: the padding to use when computing the transform
        :param cut_edges: whether the transform should be computed only in
        the cone of influence
        :param window: the window type to use in the WFT - Gaussian, Hann, Blackman, Exp,
        Rect or Kaiser-a.
        :param wavelet: the wavelet type to use in the WT - Lognorm, Morlet, Bump or Morse-a.
        :param preprocess: whether to perform preprocessing on the signal
        :param rel_tolerance: relative tolerance, specifying the cone of influence
        """
        if transform == _wt and fmin == 0:
            fmin = None

        self.signals = signals
        self.fs = float(signals.frequency)
        self.transform = transform

        self.data = {
            _fmin: float(fmin) if fmin is not None else None,
            _fmax: float(fmax) if fmax else self.fs / 2.0,
            _f0: float(f0),
            _rel_tolerance: float(rel_tolerance),
            _fstep: fstep if isinstance(fstep, str) else float(fstep),
            _padding: padding,
            _cut_edges: "on" if cut_edges else "off",
            _window: window,
            _wavelet: wavelet,
            _preprocess: "on" if preprocess else "off",
        }

        temp_keys = []
        for key, value in self.data.items():
            if value is None:
                temp_keys.append(key)

        # Remove values which are None, because they cannot be passed to Matlab.
        for k in temp_keys:
            del self.data[k]

    def get(self) -> dict:
        """Gets the parameters to supply to the wt/wft function as a dictionary."""
        return self.data

    def remove_signals(self):
        """
        Remove the signals parameter, since it is expensive to
        pass through a multiprocessing Queue unnecessarily.
        """
        self.signals = None

    def contains(self, key):
        return key in self.data


def create(signals, params_type=TFParams, **kwargs):
    """
    Creates a TFParams object, taking the same **kwargs as
    the constructor. Any argument that is set to None - or not
    supplied at all - will cause the params object to use the default
    value for that argument.
    """
    out = {}
    for key, value in kwargs.items():
        if value is not None:
            out[key] = value

    return params_type(signals, **out)


class ParamsException(Exception):
    pass
