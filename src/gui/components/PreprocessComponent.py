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
from gui.plotting.plots.PreprocessPlot import PreprocessPlot


class PreprocessComponent:
    """
    Component which handles the plot of the preprocessed signal on a PreprocessPlot.
    """

    def __init__(self, preproc_plot: PreprocessPlot):
        self._preproc_plot = preproc_plot

    def plot_preprocessed_signal(self, times, signal, preproc_signal):
        self._preproc_plot.plot(times, signal, preproc_signal)
