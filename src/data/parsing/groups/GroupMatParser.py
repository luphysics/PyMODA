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
from typing import Dict

import numpy as np
from numpy import ndarray
from scipy.io import loadmat

from data.parsing.MatParser import MatParser


class GroupMatParser(MatParser):
    """
    Parser which loads group data from a .mat file.
    """

    def parse(self) -> ndarray:
        from data.parsing.parsing import ParsingException

        data: Dict = loadmat(self.filename)
        arrays = list(filter(lambda i: isinstance(i, ndarray), data.values()))

        if len(arrays) > 1:
            raise ParsingException(
                f"Data files containing a signal group should only "
                f"contain 1 (3-dimensional) array: {self.filename}."
            )

        group: ndarray = arrays[0]
        x, y, z = group.shape

        if z == 2 and x != 2:
            out = np.empty((x, y, z,))
            out[0, :, :] = out[:, :, 0]
            out[1, :, :] = out[:, :, 1]
        else:
            out = group

        return out
