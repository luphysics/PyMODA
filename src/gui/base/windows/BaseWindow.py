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

from PyQt5.QtWidgets import QMainWindow

from gui import resources
from gui.base.BaseUI import BaseUI


class BaseWindow(QMainWindow, BaseUI):
    """
    A base window which inherits from BaseUI.
    """

    def __init__(self):
        super(BaseWindow, self).__init__()
        # self.init_ui()
        self.set_title()

    def set_title(self, title=resources.get_name()):
        """
        Sets the title of the window. If no title is supplied,
        the default name of the application is used.
        """
        self.setWindowTitle(title)
