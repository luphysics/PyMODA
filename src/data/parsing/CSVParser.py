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

from data.parsing import parsing
from data.parsing.BaseParser import BaseParser


class CSVParser(BaseParser):
    """
    A class which can parse CSV data (comma-separated-values),
    either row-wise or column-wise.
    """

    def parse(self):
        """
        Parses the file, returning a list whose items are a list of
        the values in every signal respectively.
        """
        lines = parsing.get_lines(self.filename)

        if not lines:
            return [[]]

        # If each line has more values than the number of lines,
        # then each line corresponds to a separate signal.
        row_wise = len(lines) < len(lines[0].split(","))
        if row_wise:
            signal_count = len(lines)
        else:
            signal_count = len(lines[0].split(","))

        # List containing a list of data for each signal.
        data = [[] for _ in range(signal_count)]

        index = 0
        for l in lines:
            split = l.split(",")

            for i in range(len(split)):
                value = float(split[i])
                if row_wise:
                    data[index].append(value)
                else:
                    data[i].append(value)

            if row_wise:
                index += 1

        return data
