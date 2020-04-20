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
import functools
from typing import Iterable

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox

from data import resources
from gui.BaseUI import BaseUI
from utils import args


class LoadGroupDataDialog(QDialog, BaseUI):
    """
    Dialog which allows the user to load data for group phase coherence.

    Data can be loaded as one or two groups.
    """

    def __init__(self):
        self.lbl_dragdrop1 = None
        self.lbl_dragdrop2 = None
        super(LoadGroupDataDialog, self).__init__()

        self.files = [None, None]
        self.btn_browse1.clicked.connect(functools.partial(self.browse_for_file, 0))
        self.btn_browse2.clicked.connect(functools.partial(self.browse_for_file, 1))

        self.update_ok_button()

    def setup_ui(self) -> None:
        uic.loadUi(resources.get("layout:dialog_select_group.ui"), self)
        self.setup_drops()

        QTimer.singleShot(500, self.check_args)

    def get_result(self) -> Iterable[str]:
        """
        Shows the dialog and returns the path to the file chosen by the user.
        """
        self.exec()
        return self.get_file_paths()

    def setup_drops(self) -> None:
        drop1 = self.lbl_dragdrop1
        drop2 = self.lbl_dragdrop2

        for index, d in enumerate((drop1, drop2)):
            d.setAcceptDrops(True)
            d.set_drop_callback(functools.partial(self.on_drop, index))

    def on_drop(self, index: int, file: str) -> None:
        if not file:
            raise Exception(
                f"Cannot load file: '{file}'. This may be an issue specific "
                f"to drag-and-drop on your OS."
            )

        self.files[index] = file
        self.update_ok_button()

    def browse_for_file(self, index: int) -> None:
        """
        Opens a file browser dialog for selecting a file.

        Parameters
        ----------
        index : int
            The index of the group to select a file for (0 or 1).
        """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)

        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            self.files[index] = filename

            self.update_text()
            self.update_ok_button()

    def update_ok_button(self) -> None:
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(any(self.files))

    def update_text(self):
        for index, item in enumerate(self.files):
            if item:
                (
                    self.lbl_dragdrop2 if index else self.lbl_dragdrop1
                ).show_selected_file(item)

    def get_file_paths(self) -> Iterable[str]:
        """
        Gets the file paths for the selected files.
        """
        out = [None, None]
        for index, f in enumerate(self.files):
            try:
                out[index] = resources.path_from_file_string(f)
            except:
                pass

        return out

    def check_args(self) -> None:
        """
        Checks whether the files have been specified in the command line arguments.
        """
        files = args.args_files()
        if files and any(files):
            self.files = [resources.get(f) for f in files]
            return self.accept()  # Close dialog.

        file = args.args_file()
        if file:
            self.files = [resources.get(file), None]
            return self.accept()
