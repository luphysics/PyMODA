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
from PyQt5.QtWidgets import QWidget

from gui.BaseUI import BaseUI


class PlotWidget(QWidget, BaseUI):
    """
    A base component for plotting. Should be independent of any
    plotting library.
    """

    def get_xlabel(self) -> str:
        """Returns the label for the x-axis. Should be overridden in subclasses."""
        pass

    def get_ylabel(self) -> str:
        """Returns the label for the y-axis. Should be overridden in subclasses."""
        pass

    def set_in_progress(self, in_progress) -> None:
        """Sets the progress bar to display whether the plotting is in progress."""
        pass

    def on_plot_complete(self) -> None:
        """
        Should be called after the first plotting is complete. It will then set the initial state
        so that the reset button can work.
        """
        pass

    def clear(self) -> None:
        """
        Clears the plot, removing all plotted elements.
        """
        pass

    def update_xlabel(self, text=None) -> None:
        """
        Updates the x-label. If no value is passed,
        the result from get_xlabel() will be used.
        """
        pass

    def update_ylabel(self, text=None) -> None:
        """
        Updates the y-label. If no value is passed,
        the result from get_ylabel() will be used.
        """
        pass
