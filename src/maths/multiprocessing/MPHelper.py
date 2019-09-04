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
from typing import Callable
from typing import List

import numpy as np
from PyQt5.QtGui import QWindow
from multiprocess import Queue, Process
from scipy.signal import hilbert

import maths.multiprocessing.mp_utils
from maths.algorithms.loop_butter import loop_butter
from maths.algorithms.surrogates import surrogate_calc
from maths.algorithms.wpc import wpc, wphcoh
from maths.multiprocessing.Scheduler import Scheduler
from maths.multiprocessing.Task import Task
from maths.params.PCParams import PCParams
from maths.params.REParams import REParams
from maths.params.TFParams import TFParams, _wft, _fmin, _fmax
from maths.signals.SignalPairs import SignalPairs
from maths.signals.Signals import Signals
from maths.signals.TimeSeries import TimeSeries
from maths.utils import matlab_to_numpy
from utils import args


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
        self.scheduler: Scheduler = None

    async def coro_transform(
            self,
            params: TFParams,
            on_progress: Callable[[int, int], None]
    ) -> List[tuple]:

        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        signals: Signals = params.signals
        params.remove_signals()  # Don't want to pass large unneeded object to other process.

        for time_series in signals:
            q = Queue()
            p = Process(target=_time_frequency, args=(q, time_series, params,))

            self.scheduler.append(Task(p, q))

        return await self.scheduler.coro_run()

    def transform(self,
                  params: TFParams,
                  window: QWindow,
                  on_result: Callable,
                  on_progress: Callable[[int, int], None]
                  ):
        """
        Performs the windowed Fourier transform in another process, returning a result
        in the main process.

        :param params: the parameters for the WFT
        :param window: the QWindow from which the WFT is being calculated
        :param on_result: a callback which takes the result of the calculations
        on the main process/thread
        :param on_progress: a callback with takes the current number of completed tasks,
        and the total number of tasks being run
        """
        self.stop()
        self.scheduler = Scheduler(window, progress_callback=on_progress)

        signals: Signals = params.signals
        params.remove_signals()  # Don't want to pass large unneeded object to other process.

        for time_series in signals:
            q = Queue()
            p = Process(target=_time_frequency, args=(q, time_series, params,))

            self.scheduler.append(
                Task(p, q, on_result)
            )

        self.scheduler.start()

    def phase_coherence(self,
                        signals: SignalPairs,
                        params: PCParams,
                        window: QWindow,
                        on_result: Callable,
                        on_progress: Callable[[int, int], None]
                        ):
        """
        Calculates the wavelet phase coherence for pairs of signals.
        """
        self.stop()  # Clear lists of processes, etc.
        self.scheduler = Scheduler(window, progress_callback=on_progress)

        for i in range(signals.pair_count()):
            q = Queue()

            pair = signals.get_pair_by_index(i)
            p = Process(target=_phase_coherence, args=(q, pair, params,))

            self.scheduler.append(
                Task(p, q, on_result, subtasks=params.surr_count)
            )

        self.scheduler.start()

    def ridge_extraction(self,
                         params: REParams,
                         window: QWindow,
                         on_result: Callable,
                         on_progress: Callable[[int, int], None]
                         ):
        """
        Calculates transforms in required frequency interval,
        and performs ridge extraction on transforms.

        :param wavelet_transforms: the wavelet transforms to perform ridge extraction on
        :param frequencies: a 1d array of frequencies
        :param fs: the sampling frequency
        :return:
        """
        self.stop()
        self.scheduler = Scheduler(window, progress_callback=on_progress)

        signals = params.signals
        num_transforms = len(signals)
        intervals = params.intervals

        for i in range(num_transforms):
            for j in range(len(intervals)):
                fmin, fmax = intervals[j]
                params.set_item(_fmin, fmin)
                params.set_item(_fmax, fmax)

                q = Queue()
                p = Process(target=_ridge_extraction, args=(q, signals[i], params))

                self.scheduler.append(
                    Task(p, q, on_result)
                )
        self.scheduler.start()

    def bandpass_filter(self,
                        signals: Signals,
                        intervals: tuple,
                        window: QWindow,
                        on_result: Callable,
                        on_progress: Callable[[int, int], None]
                        ):

        self.stop()
        self.scheduler = Scheduler(window, progress_callback=on_progress)

        for s in signals:
            fs = s.frequency
            for i in range(len(intervals)):
                fmin, fmax = intervals[i]

                q = Queue()
                p = Process(target=_bandpass_filter, args=(q, s, fmin, fmax, fs))
                self.scheduler.append(Task(p, q, on_result))

        self.scheduler.start()

    def bispectrum_analysis(self,
                            signal_pairs: SignalPairs,
                            window: QWindow,
                            on_result: Callable,
                            on_progress: Callable[[int, int], None]
                            ):
        pass

    def stop(self):
        """
        Stops the tasks in progress. The MPHelper can be reused.

        Removes all items from the lists of processes, queues
        and watchers.
        """
        if self.scheduler:
            self.scheduler.terminate()


def _bandpass_filter(queue, time_series: TimeSeries, fmin, fmax, fs):
    bands, _ = loop_butter(time_series.signal, fmin, fmax, fs)
    h = hilbert(bands)

    phase = np.angle(h)
    amp = np.abs(h)

    queue.put((
        time_series.name,
        bands,
        phase,
        amp,
        (fmin, fmax),
    ))


def _ridge_extraction(queue, time_series: TimeSeries, params: REParams):
    maths.multiprocessing.mp_utils.setup_matlab_runtime()
    import ridge_extraction
    import matlab

    package = ridge_extraction.initialize()

    d = params.get()
    result = package.ridge_extraction(1,
                                      matlab.double(time_series.signal.tolist()),
                                      params.fs,
                                      d["fmin"],
                                      d["fmax"],
                                      d["CutEdges"],
                                      d["Preprocess"],
                                      d["Wavelet"],
                                      nargout=6)

    transform, freq, iamp, iphi, ifreq, filtered_signal = result

    transform = matlab_to_numpy(transform)
    freq = matlab_to_numpy(freq)

    iamp = matlab_to_numpy(iamp)
    iamp = iamp.reshape(iamp.shape[1])

    iphi = matlab_to_numpy(iphi)
    iphi = iphi.reshape(iphi.shape[1])

    ifreq = matlab_to_numpy(ifreq)
    ifreq = ifreq.reshape(ifreq.shape[1])

    filtered_signal = matlab_to_numpy(filtered_signal)
    filtered_signal = filtered_signal.reshape(filtered_signal.shape[1])

    amplitude = np.abs(transform)
    powers = np.square(amplitude)

    length = len(amplitude)

    avg_ampl = np.empty(length, dtype=np.float64)
    avg_pow = np.empty(length, dtype=np.float64)

    for i in range(length):
        arr = amplitude[i]
        row = arr[np.isfinite(arr)]

        avg_ampl[i] = np.mean(row)
        avg_pow[i] = np.mean(np.square(row))

    queue.put((
        time_series.name,
        time_series.times,
        freq,
        transform,
        amplitude,
        powers,
        avg_ampl,
        avg_pow,
        (d["fmin"], d["fmax"]),
        filtered_signal,
        iphi,
        ifreq,
    ))


def _wt_surrogate_calc(queue, wt1, surrogate, params, index):
    from maths.algorithms import wt

    transform, freq = wt.calculate(surrogate, params)
    wt_surrogate = matlab_to_numpy(transform)

    surr_avg, _ = wphcoh(wt1, wt_surrogate)

    queue.put((index, surr_avg,))


def _phase_coherence(queue, signal_pair, params: PCParams):
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
                target=_wt_surrogate_calc, args=(q, wt1, surrogates[i], params, i)
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

    if len(tpc_surr) > 0:
        tpc_surr = np.mean(tpc_surr, axis=0)

    # Put all results, including phase coherence and surrogates,
    # in the queues to be returned to the GUI.
    queue.put((
        signal_pair,
        tpc,
        pc,
        pdiff,
        tpc_surr,
    ))


def _time_frequency(queue, time_series: TimeSeries, params: TFParams):
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

    out = (
        time_series.name,
        time_series.times,
        freq,
        transform,
        amplitude,
        power,
        avg_ampl,
        avg_pow,
    )

    if queue:
        queue.put(out)
    else:
        return out
