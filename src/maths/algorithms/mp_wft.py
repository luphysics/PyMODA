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

from maths.TimeSeries import TimeSeries


class Watcher:

    def __init__(self, window, queue, delay, on_result):
        self.delay = delay * 1000
        self.on_result = on_result
        self.queue = queue

        # self.timer = QTimer(window)
        # self.timer.timeout.connect(self.check_result)
        QTimer.singleShot(self.delay, self.check_result)

    def start(self):
        self.timer.start(self.delay)
        print("Started")

    def stop(self):
        self.timer.stop()
        self.timer.deleteLater()
        print("Stopped")

    def check_result(self):
        if not self.queue.empty():
            self.on_result(*self.queue.get())
            self.stop()
        else:
            QTimer.singleShot(self.delay, self.check_result)


def mp_calculate(data: TimeSeries, window, on_result):
    queue = Queue()
    watcher = Watcher(window, queue, 2, on_result)

    proc = Process(target=_calculate, args=(queue, data, data.frequency,))
    # watcher.start()
    proc.start()


def _calculate(queue, data, freq):
    from maths.algorithms import wft
    import matlab

    signal = matlab.double([data.data.tolist()])
    freq = freq

    wft, f = wft.calculate(signal, freq)

    queue.put((
        data.times,
        np.asarray(wft),
        np.asarray(f),
    ))
