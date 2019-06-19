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
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from gui import resources
from gui.base.SelectFileDialog import SelectFileDialog
from gui.base.windows.MaximisedWindow import MaximisedWindow


class TimeFreqWindow(MaximisedWindow):
    """
    The window which is used to perform time-frequency analysis.
    """

    name = "Time-Frequency Analysis"
    open_file = None

    def __init__(self, application):
        super().__init__()
        self.application = application

    def maximise_on_start(self):
        return False

    def init_ui(self):
        uic.loadUi(resources.get_ui("window_time_freq"), self)
        self.set_title()
        self.setup_menu_bar()
        self.select_file()

    def set_title(self, name=""):
        super(TimeFreqWindow, self).set_title(self.get_window_name())

    def get_window_name(self):
        """
        Gets the name of this window, adding the currently open file
        if applicable.
        """
        title = self.name
        if self.open_file:
            title += f" - {self.open_file}"
        return title

    def setup_menu_bar(self):
        menu = self.menubar
        file = menu.addMenu("File")
        file.addAction("Load data file")
        file.triggered.connect(self.select_file)

    def select_file(self):
        """Opens a dialog to select a file, and gets the result."""
        dialog = SelectFileDialog()

        code = dialog.exec()
        if code == QDialog.Accepted:
            self.open_file = dialog.get_file()
            print(f"Opening {self.open_file}...")
            self.set_title()
