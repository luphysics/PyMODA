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
import subprocess
from typing import Optional

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QDialog,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QComboBox,
)

from data import resources
from gui.BaseUI import BaseUI
from utils import file_utils
from utils.os_utils import OS
from utils.settings import Settings


class SettingsDialog(QDialog, BaseUI):
    """
    Dialog which allows the user to modify their preferences for PyMODA.
    """

    def __init__(self):
        self.settings = Settings()

        self.checkbox_default: QCheckBox = None
        self.line_cache_loc: QLineEdit = None
        self.btn_browse: QPushButton = None
        self.btn_open_logs: QPushButton = None

        self.combo_update_source: QComboBox = None

        super().__init__()

    def setup_ui(self) -> None:
        uic.loadUi(resources.get("layout:dialog_settings.ui"), self)

        self.btn_browse.clicked.connect(self.browse_for_folder)
        self.btn_open_logs.clicked.connect(self.on_open_logs_clicked)

        cache_loc = self.settings.get_pymodalib_cache()
        self.line_cache_loc.setText(cache_loc if cache_loc != "None" else cache_loc)

        self.combo_update_source.setCurrentText(
            self.settings.get_update_branch().capitalize()
        )

    def run(self) -> None:
        if QDialog.Accepted == self.exec():
            self.settings.set_pymodalib_cache(self.get_location())
            self.settings.set_update_source(
                self.combo_update_source.currentText().lower()
            )
            print("Settings saved.")
        else:
            print("Settings not saved.")

    def browse_for_folder(self) -> None:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)

        if QDialog.Accepted == dialog.exec():
            cache_location = dialog.selectedFiles()[0]
            self.line_cache_loc.setText(cache_location)

    def get_location(self) -> Optional[str]:
        return self.line_cache_loc.text()

    @staticmethod
    def on_open_logs_clicked() -> None:
        location = file_utils.pymoda_path

        if OS.is_windows():
            os.startfile(location)
        elif OS.is_linux():
            subprocess.Popen(["xdg-open", location])
        elif OS.is_mac_os():
            subprocess.Popen(["open", location])
