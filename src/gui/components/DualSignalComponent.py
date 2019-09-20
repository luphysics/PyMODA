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
from typing import Tuple

from gui.plotting.plots.SignalPlot import SignalPlot
from maths.signals.TimeSeries import TimeSeries


class DualSignalComponent:
    """
    Component used in windows which have two signals plotted
    simultaneously.
    """

    def __init__(self, signal_plot: SignalPlot):
        self._signal_plot: SignalPlot = signal_plot

    def plot_signal_pair(self, pair: Tuple[TimeSeries, TimeSeries]):
        """Plots a pair of signals on the SignalPlot."""
        sig1, sig2 = pair
        self._signal_plot.plot(sig1, clear=True)
        self._signal_plot.plot(sig2, clear=False)
