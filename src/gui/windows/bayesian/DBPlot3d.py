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
from gui.plotting.MatplotlibWidget import MatplotlibWidget
from gui.plotting.plots.ColorMeshPlot import colormap


class DBPlot3d(MatplotlibWidget):

    def plot(self, x, y, z):
        self.axes.xaxis.set_label_position("top")
        self.update_xlabel()
        self.update_ylabel()

        self.axes.autoscale(True)

        self.axes.plot_surface(x, y, z, cmap=colormap())
        self.axes.autoscale(False)

        self.axes.invert_xaxis()
        self.set_mouse_zoom_enabled(False)

        self.on_plot_complete()

    def is_3d(self) -> bool:
        return True

    def get_xlabel(self):
        return "Time (s)"
