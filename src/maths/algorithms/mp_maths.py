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

import numpy as np
from PyQt5.QtCore import QTimer

from maths.algorithms.params import WFTParams


class Watcher:
    """
    A class which watches for a result from a process, using a QTimer
    to avoid blocking the main thread.
    """

    def __init__(self, window, queue, delay_seconds, on_result):
        """
        :param window: the QWindow from which the operation is being performed
        :param queue: the queue which will be used to get the result from the other process
        :param delay_seconds: the time between each consecutive check for a result
        :param on_result: a callback which should run on the main process/thread, taking
        the result of the operation
        """

        self.delay = delay_seconds * 1000
        self.on_result = on_result
        self.queue = queue

        self.timer = QTimer(window)
        self.timer.timeout.connect(self.check_result)
        self.running = False

    def start(self):
        """Starts the Watcher checking for a result."""
        self.timer.start(self.delay)
        self.running = True

    def stop(self):
        """Stops the timer and deletes it. The Watcher cannot be started again."""
        if self.running:
            self.running = False
            self.timer.stop()
            self.timer.deleteLater()

    def check_result(self):
        """Check for a result from the other process."""
        if not self.queue.empty():
            self.stop()
            self.on_result(*self.queue.get())


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

    def wft(self,
            params: WFTParams,
            window,
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

        self.proc = Process(target=self.__wft, args=(self.queue, params,))
        self.proc.start()

        self.watcher = Watcher(window, self.queue, 0.5, on_result)
        self.watcher.start()

    @staticmethod
    def __wft(queue, params: WFTParams):
        # Don't move the import statements.
        from maths.algorithms import wft

        wft, f = wft.calculate(params)

        queue.put((
            params.time_series.times,
            np.asarray(wft),
            np.asarray(f),
        ))

    def stop(self):
        """Stops the tasks in progress."""
        self.proc.terminate()
        self.watcher.stop()
        self.queue.close()
