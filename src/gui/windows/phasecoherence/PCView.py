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
from gui.windows.base.analysis.BaseTFView import BaseTFView
from gui.windows.timefrequency.TFView import TFView


class PCView(BaseTFView):
    """
    A View class to be subclassed by the phase coherence window.
    """

    name = "Wavelet Phase Coherence"

    def setup_surr_method(self):
        pass

    def setup_surr_count(self):
        pass

    def setup_surr_type(self):
        pass
