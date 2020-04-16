#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2020 Lancaster University
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


class GroupNpyParser(BaseParser):
    """
    A parser which loads group data from a .npy file.
    """

    def parse(self) -> ndarray:
        group: ndarray = np.load(self.filename)
        x, y, z = group.shape

        if z == 2 and x != 2:
            out = np.empty((x, y, z,))
            out[0, :, :] = out[:, :, 0]
            out[1, :, :] = out[:, :, 1]
        else:
            out = group

        return out
