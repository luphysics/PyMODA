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
import itertools
from typing import List, Tuple

from data.parsing.parsing import get_parser
from maths.signals.Signals import Signals
from maths.signals.TimeSeries import TimeSeries


class SignalPairs(Signals):
    """
    A class containing multiple pairs of TimeSeries signals.
    """

    def __init__(self, *args: TimeSeries):
        super().__init__(*args)

    def get_pairs(self) -> List[Tuple[TimeSeries, TimeSeries]]:
        if len(self) < 2:
            return [(self[0], self[0])]

        def mapper(index):
            return self[index], self[index + 1]

        # 0, 2, 4, 6 etc.
        pair_indices = range(0, len(self), 2)
        return list(map(mapper, pair_indices))

    def get_pair_names(self) -> List[str]:
        def mapper(index):
            return f"Signal Pair {index + 1}"

        return list(map(mapper, range(len(self.get_pairs()))))

    def get_pair_by_name(self, name: str) -> Tuple[TimeSeries, TimeSeries]:
        pairs = self.get_pairs()
        names = self.get_pair_names()

        index = names.index(name)
        return pairs[index]

    def get_pair_by_index(self, index: int) -> Tuple[TimeSeries, TimeSeries]:
        return self.get_pairs()[index]

    def pair_count(self) -> int:
        """Returns the number of signal pairs."""
        return len(self) // 2

    def only(self, *pair_names) -> "SignalPairs":
        """
        Creates a new SignalPairs object containing only the signal pairs
        with the supplied names.
        """
        pairs: List[Tuple[TimeSeries, TimeSeries]] = [
            self.get_pair_by_name(n) for n in pair_names
        ]

        # Expand tuples to list of all signals.
        pairs_list: List[TimeSeries] = list(itertools.chain.from_iterable(pairs))

        signals = SignalPairs(*pairs_list)
        signals.set_frequency(self.frequency)
        return signals

    @staticmethod
    def from_file(file: str) -> "SignalPairs":
        parser = get_parser(file)
        args = [TimeSeries(d) for d in parser.parse()]
        return SignalPairs(*args)
