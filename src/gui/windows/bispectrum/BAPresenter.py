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
from gui.windows.phasecoherence.PCPresenter import PCPresenter
from maths.multiprocessing.MPHelper import MPHelper


class BAPresenter(PCPresenter):

    def __init__(self, view):
        super().__init__(view)

        from gui.windows.bispectrum.BAWindow import BAWindow
        self.view: BAWindow = view

    def calculate(self, calculate_all: bool):
        if self.mp_handler:
            self.mp_handler.stop()

        self.is_plotted = False
        self.invalidate_data()

        self.mp_handler = MPHelper()
        self.mp_handler.bispectrum_analysis(self.signals,
                                            self.view.get_window(),
                                            self.on_bispectrum_completed)

    def on_bispectrum_completed(self):
        pass
