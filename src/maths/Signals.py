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
from typing import List

from data.parsing.CSVParser import CSVParser
from maths.TimeSeries import TimeSeries


class Signals(list):
    """
    A class inheriting from `list`, which contains a collection of
    TimeSeries instances. Each Signals instance should have a frequency
    which is shared across all contained TimeSeries instances.
    """

    def __init__(self, *args: TimeSeries):
        super().__init__()

        for t in args:
            if isinstance(t, TimeSeries):
                self.append(t, generate_name=False)
            else:
                raise Exception(f"Signals constructor: expected TimeSeries, got {t}")

        self.generate_names()
        self.frequency = None

    def generate_names(self):
        """
        Generates a unique name for every TimeSeries in the dataset. If multiple
        items have the same name, then all instances with the name will be renamed.
        """
        temp = set()

        # Gets all duplicate names.
        duplicates = [name for name in self.names() if name in temp or temp.add(name)]

        for t in self:
            # Should rename if it has no name, or if it is a duplicate.
            if t.name is None or t.name in duplicates:
                t.name = self._name_template()

    def _name_template(self, index=1) -> str:
        """
        A template for a generating a particular name.
        It will not produce a name that is already in
        use by this instance.
        """
        while True:  # Iterate until we have a unique name.
            name = f"Signal {index}"
            index += 1
            if name not in self.names():
                break

        return name

    def append(self, object: TimeSeries, generate_name=True) -> None:
        """
        Overrides the append function, ensuring that any signal added
        has a unique name.
        """
        super(Signals, self).append(object)
        if generate_name:
            self.generate_names()

    def names(self) -> List:
        """
        Returns a list containing the name of every TimeSeries respectively.
        May contain duplicates if names have not been generated safely.
        """
        return [t.name for t in self]

    def set_frequency(self, freq: float):
        """Sets the frequency. This affects all TimeSeries contained within this instance."""
        freq = float(freq)
        self.frequency = freq
        for t in self:
            t.set_frequency(freq)

    def has_frequency(self):
        """Returns whether the frequency has been set."""
        return self.frequency is not None

    def get(self, name: str) -> TimeSeries:
        """
        Gets the TimeSeries with a given name. If no TimeSeries
        has the provided name, the first TimeSeries is returned.
        """
        for t in self:
            if t.name == name:
                return t
        return self[0]

    def reset(self):
        for t in self:
            t.reset_xlimits()

    def set_xlimits(self, x1, x2):
        """
        Sets the x-limits of all data (restricting the values to a certain
        range of times).

        :param x1: the lower limit
        :param x2: the upper limit
        """
        for t in self:
            t.set_xlimits(x1, x2)

    def only(self, *signal_names):
        """
        Creates a new Signals object containing only
        the desired signals.
        """
        signals = Signals(*[sig for sig in self if sig.name in signal_names])
        signals.set_frequency(self.frequency)
        return signals

    @staticmethod
    def from_file(file: str):
        """Creates a Signals instance from a provided file."""
        parser = get_parser(file)
        args = [TimeSeries(d) for d in parser.parse()]
        return Signals(*args)


def get_parser(filename):
    """Gets the appropriate parser for a given file."""
    return CSVParser(filename)  # Test implementation.
