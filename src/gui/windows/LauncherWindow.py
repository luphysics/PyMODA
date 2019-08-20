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

from data import resources
from gui.windows.base.CentredWindow import CentredWindow
from data.resources import get_ui, get


class LauncherWindow(CentredWindow):
    """
    The first window that opens, providing options to perform different
    types of analysis.
    """

    def __init__(self, application):
        super().__init__(application)

    def init_ui(self):
        uic.loadUi(get("layout:window_launcher.ui"), self)
        self.load_banner_images()

        self.btn_time_freq.clicked.connect(self.application.start_time_frequency)
        self.btn_wavelet_phase.clicked.connect(self.application.start_phase_coherence)
        self.btn_ridge_extraction.clicked.connect(self.application.start_ridge_extraction)
        self.btn_wavelet_bispectrum.clicked.connect(self.application.start_bispectrum)

        # Placeholder.
        self.btn_dynamical_bayesian.clicked.connect(self.application.start_phase_coherence)

    def load_banner_images(self):
        physics_label = self.lbl_physics
        image = QPixmap(resources.get("image:physicslogo.png"))
        physics_label.setPixmap(image.scaled(600, 300, Qt.KeepAspectRatio))
