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
from typing import Tuple


class ParamSet:
    """
    Represents the parameter set used by the dynamical Bayesian inference window.
    """

    def __init__(self,
                 freq_range1: Tuple[float, float],
                 freq_range2: Tuple[float, float],
                 window: float,
                 propagation_const: float,
                 surr_count: int,
                 overlap: float,
                 order: int,
                 confidence_level: float
                 ):
        self.freq_range1 = freq_range1
        self.freq_range2 = freq_range2
        self.window = window
        self.propagation_const = propagation_const
        self.surr_count = surr_count
        self.overlap = overlap
        self.order = order
        self.confidence_level = confidence_level

    def to_string(self) -> Tuple[str, str]:
        """
        Returns a string representation of this object for each frequency band.
        """
        # Function to use for each frequency band.
        def convert(freq: Tuple[float, float]) -> str:
            freq_range_str = ",".join([str(i) for i in freq])
            items = [freq_range_str,
                     self.window,
                     self.overlap,
                     self.propagation_const,
                     self.order,
                     self.confidence_level]

            return " | ".join([str(i) for i in items])

        return convert(self.freq_range1), convert(self.freq_range2)
