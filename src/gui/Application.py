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
import asyncio
from typing import Type

from PyQt5.QtWidgets import QApplication
from asyncqt import QEventLoop

from gui.windows.BaseWindow import BaseWindow
from gui.windows.LauncherWindow import LauncherWindow
from gui.windows.bayesian.DBWindow import DBWindow
from gui.windows.bispectrum.BAWindow import BAWindow
from gui.windows.phasecoherence.PCWindow import PCWindow
from gui.windows.ridgeextraction.REWindow import REWindow
from gui.windows.timefrequency.TFWindow import TFWindow
from utils import cache


class Application(QApplication):
    """
    The base application class.
    """

    windows = []

    def __init__(self, _args):
        super(Application, self).__init__(_args)
        self.setup_event_loop()
        self.start_launcher()

    def setup_event_loop(self):
        """
        Sets the event loop which will be used by asyncio.
        """
        loop = QEventLoop(self)
        asyncio.set_event_loop(loop)

    def start_launcher(self):
        """Opens the launcher window which has buttons to open the other windows."""
        self.open_window(LauncherWindow)

    def start_time_frequency(self):
        """Opens the time-frequency common window."""
        self.open_window(TFWindow)

    def start_phase_coherence(self):
        """Opens the wavelet phase coherence window."""
        self.open_window(PCWindow)

    def start_ridge_extraction(self):
        """Opens the ridge extraction and filtering window."""
        self.open_window(REWindow)

    def start_bispectrum(self):
        """Opens the wavelet bispectrum common window."""
        self.open_window(BAWindow)

    def start_bayesian(self):
        """Opens the dynamical Bayesian inference window."""
        self.open_window(DBWindow)

    def open_window(self, WindowType: Type[BaseWindow]):
        """
        Opens a window with a given type which inherits from BaseWindow.

        Important: pass the class name instead of an instance of the class.
        """
        window = WindowType(self)
        self.windows.append(window)
        window.show()

    def notify_close_event(self, window: BaseWindow):
        """
        Should be called to notify the application when a window
        is closed. This functionality is implemented in BaseWindow.
        """
        try:
            self.windows.remove(window)
        except ValueError:
            pass

        if not self.windows:
            cache.clear()
