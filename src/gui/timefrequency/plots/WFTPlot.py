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
from gui.base.components.MatplotlibComponent import MatplotlibComponent
from maths.utils import subset2d, calc_subset_count


class WFTPlot(MatplotlibComponent):
    """
    Plots the windowed Fourier transform.
    """

    def plot(self, times, values, freq):
        self.clear()

        finite = values[np.isfinite(values)]  # Remove the 'NaN' items.
        mesh1, mesh2 = np.meshgrid(times, freq)

        n = calc_subset_count(values)
        if n > 1:
            mesh1 = subset2d(mesh1, n)
            mesh2 = subset2d(mesh2, n)
            values = subset2d(values, n)

        self.mesh = self.axes.contourf(mesh1, mesh2, values, 256,
                                       vmin=np.min(finite), vmax=np.max(finite),
                                       cmap=self.colormap())  # Can use: shading="gouraud"

        self.axes.set_title('STFT Magnitude')
        self.axes.autoscale(False)
        self.on_plot_complete()
        # self.colorbar()

    def colormap(self):
        file = resources.get("colours:colormap.csv")
        colours = np.loadtxt(file, dtype=float, delimiter=',')

        cmap = LinearSegmentedColormap.from_list("colours", colours, N=len(colours), gamma=1.0)
        return cmap

    def colorbar(self):
        """Create the colorbar. Needs to be refactored to avoid breaking alignment with the signal plot."""
        colorbar = self.fig.colorbar(self.mesh)
        pass

    def get_xlabel(self):
        return "Time (s)"

    def get_ylabel(self):
        return "Frequency (Hz)"
