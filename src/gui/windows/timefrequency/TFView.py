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
from gui.common.BaseTFView import BaseTFView
from gui.windows.timefrequency.TFViewProperties import TFViewProperties
from utils.decorators import deprecated


class TFView(TFViewProperties, BaseTFView):
    """
    A View class to be subclassed by the time-frequency window.
    """

    @deprecated
    def __init__(self, application, presenter):
        TFViewProperties.__init__(self)
        BaseTFView.__init__(self, application, presenter)

    def setup_radio_transform(self):
        pass

    def setup_radio_stats_avg(self):
        pass

    def setup_radio_stats_paired(self):
        pass

    def setup_radio_test(self):
        pass

    def get_fstep(self) -> float:
        pass

    def get_padding(self) -> str:
        pass

    def get_rel_tolerance(self) -> float:
        pass

    def get_cut_edges(self) -> bool:
        pass

    def get_wt_wft_type(self) -> str:
        pass

    def get_transform_type(self) -> str:
        pass
