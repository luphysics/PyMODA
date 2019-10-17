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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

from data import resources
from data.resources import get
from gui.windows.CentredWindow import CentredWindow
from utils.shortcuts import create_shortcut


class LauncherWindow(CentredWindow):
    """
    The first window that opens, providing buttons to open the important windows.
    """

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
