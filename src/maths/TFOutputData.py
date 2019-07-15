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


class TFOutputData:
    """
    A class which contains the time-frequency output data required
    for plotting the appropriate transform.
    """

    def __init__(self,
                 times,
                 ampl,
                 freq,
                 powers,
                 avg_ampl,
                 avg_pow,
                 ):
        self.times = times
        self.ampl = ampl
        self.freq = freq
        self.powers = powers
        self.avg_ampl = avg_ampl
        self.avg_pow = avg_pow

        self.valid = True

    def is_valid(self):
        """Returns whether the data is valid and should be plotted."""
        return self.valid and len(self.times) > 0 and len(self.freq) > 0 and len(self.ampl) > 0

    def invalidate(self):
        """Sets the data as invalid."""
        self.valid = False
        self.ampl = None
        self.freq = None
        self.powers = None
        self.avg_ampl = None
        self.avg_pow = None
