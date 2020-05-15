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
import os
from os.path import join

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QFileDialog, QComboBox, QDialogButtonBox

from data import resources
from gui.BaseUI import BaseUI
from gui.dialogs.UseShortcutComponent import UseShortcutComponent
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
        self.settings = Settings()

        self.combo_recent: QComboBox = None
        self.buttonBox: QDialogButtonBox = None

        super().__init__()
        self.use_shortcut = UseShortcutComponent(self, self.use_recent_file)

    def setup_ui(self):
        uic.loadUi(resources.get("layout:dialog_select_file.ui"), self)
        self.setup_drops()
        self.setup_recent_files()

        self.btn_browse.clicked.connect(self.browse_for_file)
        self.btn_use_recent.clicked.connect(self.use_recent_file)

        self.set_ok_enabled(False)

        QTimer.singleShot(500, self.check_args)

    def get_result(self) -> str:
        """
        Shows the dialog and returns the path to the file chosen by the user.
        """
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

        folder = self.settings.get_last_opened_directory()
        if not folder:
            folder = join(os.getcwd(), "res", "data")

        dialog.setDirectory(folder)

        if dialog.exec():
            filepath = dialog.selectedFiles()[0]

            directory, filename = os.path.split(filepath)
            self.settings.set_last_opened_directory(directory)

            self.set_file(filepath)
            self.lbl_drag_drop.show_selected_file(self.file)

            if self.file:
                self.disable_recent_files()

    def setup_recent_files(self):
        files = self.settings.get_recent_files()
        if files:
            self.combo_recent.addItems(files)
        else:
            self.disable_recent_files()

    def use_recent_file(self):
        file = self.combo_recent.currentText()
        self.file = file
        self.accept()  # Close the dialog.

    def on_drop(self, file: str):
        if not file:
            raise Exception(
                f"Cannot load file: '{file}'. This may be an issue specific to drag-and-drop on your OS."
            )

        self.disable_recent_files()
        self.set_file(file)

    def set_file(self, file: str) -> None:
        self.file = file
        self.set_ok_enabled(bool(file))

    def disable_recent_files(self):
        """
        Disables the UI for selecting a recent file, since it may cause users to erroneously
        use a recent file instead of the file chosen in the GUI.
        """
        self.btn_use_recent.setDisabled(True)
        self.combo_recent.setDisabled(True)

    def set_ok_enabled(self, enabled: bool) -> None:
        """
        Sets the "ok" button in the dialog as enabled or disabled.

        :param enabled: whether to set the button as enabled, not disabled
        """
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enabled)

    def get_file_path(self):
        """Gets the file path for the selected file."""
        return resources.path_from_file_string(self.file)
