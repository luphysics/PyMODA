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
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QFileDialog, QComboBox

from data import resources
from gui.BaseUI import BaseUI
from utils import args
from utils.settings import Settings


class SelectFileDialog(QDialog, BaseUI):
    """
    A dialog allowing the user to select a file. Files can be
    selected via drag-and-drop, or by browsing with the file
    explorer.
    """

    def __init__(self):
        self.file: str = None
        self.combo_recent: QComboBox = None
        self.settings = Settings()
        super().__init__()

    def setup_ui(self):
        uic.loadUi(resources.get("layout:dialog_select_file.ui"), self)
        self.setup_drops()
        self.setup_recent_files()

        self.btn_browse.clicked.connect(self.browse_for_file)
        self.btn_use_recent.clicked.connect(self.use_recent_file)

        QTimer.singleShot(500, self.check_args)

    def get_result(self) -> str:
        self.exec()
        self.settings.add_recent_file(self.file)
        return self.get_file_path()

    def check_args(self):
        """
        Check the commandline arguments in case there is
        a pre-selected file.
        """
        file = args.args_file()
        if file:
            self.file = resources.get(file)
            self.accept()  # Close dialog.

    def setup_drops(self):
        """Sets up the label to accept drag-and-drop."""
        drop_target = self.lbl_drag_drop
        drop_target.setAcceptDrops(True)
        drop_target.set_drop_callback(self.on_drop)

    def browse_for_file(self):
        """Opens a file browser dialog for selecting a file."""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)

        if dialog.exec():
            filenames = dialog.selectedFiles()
            self.file = filenames[0]
            self.lbl_drag_drop.show_selected_file(self.file)

    def setup_recent_files(self):
        files = self.settings.get_recent_files()
        self.combo_recent.addItems(files)

    def use_recent_file(self):
        file = self.combo_recent.currentText()
        self.file = file
        self.accept()  # Close the dialog.

    def on_drop(self, file: str):
        if not file:
            raise Exception(
                "Cannot load file: ''. This may be an issue specific to your OS."
            )

        self.file = file

    def get_file_path(self):
        """Gets the file path for the selected file."""
        return resources.path_from_file_string(self.file)
