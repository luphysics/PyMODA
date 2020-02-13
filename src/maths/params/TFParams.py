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
from typing import Type, Dict

from maths.signals.Signals import Signals
from utils.dict_utils import sanitise

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
    the time-frequency window.

    When the calculation begins, an instance of this
    parameters object should be created using the current settings (and therefore
    avoid issues when settings are edited in the window
    while the calculation is in progress).

    The params object holds a dictionary of data params which are passed to the
    Matlab functions as **kwargs. The dictionary can be accessed with the `get()`
    function, which will avoid errors in Matlab by removing all `None` values
    from the dictionary.
    """

    def __init__(
        self,
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
    ):
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

        self.signals: Signals = signals
        self.fs: float = float(signals.frequency)
        self.transform: str = transform

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

    def get(self) -> dict:
        """
        Gets the parameters to supply to the wt/wft function as a dictionary.

        Removes values which are None, because they cannot be passed to Matlab.
        """
        return sanitise(self.data)

    def set_item(self, key, value):
        self.data[key] = value

    def get_item(self, key):
        return self.data.get(key)

    def items_to_save(self) -> Dict:
        """
        Returns a dictionary containing the parameters which should be saved
        when using the "save data" option.
        """
        # Window type or wavelet type.
        if self.transform == _wft:
            window_type_name = "window_type"
            window_type = self.get_item("Window")
        else:
            window_type_name = "wavelet_type"
            window_type = self.get_item("Wavelet")

        out = {
            "transform_type": self.transform.upper(),
            "sampling_frequency": self.fs,
            window_type_name: window_type,
            "fmax": self.get_item(_fmax),
            "fmin": self.get_item(_fmin),
            "cut_edges": self.get_item(_cut_edges),
            "fr": self.get_item(_f0),
            "preprocessing": self.get_item(_preprocess),
        }
        return sanitise(out)

    def remove_signals(self):
        """
        Remove the signals parameter, since it is expensive to
        pass through a multiprocessing Queue unnecessarily.
        """
        self.signals = None

    def contains(self, key):
        return key in self.data

    def delete(self, key: str):
        try:
            del self.data[key]
        except KeyError:
            pass


def create(signals: Signals, params_type=Type[TFParams], **kwargs):
    """
    Creates a params object, taking the same **kwargs as
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
