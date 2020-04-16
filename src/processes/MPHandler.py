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

from typing import Callable, List, Tuple, Union

import multiprocess as mp
import pymodalib
from numpy import ndarray
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
from maths.algorithms.multiprocessing.ridge_extraction import _ridge_extraction
from maths.algorithms.multiprocessing.time_frequency import _time_frequency
from maths.params.BAParams import BAParams
from maths.params.DHParams import DHParams
from maths.params.PCParams import PCParams
from maths.params.REParams import REParams
from maths.params.TFParams import TFParams, _fmin, _fmax
from maths.signals.SignalPairs import SignalPairs
from maths.signals.Signals import Signals
from maths.signals.TimeSeries import TimeSeries
from utils.os_utils import OS


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

    # On Linux, we don't need to run in a thread because processes can be forked; we also need to avoid
    # using a thread because this will cause issues with the LD_LIBRARY_PATH.
    should_run_in_thread = not OS.is_linux()

    def __init__(self):
        self.scheduler: Scheduler = None

    async def coro_transform(
        self, params: TFParams, on_progress: Callable[[int, int], None]
    ) -> List[Tuple]:
        """
        Performs a wavelet transform or windowed Fourier transform of signals.
        Used in "time-frequency analysis".

        :param params: the parameters which are used in the algorithm
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(
            progress_callback=on_progress, run_in_thread=self.should_run_in_thread
        )

        signals: Signals = params.signals
        params.remove_signals()  # Don't want to pass large unneeded object to other process.

        return await self.scheduler.map(
            target=_time_frequency,
            args=[(time_series, params, True) for time_series in signals],
            process_type=mp.Process,
            queue_type=mp.Queue,
        )

    async def coro_harmonics(
        self,
        signals: Signals,
        params: DHParams,
        preprocess: bool,
        on_progress: Callable[[int, int], None],
    ) -> List[Tuple]:
        """
        Detects harmonics in signals.

        :param signals: the signals
        :param params: the parameters to pass to the harmonic finder
        :param preprocess: whether to perform pre-processing on the signals
        :param on_progress: the progress callback
        :return: list containing the output from each process
        """
        # Whether to parallelize the algorithm for each calculation.
        parallel = len(signals) < Scheduler.optimal_process_count()

        self.stop()
        self.scheduler = Scheduler(
            progress_callback=on_progress, run_in_thread=self.should_run_in_thread
        )

        return await self.scheduler.map(
            target=harmonic_wrapper,
            args=[
                (preprocess, sig.signal, params, *params.args(), parallel, params.crop)
                for sig in signals
            ],
        )

    async def coro_phase_coherence(
        self,
        signals: SignalPairs,
        params: PCParams,
        on_progress: Callable[[int, int], None],
    ) -> List[Tuple]:
        """
        Performs wavelet phase coherence between signal pairs. Used in "wavelet phase coherence".

        :param signals: the pairs of signals
        :param params: the parameters which are used in the algorithm
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(
            progress_callback=on_progress, run_in_thread=self.should_run_in_thread
        )

        return await self.scheduler.map(
            target=_phase_coherence,
            args=[(pair, params) for pair in signals.get_pairs()],
            subtasks=params.surr_count,
            process_type=mp.Process,
            queue_type=mp.Queue,
        )

    async def coro_ridge_extraction(
        self, params: REParams, on_progress: Callable[[int, int], None]
    ) -> List[Tuple]:
        """
        Performs ridge extraction on wavelet transforms. Used in "ridge extraction and filtering".

        :param params: the parameters which are used in the algorithm
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(
            progress_callback=on_progress, run_in_thread=self.should_run_in_thread
        )

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
        intervals: Tuple,
        on_progress: Callable[[int, int], None],
    ) -> List[Tuple]:
        """
        Performs bandpass filter on signals. Used in "ridge extraction and filtering".

        :param signals: the signals
        :param intervals: the intervals to calculate bandpass filter on
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(
            progress_callback=on_progress, run_in_thread=self.should_run_in_thread
        )

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
    ) -> List[Tuple]:
        """
        Performs Bayesian inference on signal pairs. Used in "dynamical Bayesian inference".

        :param signals: the signals
        :param paramsets: the parameter sets to use in the algorithm
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(
            progress_callback=on_progress, run_in_thread=self.should_run_in_thread
        )

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
    ) -> List[Tuple]:
        """
        Performs wavelet bispectrum analysis on signal pairs.
        Used in "wavelet bispectrum analysis".

        :param signals: the signal pairs
        :param params: the parameters to use in the algorithm
        :param on_progress: progress callback
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(
            progress_callback=on_progress, run_in_thread=self.should_run_in_thread
        )

        return await self.scheduler.map(
            target=_bispectrum_analysis,
            args=[(*pair, params) for pair in signals.get_pairs()],
            subtasks=4,
            process_type=mp.Process,
            queue_type=mp.Queue,
        )

    async def coro_biphase(
        self,
        signals: SignalPairs,
        fs: float,
        f0: float,
        fr: Tuple[float, float],
        on_progress: Callable[[int, int], None],
    ) -> List[Tuple]:
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
        self.scheduler = Scheduler(
            progress_callback=on_progress, run_in_thread=self.should_run_in_thread
        )

        args = [
            (s1, s2, fs, f0, fr, s1.output_data.opt) for s1, s2 in signals.get_pairs()
        ]
        return await self.scheduler.map(
            target=_biphase, args=args, process_type=mp.Prcess, queue_type=mp.Queue
        )

    async def coro_preprocess(
        self, signals: Union[TimeSeries, List[TimeSeries]], fmin: float, fmax: float
    ) -> List[ndarray]:
        """
        Performs preprocessing on a single signal.

        :param signals: the signal or signals to perform pre-processing on
        :param fmin: the minimum frequency
        :param fmax: the maximum frequency
        :return: list containing the output from each process
        """
        self.stop()
        self.scheduler = Scheduler(run_in_thread=True)

        if isinstance(signals, TimeSeries):
            signals = [signals]

        args = [(s.signal, s.frequency, fmin, fmax) for s in signals]
        return await self.scheduler.map(
            target=pymodalib.preprocess,
            args=args,
            process_type=mp.Process,
            queue_type=mp.Queue,
        )

    def stop(self):
        """
        Stops the tasks in progress. The MPHandler instance can be reused.
        """
        if self.scheduler:
            self.scheduler.terminate()


def harmonic_wrapper(preprocess, signal, params, *args, **kwargs):
    if preprocess:
        signal = pymodalib.preprocess(signal, params.fs, None, None)

    return pymodalib.harmonicfinder(signal, *args, **kwargs)
