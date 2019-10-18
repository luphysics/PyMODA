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

from numpy import ndarray
from scipy.io import loadmat

from data.parsing.BaseParser import BaseParser


class MatParser(BaseParser):
    """
    A parser which loads data from a .mat file.
    """

    def parse(self) -> ndarray:
        from data.parsing.parsing import ParsingException

        data: dict = loadmat(self.filename)
        arrays: List[ndarray] = list(
            filter(lambda i: isinstance(i, ndarray), data.values())
        )

        if len(arrays) > 1:
            raise ParsingException(
                ".mat file should have only one array. To load multiple signals,"
                " each signal should be a row or column in the array."
            )
        elif len(arrays) == 0:
            raise ParsingException("No arrays were found in the .mat file.")
        else:
            signals: ndarray = arrays[0]

        rows, cols = signals.shape
        row_wise = rows < cols

        if not row_wise:
            signals = signals.T  # Transpose signals.

        return signals
