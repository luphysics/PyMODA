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
from gui import Application
from gui.windows.base.analysis.BaseTFWindow import BaseTFWindow
from gui.windows.phasecoherence.PCPresenter import PCPresenter
from gui.windows.phasecoherence.PCView import PCView


class PCWindow(BaseTFWindow, PCView):
    """
    The phase coherence window.
    """

    def __init__(self, application: Application):
        PCView.__init__(self, application, PCPresenter(self))
        BaseTFWindow.__init__(self)

    def get_layout_file(self) -> str:
        return resources.get("layout:window_phase_coherence.ui")

    def get_window(self):
        super().get_window()
