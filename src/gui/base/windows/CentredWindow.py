#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2019  Lancaster University
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

from PyQt5.QtWidgets import QDesktopWidget

from gui.base.windows.BaseWindow import BaseWindow


class CentredWindow(BaseWindow):
    """
    A window which opens at the centre of the screen.
    """

    def __init__(self):
        super(CentredWindow, self).__init__()
        self.centre()

    def centre(self):
        """Moves the window to the centre of the screen."""
        geometry = self.frameGeometry()
        centre = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(centre)
        self.move(geometry.topLeft())
