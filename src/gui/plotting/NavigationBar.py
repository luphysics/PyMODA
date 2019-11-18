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
from typing import Callable

from matplotlib.backends.backend_qt5 import NavigationToolbar2QT


class NavigationBar(NavigationToolbar2QT):
    """
    A toolbar which provides helpful options for interacting with a MatplotlibWidget,
    like resetting the view or switching to zoom mode.
    """

    def __init__(self, canvas, parent, coordinates=True):
        NavigationToolbar2QT.__init__(self, canvas, parent, coordinates)
        self.zoom_callbacks = []

    def disable_panning(self) -> None:
        """
        Disables the "pan" option in the toolbar.
        """
        self.actions()[4].setVisible(False)

    def release_zoom(self, event) -> None:
        """
        Overrides the function called when a zoom completes, to call the zoom listeners.
        """
        super(NavigationBar, self).release_zoom(event)
        self.on_zoom()

    def home(self, *args) -> None:
        """
        Overrides the function called when the home button is pressed, to call the zoom listeners.
        """
        super(NavigationBar, self).home(*args)
        self.on_zoom()

    def back(self, *args) -> None:
        """
        Overrides the function called when the back button is pressed, to call the zoom listeners.
        """
        super(NavigationBar, self).back(*args)
        self.on_zoom()

    def forward(self, *args) -> None:
        """
        Overrides the function called when the forwards button is pressed, to call the zoom listeners.
        """
        super(NavigationBar, self).forward(*args)
        self.on_zoom()

    def on_zoom(self) -> None:
        """
        Executes the zoom callbacks.
        """
        for callback in self.zoom_callbacks:
            callback()

    def add_zoom_callback(self, func: Callable[[None], None]) -> None:
        """
        Adds a zoom callback.

        :param func: a function which takes no parameters
        """
        self.zoom_callbacks.append(func)

    def remove_zoom_callback(self, func: Callable[[None], None]) -> None:
        """
        Removes a zoom callback.

        :param func: the same instance of a function which was added as a callback
        """
        self.zoom_callbacks.remove(func)
