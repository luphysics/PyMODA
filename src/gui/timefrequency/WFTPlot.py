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
from scipy.io import matlab

from gui.base.components.PlotComponent import PlotComponent
from maths.TimeSeries import TimeSeries
from packages.wft.for_redistribution_files_only import windowFT



class WFTPlot(PlotComponent):

    def plot(self, data: TimeSeries):
        self.WFTplot()
        self.axes.autoscale(False)
        self.on_initial_plot_complete()

    def get_xlabel(self):
        return "Time (s)"

    def get_ylabel(self):
        return "Value"

    def WFTplot(self):

        package = windowFT.initialize()

        fs = 20

        t = np.arange(0, 50, 1 / fs)
        sig = np.cos(2 * np.pi * 3 * t + 0.75 * np.sin(2 * np.pi * t / 5))
        sigMat = sig.tolist()

        A = matlab.double([sigMat])
        fsMat = matlab.double([fs])

        w, l = package.windowFT(A, fsMat, nargout=2)

        # freq = np.asarray(frq)
        # trans = np.asarray(trns)

        a = np.asarray(w)
        gh = np.asarray(l)

        pyA = np.asarray(A)

        self.axes.pcolormesh(t, gh, np.abs(a))
        self.axes.title('STFT Magnitude')
        self.axes.ylabel('Frequency [Hz]')
        self.axes.xlabel('Time [sec]')

