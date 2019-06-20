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
import numpy as np

from data.parsing.CSVParser import CSVParser
from data.parsing.parsing import extension


class TimeSeries:
    """
    A time-series of data. A time-series is a 1-dimensional series of recorded values,
    with a frequency at which the data were recorded. The sampling frequency can be used
    to calculate the time for each datum point in the series.
    """

    def __init__(self, data, frequency=None):
        self.frequency = frequency
        self.data = np.asarray(data)

    def has_frequency(self):
        return self.frequency is not None

    @staticmethod
    def from_file(file):
        """Returns a time-series from a file."""
        return TimeSeries(get_parser(file).parse())


def get_parser(filename):
    ext = extension(filename)
    return CSVParser(filename)
