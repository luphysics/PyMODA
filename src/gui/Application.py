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
from typing import Type

from PyQt5.QtWidgets import QApplication

from gui.windows.BaseWindow import BaseWindow
from gui.windows.LauncherWindow import LauncherWindow
from gui.windows.bayesian.DBWindow import DBWindow
from gui.windows.bispectrum.BAWindow import BAWindow
from gui.windows.groupcoherence.GCWindow import GCWindow
from gui.windows.harmonics.DHWindow import DHWindow
from gui.windows.phasecoherence.PCWindow import PCWindow
from gui.windows.ridgeextraction.REWindow import REWindow
from gui.windows.timefrequency.TFWindow import TFWindow


class Application(QApplication):
    """
    The base application class.
    """

    windows = []

    def start_launcher(self) -> None:
        """Opens the launcher window which has buttons to open the other windows."""
        self.open_window(LauncherWindow)

    def start_time_frequency(self) -> None:
        """Opens the time-frequency common window."""
        self.open_window(TFWindow)

    def start_phase_coherence(self) -> None:
        """Opens the wavelet phase coherence window."""
        self.open_window(PCWindow)

    def start_group_coherence(self) -> None:
        """Opens the group phase coherence window."""
        self.open_window(GCWindow)

    def start_ridge_extraction(self) -> None:
        """Opens the ridge extraction and filtering window."""
        self.open_window(REWindow)

    def start_bispectrum(self) -> None:
        """Opens the wavelet bispectrum common window."""
        self.open_window(BAWindow)

    def start_bayesian(self) -> None:
        """Opens the dynamical Bayesian inference window."""
        self.open_window(DBWindow)

    def start_harmonics(self) -> None:
        """Opens the "detecting harmonics" window."""
        self.open_window(DHWindow)

    def open_window(self, WindowType: Type[BaseWindow]) -> None:
        """
        Opens a window with a given type which inherits from BaseWindow.

        Important: pass the class name instead of an instance of the class.
        """
        window = WindowType(self)
        self.windows.append(window)
        window.show()

    def notify_close_event(self, window: BaseWindow) -> None:
        """
        Should be called to notify the application when a window
        is closed. This functionality is implemented in BaseWindow.
        """
        try:
            self.windows.remove(window)
        except ValueError:
            pass
