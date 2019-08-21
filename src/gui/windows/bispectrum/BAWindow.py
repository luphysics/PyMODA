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
from gui.windows.base.analysis.BaseTFWindow import BaseTFWindow
from gui.windows.bispectrum.BAPresenter import BAPresenter
from gui.windows.bispectrum.BAView import BAView
from gui.windows.phasecoherence.PCWindow import PCWindow


class BAWindow(PCWindow, BAView):

    def __init__(self, application):
        BAView.__init__(self, application, BAPresenter(self))
        BaseTFWindow.__init__(self, application)

    def init_ui(self):
        super(BAWindow, self).init_ui()
        self.get_button_calculate_single().hide()

    def get_layout_file(self) -> str:
        return resources.get("layout:window_bispectrum_analysis.ui")
