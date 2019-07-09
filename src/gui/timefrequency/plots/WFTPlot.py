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
from multiprocess import Queue

import numpy as np

from gui.base.components.PlotComponent import PlotComponent


class WFTPlot(PlotComponent):
    """
    Plots the windowed Fourier transform.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.queue = Queue()
        self.times = None
        self.proc = None

    def plot(self, times, values, freq):


        from matplotlib.colors \
        import LinearSegmentedColormap
        colours = np.loadtxt(r'C:\Users\valys\Desktop\INTERNSHIP 2019\PyMODA\res\colours\colormap.csv', dtype=float, delimiter=',')
        clrs = LinearSegmentedColormap.from_list("colours", colours, N=len(colours), gamma=1.0)


        self.mesh = self.axes.pcolormesh(times, freq, values, vmin=0, vmax=0.55, cmap=clrs)  # Can use: shading="gouraud"
        self.axes.set_title('STFT Magnitude')
        self.axes.autoscale(False)
        self.on_initial_plot_complete()

    def colorbar(self):
        """Create the colorbar. Needs to be refactored to avoid breaking alignment with the signal plot."""
        # colorbar = self.fig.colorbar(mesh)
        pass

    def get_xlabel(self):
        return "Time (s)"

    def get_ylabel(self):
        return "Frequency (Hz)"
