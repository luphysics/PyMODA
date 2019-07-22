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
from gui.base.components.MatplotlibComponent import MatplotlibComponent


class AmplitudePlot(MatplotlibComponent):

    def plot(self, amplitude, freq):
        self.clear()

        y = freq
        ylim = sorted([y[0], y[-1]])
        self.axes.set_ylim(ylim)

        self.axes.plot(amplitude, freq)
        self.apply_scale()
        self.axes.autoscale(False)
        self.on_plot_complete()
