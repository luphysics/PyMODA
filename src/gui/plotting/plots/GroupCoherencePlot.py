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

from gui.plotting.MatplotlibWidget import MatplotlibWidget


class GroupCoherencePlot(MatplotlibWidget):
    def __init__(self, parent):
        self.xlabel = "Frequency (Hz)"
        self.ylabel = "Coherence"
        super(GroupCoherencePlot, self).__init__(parent)

    def plot(self, freq, coh1, coh2, average="median", percentile: float = 75):
        self.clear()

        self.update_ylabel()
        self.update_xlabel()

        single = coh2 is None
        if average == "median":
            favg = np.nanmedian
            average = "Median"
        else:
            favg = np.nanmean
            average = "Mean"

        pc11 = np.nanpercentile(coh1, 100 - percentile, axis=0)
        pc12 = np.nanpercentile(coh1, percentile, axis=0)

        if not single:
            pc21 = np.nanpercentile(coh2, 100 - percentile, axis=0)
            pc22 = np.nanpercentile(coh2, percentile, axis=0)

        color1 = "black"
        color2 = "red"
        alpha = 0.1
        linewidth = 1.1

        self.axes.plot(freq, favg(coh1, axis=0), color=color1, linewidth=linewidth)
        self.axes.fill_between(freq, pc11, pc12, color=color1, alpha=alpha)

        legend = [
            f"{average} coherence (group 1)",
        ]

        if not single:
            self.axes.plot(freq, favg(coh2, axis=0), color=color2, linewidth=linewidth)
            self.axes.fill_between(freq, pc21, pc22, color=color2, alpha=alpha)
            legend.append(legend[0].replace("1", "2"))

        self.set_log_scale(True, "x")
        self.axes.legend(legend)

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
