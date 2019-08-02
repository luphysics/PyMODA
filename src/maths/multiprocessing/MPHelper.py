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
import psutil as psutil
from PyQt5.QtGui import QWindow
from multiprocess import Queue, Process

from maths.SignalPairs import SignalPairs
from maths.Signals import Signals
from maths.TimeSeries import TimeSeries
from maths.algorithms.PCParams import PCParams
from maths.algorithms.TFParams import TFParams, _wft
from maths.algorithms.surrogates import surrogate_calc
from maths.algorithms.wpc import wpc, wphcoh
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
        self.on_stop = lambda: None

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

            self.processes.append(
                Process(target=self._time_frequency, args=(q, time_series, params,))
            )
            self.watchers.append(Watcher(window, q, 0.5, on_result))

        for proc in self.processes:
            proc.start()

        for watcher in self.watchers:
            watcher.start()

    def wpc(self,
            signals: SignalPairs,
            params: PCParams,
            window: QWindow,
            on_result):
        """
        Calculates the wavelet phase coherence for pairs of signals.
        """
        self.stop()  # Clear lists of processes, etc.

        for i in range(signals.pair_count()):
            q = Queue()
            self.queue.append(q)

            pair = signals.get_pair_by_index(i)
            self.processes.append(
                Process(target=self._phase_coherence, args=(q, pair, params,))
            )
            self.watchers.append(Watcher(window, q, 0.5, on_result))

        for proc in self.processes:
            proc.start()

        for watcher in self.watchers:
            watcher.start()

    def _phase_coherence(self, queue, signal_pair, params: PCParams):
        """Should not be called in the main process."""
        s1, s2 = signal_pair

        wt1 = s1.output_data.values
        wt2 = s2.output_data.values

        freq = s1.output_data.freq
        fs = s1.frequency

        # Calculate phase coherence.
        tpc, pc, pdiff = wpc(wt1, wt2, freq, fs)

        # Calculate surrogates.
        surr_count = params.surr_count
        surr_method = params.surr_method
        surr_preproc = params.surr_preproc
        surrogates, _ = surrogate_calc(s1, surr_count, surr_method, surr_preproc, fs)

        tpc_surr = list(range(surr_count))
        processes = []
        queues = []

        for i in range(surr_count):
            q = Queue()
            queues.append(q)

            processes.append(
                Process(
                    target=self._wt_surrogate_calc, args=(q, wt1, surrogates[i], params, i)
                )
            )

        for p in processes:
            p.start()

        # Wait for processes to calculate surrogate results.
        # This is fine since we're not running on the main process.
        for p in processes:
            p.join()

        # After all processes finished, get all surrogate results.
        for q in queues:
            index, result = q.get()
            tpc_surr[index] = result

        tpc_surr = np.mean(tpc_surr, axis=0)

        # Put all results, including phase coherence and surrogates,
        # in the queue to be returned to the GUI.
        queue.put((
            signal_pair,
            tpc,
            pc,
            pdiff,
            tpc_surr,
        ))

    def _wt_surrogate_calc(self, queue, wt1, surrogate, params, index):
        from maths.algorithms import wt

        transform, freq = wt.calculate(surrogate, params)
        wt_surrogate = matlab_to_numpy(transform)

        surr_avg, _ = wphcoh(wt1, wt_surrogate)

        queue.put((index, surr_avg,))

    def _time_frequency(self, queue, time_series: TimeSeries, params: TFParams):
        """Should not be called in the main process."""
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
        """
        Stops the tasks in progress. The MPHelper can be reused.

        Removes all items from the lists of processes, queues
        and watchers.
        """
        self.on_stop()
        for i in range(len(self.processes)):
            # self.processes.pop().terminate()
            self.terminate_tree(self.processes.pop())
            self.watchers.pop().stop()
            self.queue.pop().close()

    def terminate_tree(self, process: Process):
        pid = process.pid
        for child in psutil.Process(pid).children(recursive=True):
            child.terminate()

        process.terminate()
