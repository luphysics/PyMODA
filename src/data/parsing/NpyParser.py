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
from numpy import ndarray

from data.parsing.BaseParser import BaseParser


class NpyParser(BaseParser):
    """
    A parser which loads data from a .npy file.
    """

    def parse(self) -> ndarray:
        signals: ndarray = np.load(self.filename)

        rows, cols = signals.shape
        row_wise = rows < cols

        if not row_wise:
            signals = signals.T  # Transpose signals.

        return signals
