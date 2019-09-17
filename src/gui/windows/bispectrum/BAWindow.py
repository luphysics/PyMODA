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
from data import resources
from gui.windows.bispectrum.BAPresenter import BAPresenter
from gui.windows.bispectrum.BAViewProperties import BAViewProperties
from gui.windows.common.BaseTFWindow import BaseTFWindow


class BAWindow(BAViewProperties, BaseTFWindow):
    name = "Wavelet Bispectrum Analysis"

    def __init__(self, application):
        BAViewProperties.__init__(self)
        BaseTFWindow.__init__(self, application, BAPresenter(self))

    def init_ui(self):
        super(BAWindow, self).init_ui()
        self.btn_calculate_single.hide()

    def get_layout_file(self) -> str:
        return resources.get("layout:window_bispectrum_analysis.ui")

    def setup_surr_method(self):
        """Override to do nothing."""

    def setup_analysis_type(self):
        """Override to do nothing."""
