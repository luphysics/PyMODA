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
from typing import Tuple

from gui.windows.base.analysis.BaseTFView import BaseTFView
from gui.windows.bayesian.DBViewProperties import DBViewProperties
from maths.signals.TimeSeries import TimeSeries
from maths.utils import float_or_none, dec_float_or_none


class DBView(DBViewProperties, BaseTFView):

    def __init__(self, application, presenter):
        # Import here to avoid circular imports.
        from gui.windows.bayesian import DBPresenter
        presenter: DBPresenter = presenter

        DBViewProperties.__init__(self)
        BaseTFView.__init__(self, application, presenter)

    def plot_signal_pair(self, pair: Tuple[TimeSeries, TimeSeries]):
        pass

    @dec_float_or_none
    def get_freq_range1(self) -> Tuple[float, float]:
        min = float_or_none(self.lineedit_freq_range1_min.text())
        max = float_or_none(self.lineedit_freq_range1_max.text())
        return min, max

    @dec_float_or_none
    def get_freq_range2(self) -> Tuple[float, float]:
        min = float_or_none(self.lineedit_freq_range2_min.text())
        max = float_or_none(self.lineedit_freq_range2_max.text())
        return min, max

    @dec_float_or_none
    def get_window_size(self) -> float:
        return self.lineedit_window_size.text()

    @dec_float_or_none
    def get_propagation_const(self) -> float:
        return self.lineedit_propagation_const.text()

    @dec_float_or_none
    def get_num_surrogates(self) -> float:
        raise Exception("Not implemented yet.")

    @dec_float_or_none
    def get_overlap(self) -> float:
        return self.lineedit_overlap.text()

    @dec_float_or_none
    def get_order(self) -> float:
        return self.lineedit_order.text()

    @dec_float_or_none
    def get_confidence_level(self) -> float:
        return self.lineedit_confidence_level.text()
