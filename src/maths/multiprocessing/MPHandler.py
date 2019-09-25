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

from typing import Callable, List

from multiprocess import Queue, Process

from gui.windows.bayesian.ParamSet import ParamSet
from maths.multiprocessing.Scheduler import Scheduler
from maths.multiprocessing.Task import Task
from maths.multiprocessing.algorithms.bandpass_filter import _bandpass_filter
from maths.multiprocessing.algorithms.bayesian_inference import _dynamic_bayesian_inference
from maths.multiprocessing.algorithms.bispectrum_analysis import _bispectrum_analysis
from maths.multiprocessing.algorithms.phase_coherence import _phase_coherence
from maths.multiprocessing.algorithms.ridge_extraction import _ridge_extraction
from maths.multiprocessing.algorithms.time_frequency import _time_frequency
from maths.params.PCParams import PCParams
from maths.params.REParams import REParams
from maths.params.TFParams import TFParams, _fmin, _fmax
from maths.signals.SignalPairs import SignalPairs
from maths.signals.Signals import Signals


class MPHandler:
    """
    A class providing a simple way to perform computations in another
    process.

    Using another process is necessary to avoid issues related to
    LD_LIBRARY_PATH on Linux, and prevent the UI from freezing.

    Unlike multithreading (due to the GIL) multiprocessing improves
    performance when multiple tasks are running simultaneously.

    IMPORTANT: you should hold a reference to any instances
    of this class to prevent them from being garbage collected
    before completion.
    """

    def __init__(self):
        self.scheduler: Scheduler = None

    async def coro_transform(self,
                             params: TFParams,
                             on_progress: Callable[[int, int], None]) -> List[tuple]:

        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        signals: Signals = params.signals
        params.remove_signals()  # Don't want to pass large unneeded object to other process.

        for time_series in signals:
            q = Queue()
            p = Process(target=_time_frequency, args=(q, time_series, params,))

            self.scheduler.append(Task(p, q))

        return await self.scheduler.coro_run()

    async def coro_phase_coherence(self,
                                   signals: SignalPairs,
                                   params: PCParams,
                                   on_progress: Callable[[int, int], None]):

        self.stop()  # Clear lists of processes, etc.
        self.scheduler = Scheduler(progress_callback=on_progress)

        for i in range(signals.pair_count()):
            q = Queue()

            pair = signals.get_pair_by_index(i)
            p = Process(target=_phase_coherence, args=(q, pair, params,))

            self.scheduler.append(Task(p, q, subtasks=params.surr_count))

        return await self.scheduler.coro_run()

    async def coro_ridge_extraction(self,
                                    params: REParams,
                                    on_progress: Callable[[int, int], None]):
        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

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

                self.scheduler.append(Task(p, q))

        return await self.scheduler.coro_run()

    async def coro_bandpass_filter(self,
                                   signals: Signals,
                                   intervals: tuple,
                                   on_progress: Callable[[int, int], None]):

        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        for s in signals:
            fs = s.frequency
            for i in range(len(intervals)):
                fmin, fmax = intervals[i]

                q = Queue()
                p = Process(target=_bandpass_filter, args=(q, s, fmin, fmax, fs))
                self.scheduler.append(Task(p, q))

        return await self.scheduler.coro_run()

    async def coro_bayesian(self,
                            signals: SignalPairs,
                            paramsets: List[ParamSet],
                            on_progress: Callable[[int, int], None]):

        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        for params in paramsets:
            for pair in signals.get_pairs():
                q = Queue()
                p = Process(target=_dynamic_bayesian_inference, args=(q, *pair, params,))

                self.scheduler.append(Task(p, q))

        return await self.scheduler.coro_run()

    async def coro_bispectrum_analysis(self,
                                       signals: SignalPairs,
                                       on_progress: Callable[[int, int], None]):
        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        for pair in signals.get_pairs():
            q = Queue()
            p = Process(target=_bispectrum_analysis, args=(q, pair))

        return await self.scheduler.coro_run()

    def stop(self):
        """
        Stops the tasks in progress. The MPHandler can be reused.

        Removes all items from the lists of processes, queues
        and watchers.
        """
        if self.scheduler:
            self.scheduler.terminate()
