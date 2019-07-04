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
from gui.base.components.PlotComponent import PlotComponent
from maths.TimeSeries import TimeSeries


class SignalPlot(PlotComponent):

    def plot(self, data: TimeSeries):
        x = data.times
        y = data.data

        xlim = (x[0], x[-1])
        self.axes.plot(x, y, linewidth=0.7)
        self.axes.autoscale(False)
        self.axes.set_xlim(xlim)
        self.on_initial_plot_complete()

    def get_xlabel(self):
        return "Time (s)"

    def get_ylabel(self):
        return "Value"
