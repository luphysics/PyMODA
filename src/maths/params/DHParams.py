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
from typing import List, Dict

from maths.params.TFParams import TFParams
from utils.dict_utils import sanitise


class DHParams(TFParams):
    def __init__(
        self, signals, scale_min, scale_max, time_res, sigma, surr_count, crop
    ):
        super(DHParams, self).__init__(signals)

        self.crop = crop
        self.surr_count = surr_count
        self.sigma = sigma
        self.time_res = time_res
        self.scale_max = scale_max
        self.scale_min = scale_min

    def args(self) -> List:
        items = (
            self.fs,
            self.scale_min,
            self.scale_max,
            self.sigma,
            self.time_res,
            self.surr_count,
        )
        return [i for i in items if i is not None]

    def items_to_save(self) -> Dict:
        return sanitise(
            {
                "crop": self.crop,
                "surrogates": self.surr_count,
                "sigma": self.sigma,
                "scale_max": self.scale_max,
                "scale_min": self.scale_min,
                "time_res": self.time_res,
            }
        )
