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

from gui.plotting.MatplotlibComponent import MatplotlibComponent
from maths.TimeSeries import TimeSeries


class PreprocessPlot(MatplotlibComponent):

    def plot(self, times: np.ndarray, original: np.ndarray, preprocessed: np.ndarray):
        self.clear()
        self.rect_stack.clear()

        self.axes.autoscale(True)

        width = 0.7
        self.axes.plot(times, original, linewidth=width)
        self.axes.plot(times, preprocessed, linewidth=width)

        self.axes.legend(["Original", "Preprocessed"])

        xlim = sorted((times[0], times[-1],))
        self.axes.set_xlim(xlim)

        self.axes.autoscale(False)
        self.on_plot_complete()
