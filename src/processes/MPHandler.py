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

from typing import Callable, List, Tuple

import multiprocess as mp
from scheduler.Scheduler import Scheduler

from gui.windows.bayesian.ParamSet import ParamSet
from maths.algorithms.multiprocessing.bandpass_filter import _bandpass_filter
from maths.algorithms.multiprocessing.bayesian_inference import (
    _dynamic_bayesian_inference,
)
from maths.algorithms.multiprocessing.bispectrum_analysis import (
    _bispectrum_analysis,
    _biphase,
)
from maths.algorithms.multiprocessing.phase_coherence import _phase_coherence
from maths.algorithms.multiprocessing.preprocess import _preprocess
from maths.algorithms.multiprocessing.ridge_extraction import _ridge_extraction
from maths.algorithms.multiprocessing.time_frequency import _time_frequency
from maths.params.BAParams import BAParams
from maths.params.PCParams import PCParams
from maths.params.REParams import REParams
from maths.params.TFParams import TFParams, _fmin, _fmax
from maths.signals.SignalPairs import SignalPairs
from maths.signals.Signals import Signals
from maths.signals.TimeSeries import TimeSeries


class MPHandler:
    """
    A class providing functions which perform mathematical computations
    using a Scheduler. 

    Important:
    - Keep a reference to any instances of `MPHandler` to prevent them from
      being garbage collected before tasks have completed.
    - Calling any function on a running MPHandler will stop any tasks
      currently in progress.
    """

    def __init__(self):
        self.scheduler: Scheduler = None

    async def coro_transform(
        self, params: TFParams, on_progress: Callable[[int, int], None]
    ) -> List[tuple]:
        """
        Performs a wavelet transform or windowed Fourier transform of signals.
        Used in "time-frequency analysis".

        :param params: the parameters which are used in the algorithm
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        signals: Signals = params.signals
        params.remove_signals()  # Don't want to pass large unneeded object to other process.

        for time_series in signals:
            self.scheduler.add(
                target=_time_frequency,
                args=(time_series, params),
                process_type=mp.Process,
                queue_type=mp.Queue,
            )

        return await self.scheduler.run()

    async def coro_phase_coherence(
        self,
        signals: SignalPairs,
        params: PCParams,
        on_progress: Callable[[int, int], None],
    ) -> List[tuple]:
        """
        Performs wavelet phase coherence between signal pairs. Used in "wavelet phase coherence".

        :param signals: the pairs of signals
        :param params: the parameters which are used in the algorithm
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        for i in range(signals.pair_count()):
            pair = signals.get_pair_by_index(i)
            self.scheduler.add(
                target=_phase_coherence,
                args=(pair, params),
                subtasks=params.surr_count,
                process_type=mp.Process,
                queue_type=mp.Queue,
            )

        return await self.scheduler.run()

    async def coro_ridge_extraction(
        self, params: REParams, on_progress: Callable[[int, int], None]
    ) -> List[tuple]:
        """
        Performs ridge extraction on wavelet transforms. Used in "ridge extraction and filtering".

        :param params: the parameters which are used in the algorithm
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
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

                self.scheduler.add(
                    target=_ridge_extraction,
                    args=(signals[i], params),
                    process_type=mp.Process,
                    queue_type=mp.Queue,
                )

        return await self.scheduler.run()

    async def coro_bandpass_filter(
        self,
        signals: Signals,
        intervals: tuple,
        on_progress: Callable[[int, int], None],
    ) -> List[tuple]:
        """
        Performs bandpass filter on signals. Used in "ridge extraction and filtering".

        :param signals: the signals
        :param intervals: the intervals to calculate bandpass filter on
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        for s in signals:
            fs = s.frequency
            for i in range(len(intervals)):
                fmin, fmax = intervals[i]
                self.scheduler.add(
                    target=_bandpass_filter,
                    args=(s, fmin, fmax, fs),
                    process_type=mp.Process,
                    queue_type=mp.Queue,
                )

        return await self.scheduler.run()

    async def coro_bayesian(
        self,
        signals: SignalPairs,
        paramsets: List[ParamSet],
        on_progress: Callable[[int, int], None],
    ) -> List[tuple]:
        """
        Performs Bayesian inference on signal pairs. Used in "dynamical Bayesian inference".

        :param signals: the signals
        :param paramsets: the parameter sets to use in the algorithm
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        for params in paramsets:
            for pair in signals.get_pairs():
                self.scheduler.add(
                    target=_dynamic_bayesian_inference,
                    args=(*pair, params),
                    process_type=mp.Process,
                    queue_type=mp.Queue,
                )

        return await self.scheduler.run()

    async def coro_bispectrum_analysis(
        self,
        signals: SignalPairs,
        params: BAParams,
        on_progress: Callable[[int, int], None],
    ) -> List[tuple]:
        """
        Performs wavelet bispectrum analysis on signal pairs.
        Used in "wavelet bispectrum analysis".

        :param signals: the signal pairs
        :param params: the parameters to use in the algorithm
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        for pair in signals.get_pairs():
            self.scheduler.add(
                target=_bispectrum_analysis,
                args=(*pair, params),
                subtasks=4,
                process_type=mp.Process,
                queue_type=mp.Queue,
            )

        return await self.scheduler.run()

    async def coro_biphase(
        self,
        signals: SignalPairs,
        fs: float,
        f0: float,
        fr: Tuple[float, float],
        on_progress: Callable[[int, int], None],
    ) -> List[tuple]:
        """
        Calculates biphase and biamplitude. Used in "wavelet bispectrum analysis".

        :param signals: the signal pairs
        :param fs: the sampling frequency
        :param f0: the resolution
        :param fr: 'x' and 'y' frequencies
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(progress_callback=on_progress)

        for pair in signals.get_pairs():
            opt = pair[0].output_data.opt
            self.scheduler.add(
                target=_biphase,
                args=(*pair, fs, f0, fr, opt),
                process_type=mp.Process,
                queue_type=mp.Queue,
            )

        return await self.scheduler.run()

    async def coro_preprocess(
        self, signal: TimeSeries, fmin: float, fmax: float
    ) -> List[Tuple]:
        """
        Performs preprocessing on a single signal.

        :param signal: the signal as a 1D array
        :param fmin: the minimum frequency
        :param fmax: the maximum frequency
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler()

        self.scheduler.add(
            target=_preprocess,
            args=(signal.signal, signal.frequency, fmin, fmax),
            process_type=mp.Process,
            queue_type=mp.Queue,
        )
        return await self.scheduler.run()

    def stop(self):
        """
        Stops the tasks in progress. The MPHandler instance can be reused.
        """
        if self.scheduler:
            self.scheduler.terminate()
