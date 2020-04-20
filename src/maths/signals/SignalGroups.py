#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2020 Lancaster University
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
from typing import Iterable, Tuple

import numpy as np
from numpy import ndarray

from data.parsing import parsing
from maths.signals.Signals import Signals


class SignalGroups(Signals):
    """
    Class representing one or two groups of signals.

    Each member of a group has an associated pair of signals: signal A and signal B.
    """

    def __init__(self, sig1a, sig1b, sig2a, sig2b, *args):
        if sig1a is None and sig2a is not None:
            sig1a, sig2a = sig2a, sig1a
            sig1b, sig2b = sig2b, sig1b

        self.sig1a = sig1a
        self.sig1b = sig1b
        self.sig2a = sig2a
        self.sig2b = sig2b

        super().__init__(*args)

    def is_dual_group(self) -> bool:
        return self.sig2a is not None

    def set_frequency(self, freq: float) -> None:
        self.frequency = float(freq)
        self.times = np.arange(0, self.sig1a.shape[1] / freq, 1 / freq)

    def get_all(self) -> Tuple[ndarray, ndarray, ndarray, ndarray]:
        return self.sig1a, self.sig1b, self.sig2a, self.sig2b

    @staticmethod
    def from_files(files: Iterable[str]) -> "SignalGroups":
        """
        Creates a SignalGroups instance from a filename or pair of filenames.

        Parameters
        ----------
        files : Iterable[str]
            One or two filenames.

        Returns
        -------
        SignalGroups
            SignalGroups instance representing the data from the file(s).
        """
        out = []
        for f in files:
            if f is None:
                out.extend((None, None))
                continue

            parser = parsing.get_parser(f, groups=True)
            array: ndarray = parser.parse()

            if len(array.shape) <= 2:
                raise Exception(
                    f"Array from {f} with shape {array.shape} cannot be "
                    f"loaded as a signal group. Signal group arrays must be "
                    f"saved as 3D arrays. Please see the documentation."
                )  # TODO GC: add docs

            signals_a = array[0, :, :]
            signals_b = array[1, :, :]

            out.extend((signals_a, signals_b))

        return SignalGroups(*out)
