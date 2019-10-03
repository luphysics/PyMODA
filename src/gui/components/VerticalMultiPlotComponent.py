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
from PyQt5 import sip
from PyQt5.QtWidgets import QVBoxLayout

from gui.plotting.MatplotlibWidget import MatplotlibWidget


class VerticalMultiPlotComponent:
    """
    Component which handles a vertical layout containing a variable number of plots.
    """

    def __init__(self, container: QVBoxLayout):
        self._container = container
        self._plots = []

    def vplot_remove_plots(self, *plots: MatplotlibWidget):
        for plot in plots:
            if plot in self._plots:
                self._plots.remove(plot)

            if plot is not None:
                self._container.removeWidget(plot)
                plot.deleteLater()
                sip.delete(plot)

    def vplot_remove_all_plots(self):
        self.vplot_remove_plots(*self._plots)

    def vplot_insert_widget(self, index, plot):
        self._container.insertWidget(index, plot)
        self._plots.append(plot)

    def vplot_add_plots(self, *plots):
        for plot in plots:
            if plot:
                self._container.addWidget(plot)
                self._plots.append(plot)

    def vplot_get_plot(self, index: int) -> MatplotlibWidget:
        return self._plots[index]

    def vplot_count(self) -> int:
        return len(self._plots)
