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

import time

import numpy as np
from PyQt5.QtGui import QWindow
from multiprocess import Queue, Process

from maths.algorithms.params import TFParams, _wft
from maths.multiprocessing.Watcher import Watcher


class MPHelper:
    """
    A class providing a simple way to perform computations in another
    process. Another process is necessary to avoid issues related to
    LD_LIBRARY_PATH on Linux, and prevent the UI from freezing
    while - unlike multithreading, due to the GIL - improving
    performance when multiple tasks are running simultaneously.

    IMPORTANT: you should hold a reference to each instance
    of this class to prevent it from being garbage collected before
    completion.
    """

    def __init__(self):
        self.queue = None
        self.proc = None
        self.watcher = None

    def wft(self,
            params: TFParams,
            window: QWindow,
            on_result):
        """
        Performs the windowed Fourier transform in another process, returning a result
        in the main process.

        :param params: the parameters for the WFT
        :param window: the QWindow from which the WFT is being calculated
        :param on_result: a callback which takes the result of the calculations
        on the main process/thread
        :return:
        """
        self.queue = Queue()
        if params.transform == _wft:
            func = self._wft
        else:
            func = self._wt

        self.proc = Process(target=func, args=(self.queue, params,))
        self.proc.start()

        self.watcher = Watcher(window, self.queue, 0.5, on_result)
        self.watcher.start()

    @staticmethod
    def _wft(queue, params: TFParams):
        # Don't move the import statements.
        from maths.algorithms import wft

        wft, freq = wft.calculate(params)
        wft = np.asarray(wft)
        freq = np.asarray(freq)

        amplitude = np.abs(wft)

        power = np.square(amplitude)
        length = len(amplitude)

        avg_ampl = np.empty(length, dtype=np.float64)
        avg_pow = np.empty(length, dtype=np.float64)

        for i in range(length):
            arr = amplitude[i]
            row = arr[np.isfinite(arr)]

            avg_ampl[i] = np.mean(row)
            avg_pow[i] = np.mean(np.square(row))

        print(f"Started putting items in queue at time: {time.time()} seconds.")

        queue.put((
            params.time_series.times,
            amplitude,
            freq,
            power,
            avg_ampl,
            avg_pow,
        ))

    @staticmethod
    def _wt(queue, params: TFParams):  # TODO: refactor this
        # Don't move the import statements.
        from maths.algorithms import wt

        wft, freq = wt.calculate(params)
        wft = np.asarray(wft)
        freq = np.asarray(freq)

        amplitude = np.abs(wft)

        power = np.square(amplitude)
        length = len(amplitude)

        avg_ampl = np.empty(length, dtype=np.float64)
        avg_pow = np.empty(length, dtype=np.float64)

        for i in range(length):
            arr = amplitude[i]
            row = arr[np.isfinite(arr)]

            avg_ampl[i] = np.mean(row)
            avg_pow[i] = np.mean(np.square(row))

        print(f"Started putting items in queue at time: {time.time()} seconds.")

        queue.put((
            params.time_series.times,
            amplitude,
            freq,
            power,
            avg_ampl,
            avg_pow,
        ))

    def stop(self):
        """Stops the tasks in progress. The MPHelper can be reused."""
        if self.proc and self.watcher and self.queue:
            self.proc.terminate()
            self.watcher.stop()
            self.queue.close()
