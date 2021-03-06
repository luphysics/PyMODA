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
from typing import List, Union

import numpy as np
from numpy import ndarray

from maths.signals.data.TFOutputData import TFOutputData


class TimeSeries:
    """
    A time-series of data: a 1-dimensional series of recorded values,
    with a sampling frequency at which the data were recorded.

    The sampling frequency can be used to calculate the time for
    each datum point in the series.
    """

    def __init__(self, data: Union[List, ndarray], frequency=None, name=None):
        self.name = name
        self.frequency = frequency

        if isinstance(data, list):
            self.signal = np.asarray(data, dtype=np.float64)
        else:
            self.signal = data

        self.initial_time = 0
        self.times = None

        self.original_signal = None
        self.original_times = None

        self.output_data = TFOutputData.empty()

    def has_frequency(self) -> bool:
        """Returns whether a frequency has been set."""
        return self.frequency is not None

    def set_frequency(self, freq: float) -> None:
        """
        Sets the frequency. This will trigger a regeneration
        of the time values.
        """
        self.frequency = freq
        self.times = self._generate_times()

    def has_name(self) -> bool:
        return self.name is not None

    def has_times(self) -> bool:
        return self.times is not None

    def _generate_times(self) -> ndarray:
        """Generates the time values associated with the data."""
        count = len(self.signal)
        return (
            np.arange(0, count / self.frequency, 1 / self.frequency) + self.initial_time
        )

    def set_xlimits(self, x1, x2) -> None:
        """
        Sets the x-limits of the data (restricting the values to a certain
        range of times). The original data is saved to a variable so that
        it can be restored.

        :param x1: the lower limit
        :param x2: the upper limit
        """
        if self.times is None:
            return

        self.reset_xlimits()
        if not self.contains_original_data():
            self.save_original_data()

        if x2 < x1:
            x1, x2 = x2, x1  # Swap values.

        indices = (x1 <= self.times) & (self.times <= x2)
        self.times = self.times[indices]
        self.signal = self.signal[indices]

    def reset_xlimits(self) -> None:
        """Resets the x-limits by restoring the original data."""
        if self.contains_original_data():
            self.signal = self.original_signal.copy()
            self.times = self.original_times.copy()

    def save_original_data(self) -> None:
        """
        Saves the original data,so that it can be restored later
        even if the x-limits are changed.
        """
        self.original_signal = self.signal.copy()
        self.original_times = self.times.copy()

    def contains_original_data(self) -> bool:
        """Returns whether the original data has been saved."""
        return self.original_signal is not None and self.original_times is not None

    def get_output_data(self) -> TFOutputData:
        return self.output_data

    def has_output_data(self) -> bool:
        return self.output_data is not None
