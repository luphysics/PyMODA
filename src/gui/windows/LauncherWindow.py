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
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

from data import resources
from data.resources import get
from gui.dialogs.MatlabRuntimeDialog import MatlabRuntimeDialog
from gui.windows.CentredWindow import CentredWindow
from utils import args
from utils.os_utils import OS
from utils.settings import Settings
from utils.shortcuts import create_shortcut


class LauncherWindow(CentredWindow):
    """
    The first window that opens, providing buttons to open the important windows.
    """

    def __init__(self, parent):
        self.settings = Settings()
        super(LauncherWindow, self).__init__(parent)

    def setup_ui(self) -> None:
        uic.loadUi(get("layout:window_launcher.ui"), self)
        self.load_banner_images()

        self.btn_time_freq.clicked.connect(self.application.start_time_frequency)
        self.btn_wavelet_phase.clicked.connect(self.application.start_phase_coherence)
        self.btn_ridge_extraction.clicked.connect(
            self.application.start_ridge_extraction
        )
        self.btn_wavelet_bispectrum.clicked.connect(self.application.start_bispectrum)
        self.btn_dynamical_bayesian.clicked.connect(self.application.start_bayesian)

        self.btn_create_shortcut.clicked.connect(self.create_shortcut)
        self.check_matlab_runtime()

    def check_matlab_runtime(self) -> None:
        """
        Checks whether the LD_LIBRARY_PATH for the MATLAB Runtime is correctly passed to the program, and opens
        a dialog if appropriate.
        """
        if OS.is_linux() and not args.matlab_runtime() and self.settings.is_runtime_warning_enabled():
            dialog = MatlabRuntimeDialog()
            dialog.exec()

            self.settings.set_runtime_warning_enabled(not dialog.dont_show_again)
            if not dialog.dont_show_again:
                sys.exit(0)

    def load_banner_images(self) -> None:
        """
        Loads the banner images and displays them at the top of the window.
        """
        image = QPixmap(resources.get("image:physicslogo.png"))
        self.lbl_physics.setPixmap(image.scaled(600, 300, Qt.KeepAspectRatio))

    @staticmethod
    def create_shortcut() -> None:
        """
        Calls `create_shortcut()` and shows a message box with the result.
        """
        status = create_shortcut()
        QMessageBox(text=status).exec()
