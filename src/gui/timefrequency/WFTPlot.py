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
from multiprocessing import Queue, Process
from threading import Thread

import numpy as np
from PyQt5.QtCore import QTimer

import args
from gui.base.components.PlotComponent import PlotComponent
from maths.TimeSeries import TimeSeries


class WFTPlot(PlotComponent):

    def __init__(self, parent):
        super().__init__(parent)
        self.queue = Queue()
        self.times = None
        self.proc = None

    def plot(self, data: TimeSeries):
        self.wft_plot(data)

    def get_xlabel(self):
        return "Time (s)"

    def get_ylabel(self):
        return "Frequency (Hz)"

    def wft_plot(self, data: TimeSeries):
        fs = data.frequency

        self.times = data.times
        sig_matlab = data.data.tolist()

        self.proc = Process(target=generate_solutions, args=(self.queue, sig_matlab, fs))
        self.proc.start()
        QTimer.singleShot(1000, self.check_result)

    def check_result(self):
        if self.queue.empty():
            QTimer.singleShot(1000, self.check_result)
            return

        w, l = self.queue.get()

        a = np.asarray(w)
        gh = np.asarray(l)

        mesh = self.axes.pcolormesh(self.times, gh, np.abs(a))
        # colorbar = self.fig.colorbar(mesh)

        self.axes.set_title('STFT Magnitude')

        self.axes.autoscale(False)
        self.on_initial_plot_complete()


def generate_solutions(queue, signal, freq):
    from maths.algorithms import wft
    import matlab

    A = matlab.double([signal])
    fs_matlab = freq

    wft, f = wft.calculate(A, fs_matlab)

    queue.put((np.asarray(wft), np.asarray(f),))
