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
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QProgressBar

from gui.base.BaseUI import BaseUI
from gui.base.plot.Callbacks import Callbacks


class PlotOptionsBar(QWidget, BaseUI):
    """
    An options bar which provides helpful options for interacting with
    a PlotComponent. For example, resetting the view or switching to
    drag-to-move mode.
    """
    layout: QHBoxLayout = None

    def __init__(self, callbacks: Callbacks):
        super().__init__()
        self.callbacks = callbacks
        self.reset_button.set_onclick(self.callbacks.reset)
        self.back_button.set_onclick(self.callbacks.back)

    def init_ui(self):
        self.layout = QHBoxLayout(self)

        self.reset_button = ResetButton()
        self.layout.addWidget(self.reset_button)

        self.back_button = BackButton()
        self.layout.addWidget(self.back_button)

        self.setFixedHeight(80)
        self.setFixedWidth(340)

        self.create_progressbar()

    def create_progressbar(self):
        self.progress = QProgressBar()
        self.progress.setFixedWidth(200)

        self.progress.setMinimum(0)
        self.progress.setMaximum(0)
        self.progress.setValue(0)
        self.layout.addWidget(self.progress)

    def set_in_progress(self, boolean):
        if not boolean:
            self.progress.hide()


class OptionsButton(QPushButton, BaseUI):
    """
    A button to be used in the options bar for a plot.
    """

    def init_ui(self):
        self.setFixedWidth(50)

    def set_onclick(self, onclick):
        self.clicked.connect(onclick)


class ResetButton(OptionsButton):

    def init_ui(self):
        super().init_ui()
        self.setText("Reset")


class BackButton(OptionsButton):

    def init_ui(self):
        super().init_ui()
        self.setText("Back")
