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
from typing import Optional

from PyQt5.QtWidgets import QLineEdit

from utils.decorators import floaty


class FreqComponent:

    """
    A component which handles the 3 frequency-related QLineEdits: fmin, fmax and resolution.
    """

    def __init__(self, lineedit_fmax: QLineEdit, lineedit_fmin: QLineEdit, lineedit_res: QLineEdit):
        self._res = lineedit_res
        self._fmin = lineedit_fmin
        self._fmax = lineedit_fmax

    @floaty
    def get_fmin(self) -> Optional[float]:
        return self._fmin.text()

    @floaty
    def get_fmax(self) -> Optional[float]:
        return self._fmax.text()

    @floaty
    def get_f0(self) -> Optional[float]:
        return self._res.text()
