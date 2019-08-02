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
from maths.utils import float_or_none


class PCView(BaseTFView):
    """
    A View class to be subclassed by the phase coherence window.
    """

    name = "Wavelet Phase Coherence"

    _wavelet_types = ["Lognorm", "Morlet", "Bump"]
    _surrogate_types = ["RP", "FT", "AAFT", "IAAFT1", "IAAFT2", "WIAAFT", "tshift"]

    def setup_surr_method(self):
        pass

    def setup_surr_count(self):
        pass

    def setup_surr_type(self):
        pass

    def get_slider_count(self):
        pass

    def get_line_count(self):
        pass

    def on_slider_change(self, value):
        pass

    def set_slider_value(self, value):
        pass

    def setup_analysis_type(self):
        pass

    def on_count_line_changed(self, value):
        count = float_or_none(value)
        if count is not None and count > 1:
            self.set_slider_value(count)

    def plot_signal_pair(self, pair):
        pass

    def get_surr_count(self) -> int:
        pass

    def get_analysis_type(self) -> str:
        pass

    def get_surr_method(self) -> str:
        pass

    def get_surr_enabled(self) -> bool:
        pass
