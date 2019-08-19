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
from gui.windows.timefrequency.TFView import TFView


class REView(TFView):
    """
    The View class for ridge extraction.
    """

    name = "Ridge Extraction and Filtering"

    def setup_btn_mark_region(self):
        pass

    def setup_btn_add_marked_region(self):
        pass

    def get_btn_mark_region(self):
        pass

    def get_btn_add_region(self):
        pass

    def get_btn_ridge_extraction(self):
        pass

    def get_btn_filter(self):
        pass

    def setup_radio_stats_avg(self):
        """
        Override method from TFView to remove functionality
        implemented in time-frequency window.
        """
        pass

    def setup_radio_stats_paired(self):
        """
        Override method from TFView to remove functionality
        implemented in time-frequency window.
        """
        pass

    def setup_radio_test(self):
        """
        Override method from TFView to remove functionality
        implemented in time-frequency window.
        """
        pass
