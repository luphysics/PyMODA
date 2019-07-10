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


class TimeSeries:
    """
    A time-series of data. A time-series is a 1-dimensional series of recorded values,
    with a frequency at which the data were recorded. The sampling frequency can be used
    to calculate the time for each datum point in the series.
    """

    def __init__(self, data, frequency=None):
        self.frequency = frequency
        self.signal = np.asarray(data, dtype=np.float64)

        self.initial_time = 0
        self.times = None

        self.original_signal = None
        self.original_times = None

    def has_frequency(self):
        """Returns whether a frequency has been set."""
        return self.frequency is not None

    def set_frequency(self, freq: float):
        """
        Sets the frequency. This will trigger a regeneration
        of the time values.
        """
        self.frequency = freq
        self.times = self.generate_times()

    def generate_times(self):
        """Generates the time values associated with the data."""
        times = self.signal.copy()
        for i in range(0, len(self.signal)):
            times[i] = self.initial_time + i / self.frequency

        return times

    def set_xlimits(self, x1, x2):
        if self.times is None:
            return

        self.reset_xlimits()
        if not self.contains_original_data():
            self.save_original_data()

        if x2 < x1:
            x1, x2 = x2, x1  # Swap values.

        indices = self.find(self.times, lambda t: x1 <= t <= x2)
        self.times = self.times[indices]
        self.signal = self.signal[indices]

    def reset_xlimits(self):
        if self.contains_original_data():
            self.signal = self.original_signal.copy()
            self.times = self.original_times.copy()

    def save_original_data(self):
        self.original_signal = self.signal.copy()
        self.original_times = self.times.copy()

    def contains_original_data(self):
        return self.original_signal is not None and self.original_times is not None

    @staticmethod
    def find(array, func):
        """
        Gets indices of all items in a 1D array
        which satisfy a particular condition.
        """
        return [i for (i, value) in enumerate(array) if func(value)]

    @staticmethod
    def from_file(file):
        """Returns a time-series from a file."""
        return TimeSeries(get_parser(file).parse())


def get_parser(filename):
    """Gets the appropriate parser for a given file."""
    return CSVParser(filename)  # Test implementation.
