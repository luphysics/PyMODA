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
from gui.plotting.MatplotlibComponent import MatplotlibComponent


class AmplitudePlot(MatplotlibComponent):

    def __init__(self, parent):
        self.ylabel = "Frequency (Hz)"
        self.xlabel = ""
        super(AmplitudePlot, self).__init__(parent)

    def plot(self, amplitude, freq, surrogates=None):
        self.clear()

        self.update_ylabel()
        self.update_xlabel()

        self.axes.yaxis.set_label_position("right")

        y = freq
        ylim = sorted([y[0], y[-1]])
        self.axes.set_ylim(ylim)

        self.axes.plot(amplitude, freq)
        if hasattr(surrogates, "__len__") and len(surrogates) == len(amplitude):
            self.axes.plot(surrogates, freq)
            self.axes.legend(["Original signal", "Surrogate"])

        self.apply_scale()
        self.axes.autoscale(False)
        self.on_plot_complete()

    def get_ylabel(self):
        return self.ylabel

    def get_xlabel(self):
        return self.xlabel

    def set_xlabel(self, text):
        self.xlabel = text

    def set_ylabel(self, text):
        self.ylabel = text
