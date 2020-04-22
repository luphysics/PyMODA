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
import os
from typing import Optional

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QFileDialog,
)

from data import resources
from gui.BaseUI import BaseUI
from utils.settings import Settings


class PyMODAlibCacheDialog(QDialog, BaseUI):
    """
    A dialog which allows the sampling frequency to be entered.
    """

    def __init__(self):
        self.settings = Settings()

        self.checkbox_default: QCheckBox = None
        self.line_location: QLineEdit = None
        self.btn_browse: QPushButton = None

        super(PyMODAlibCacheDialog, self).__init__()

    def setup_ui(self) -> None:
        uic.loadUi(resources.get("layout:dialog_pymodalib_cache.ui"), self)

        self.btn_browse.clicked.connect(self.browse_for_folder)
        self.checkbox_default.toggled.connect(self.update_ok_status)
        self.line_location.textChanged.connect(self.update_ok_status)

        self.set_ok_enabled(False)

    def run(self) -> None:
        self.exec()
        self.settings.set_pymodalib_cache(self.get_location())

    def browse_for_folder(self) -> None:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)

        if QDialog.Accepted == dialog.exec():
            cache_location = dialog.selectedFiles()[0]
            self.line_location.setText(cache_location)

            self.update_ok_status()

    def get_location(self) -> Optional[str]:
        if self.checkbox_default.isChecked():
            return None

        return self.line_location.text()

    def update_ok_status(self) -> None:
        line_location = self.get_location()
        default = self.checkbox_default.isChecked()

        for w in (self.btn_browse, self.line_location):
            w.setEnabled(not default)

        self.set_ok_enabled(
            default or bool(line_location and os.path.exists(line_location))
        )

    def set_ok_enabled(self, enabled: bool) -> None:
        """
        Sets the "ok" button in the dialog as enabled or disabled.

        :param enabled: whether to set the button as enabled, not disabled
        """
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enabled)
