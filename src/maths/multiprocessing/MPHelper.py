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

from maths.SignalPairs import SignalPairs
from maths.Signals import Signals
from maths.TimeSeries import TimeSeries
from maths.algorithms.params import TFParams, _wft
from maths.algorithms.wpc import wpc
from maths.multiprocessing.Watcher import Watcher
from maths.utils import matlab_to_numpy


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
        self.queue = []
        self.processes = []
        self.watchers = []

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
        self.stop()

        signals: Signals = params.signals
        params.remove_signals()  # Don't want to pass large unneeded object to other process.

        for time_series in signals:
            q = Queue()
            self.queue.append(q)
            self.processes.append(Process(target=self._timefrequency, args=(q, time_series, params,)))
            self.watchers.append(Watcher(window, q, 0.5, on_result))

        for proc in self.processes:
            proc.start()

        for watcher in self.watchers:
            watcher.start()

    def wpc(self,
            signals: SignalPairs,
            window: QWindow,
            on_result):
        """
        Calculates the wavelet phase coherence for pairs of signals.
        """
        self.stop()

        for i in range(signals.pair_count()):
            q = Queue()
            pair = signals.get_pair_by_index(i)
            self.queue.append(q)
            self.processes.append(Process(target=self._phase_coherence, args=(q, pair,)))
            self.watchers.append(Watcher(window, q, 0.5, on_result))

        for proc in self.processes:
            proc.start()

        for watcher in self.watchers:
            watcher.start()

    @staticmethod
    def _phase_coherence(queue, signal_pair):
        s1, s2 = signal_pair

        wt1 = s1.output_data.values
        wt2 = s2.output_data.values

        freq = s1.output_data.freq
        fs = s1.frequency

        tpc, pc, pdiff = wpc(wt1, wt2, freq, fs)

        queue.put((
            signal_pair,
            tpc,
            pc,
            pdiff
        ))

    @staticmethod
    def _timefrequency(queue, time_series: TimeSeries, params: TFParams):
        # Don't move the import statements.
        from maths.algorithms import wt, wft

        if params.transform == _wft:
            func = wft
        else:
            func = wt

        transform, freq = func.calculate(time_series, params)
        transform = matlab_to_numpy(transform)
        freq = matlab_to_numpy(freq)

        amplitude = np.abs(transform)

        power = np.square(amplitude)
        length = len(amplitude)

        avg_ampl = np.empty(length, dtype=np.float64)
        avg_pow = np.empty(length, dtype=np.float64)

        for i in range(length):
            arr = amplitude[i]
            row = arr[np.isfinite(arr)]

            avg_ampl[i] = np.mean(row)
            avg_pow[i] = np.mean(np.square(row))

        print(f"Started putting items in queue at time: {time.time():.1f} seconds.")

        queue.put((
            time_series.name,
            time_series.times,
            freq,
            transform,
            amplitude,
            power,
            avg_ampl,
            avg_pow,
        ))

    def stop(self):
        """Stops the tasks in progress. The MPHelper can be reused."""
        for i in range(len(self.processes)):
            self.processes.pop().terminate()
            self.watchers.pop().stop()
            self.queue.pop().close()
