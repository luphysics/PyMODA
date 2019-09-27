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
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from data import resources
from gui.plotting.MatplotlibWidget import MatplotlibWidget
from maths.num_utils import subset2d, calc_subset_count


def colormap():
    file = resources.get("colours:colormap.csv")
    colours = np.loadtxt(file, dtype=float, delimiter=',')

    cmap = LinearSegmentedColormap.from_list("colours", colours, N=len(colours), gamma=1.0)
    return cmap


class ColorMeshPlot(MatplotlibWidget):
    """
    Plots a color mesh as a contour plot. Used for
    wavelet transforms, phase coherence, etc.
    """

    def __init__(self, parent):
        MatplotlibWidget.__init__(self, parent)
        self.mesh = None

    def plot(self, x, c, y):
        self.clear()

        self.update_ylabel()
        self.update_xlabel()

        finite = c[np.isfinite(c)]  # Remove the 'NaN' items.
        mesh1, mesh2 = np.meshgrid(x, y)

        # To improve performance, we could subsample the data. Not actually implemented yet.
        n = calc_subset_count(c)
        if n > 1:
            mesh1 = subset2d(mesh1, n)
            mesh2 = subset2d(mesh2, n)
            c = subset2d(c, n)

        self.mesh = self.axes.contourf(mesh1, mesh2, c, 256,
                                       vmin=np.min(finite), vmax=np.max(finite),
                                       cmap=colormap())

        self.apply_scale()
        self.axes.autoscale(False)
        self.on_plot_complete()

        # self.colorbar()

    def plot_line(self, times, values, xlim=False):
        self.axes.plot(times, values, "#00ccff", linewidth=0.8)
        if xlim:
            self.set_xrange(times[0], times[-1])

    def colorbar(self):
        """Create the colorbar. Needs to be refactored to avoid breaking alignment with the signal plotting."""
        colorbar = self.fig.colorbar(self.mesh)
        pass

    def get_xlabel(self):
        return "Time (s)"

    def get_ylabel(self):
        return "Frequency (Hz)"
