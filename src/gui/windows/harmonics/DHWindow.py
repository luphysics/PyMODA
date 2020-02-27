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
from data import resources
from gui.components.SingleSignalComponent import SingleSignalComponent
from gui.windows.common.BaseTFWindow import BaseTFWindow
from gui.windows.harmonics.DHPresenter import DHPresenter
from gui.windows.harmonics.DHViewProperties import DHViewProperties


class DHWindow(DHViewProperties, BaseTFWindow, SingleSignalComponent):
    def __init__(self, application):
        DHViewProperties.__init__(self)
        BaseTFWindow.__init__(self, application, DHPresenter(self))

        SingleSignalComponent.__init__(self, self.signal_plot())

        self.presenter.init()

    def setup_ui(self) -> None:
        super().setup_ui()

    def get_layout_file(self) -> str:
        return resources.get("layout:window_harmonics.ui")
