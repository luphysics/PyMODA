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
from typing import Callable, List

import numpy as np
from multiprocess import Queue, Process
from nptyping import Array
from scipy.signal import hilbert

from gui.windows.bayesian.ParamSet import ParamSet
from maths.algorithms.bayesian import bayes_main, dirc, CFprint
from maths.algorithms.loop_butter import loop_butter
from maths.algorithms.matlab_utils import sort2d
from maths.algorithms.surrogates import surrogate_calc
from maths.algorithms.wpc import wpc, wphcoh
from maths.multiprocessing import mp_utils
from maths.multiprocessing.Scheduler import Scheduler
from maths.multiprocessing.Task import Task
from maths.multiprocessing.mp_utils import setup_matlab_runtime
from maths.num_utils import matlab_to_numpy
from maths.params.BAParams import BAParams
from maths.params.PCParams import PCParams
from maths.params.REParams import REParams
from maths.params.TFParams import TFParams, _wft, _fmin, _fmax
from maths.signals.SignalPairs import SignalPairs
from maths.signals.Signals import Signals
from maths.signals.TimeSeries import TimeSeries


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
                                       signal_pairs: SignalPairs,
                                       on_progress: Callable[[int, int], None]):
        pass

    def stop(self):
        """
        Stops the tasks in progress. The MPHandler can be reused.

        Removes all items from the lists of processes, queues
        and watchers.
        """
        if self.scheduler:
            self.scheduler.terminate()


def _moda_dynamic_bayesian_inference(queue: Queue, signal1: TimeSeries, signal2: TimeSeries, params: ParamSet):
    mp_utils.setup_matlab_runtime()

    import full_bayesian
    import matlab
    package = full_bayesian.initialize()

    sig1 = matlab.double(signal1.signal.tolist())
    sig2 = matlab.double(signal2.signal.tolist())

    int1 = list(params.freq_range1)
    int2 = list(params.freq_range2)

    fs = signal1.frequency
    win = params.window
    pr = params.propagation_const
    ovr = params.overlap
    bn = params.order
    ns = params.surr_count
    signif = params.confidence_level

    result = package.full_bayesian(sig1, sig2, int1, int2, fs, win, pr, ovr, bn, ns, signif)

    queue.put((signal1.name, *result))


def _dynamic_bayesian_inference(queue: Queue, signal1: TimeSeries, signal2: TimeSeries, params: ParamSet):
    sig1 = signal1.signal
    sig2 = signal2.signal

    fs = signal1.frequency
    interval1, interval2 = params.freq_range1, params.freq_range2
    bn = params.order

    bands1, _ = loop_butter(sig1, *interval1, fs)
    phi1 = np.angle(hilbert(bands1))

    bands2, _ = loop_butter(sig2, *interval2, fs)
    phi2 = np.angle(hilbert(bands2))

    p1 = phi1
    p2 = phi2

    win = params.window
    ovr = params.overlap
    pr = params.propagation_const
    signif = params.confidence_level

    ### Bayesian inference ###

    tm, cc, e = bayes_main(phi1,
                           phi2,
                           win,
                           1 / fs,
                           ovr,
                           pr,
                           0,
                           bn)

    from maths.algorithms.matlab_utils import zeros, mean

    N, s = cc.shape
    s -= 1

    cpl1 = zeros(N)
    cpl2 = zeros(N)

    q21 = zeros((s, s, N,))
    q12 = zeros(q21.shape)

    for m in range(N):
        cpl1[m], cpl2[m], _ = dirc(cc[m, :], bn)
        _, _, q21[:, :, m], q12[:, :, m] = CFprint(cc[m, :], bn)

    cf1 = q21
    cf2 = q12

    mcf1 = np.squeeze(mean(q21, 2))
    mcf2 = np.squeeze(mean(q12, 2))

    ns = params.surr_count
    surr1, _ = surrogate_calc(phi1, ns, "CPP", 0, fs)
    surr2, _ = surrogate_calc(phi2, ns, "CPP", 0, fs)

    cc_surr: List[Array] = []
    scpl1 = zeros((ns, 2,))
    scpl2 = zeros(scpl1.shape)

    for n in range(ns):
        _, _cc_surr, _ = bayes_main(surr1[n, :], surr2[n, :], win, 1 / fs, ovr, pr, 1, bn)
        cc_surr.append(_cc_surr)

        for idx in range(len(_cc_surr)):
            scpl1[n, idx], scpl2[n, idx], _ = dirc(_cc_surr[idx], bn)

    alph = signif
    alph = 1 - alph / 100

    if np.floor((ns + 1) * alph) == 0:
        surr_cpl1 = np.max(scpl1)
        surr_cpl2 = np.max(scpl2)
    else:
        K = np.floor((ns + 1) * alph)
        K = np.int(K)

        s1 = sort2d(scpl1, descend=True)
        s2 = sort2d(scpl2, descend=True)

        surr_cpl1 = s1[K, :]
        surr_cpl2 = s2[K, :]

    queue.put((
        signal1.name,
        tm,
        p1,
        p2,
        cpl1,
        cpl2,
        cf1,
        cf2,
        mcf1,
        mcf2,
        surr_cpl1,
        surr_cpl2,
    ))


def _bispectrum_analysis(params: BAParams):
    from maths.algorithms import bispec_wav_new

    signals: SignalPairs = params.signals
    sig1, sig2 = signals.get_pair_by_index(0)
    sig1 = sig1.signal.tolist()
    sig2 = sig2.signal.tolist()

    bispxxx = []
    bispppp = []
    bispxpp = []
    bisppxx = []
    surrxxx = []
    surrppp = []
    surrxpp = []
    surrpxx = []

    sigcheck = np.sum(np.abs(signals[0] - signals[1]))

    d = params.get()
    nv = d["nv"]
    ns = params.surr_count
    preprocess = d["Preprocess"]

    if sigcheck != 0:
        if preprocess:
            bispxxx = bispec_wav_new.calculate(sig1, sig1, params)
            bispxxx = np.abs(bispxxx[0])

            bispppp = bispec_wav_new.calculate(sig2, sig2, params)
            bispppp = np.abs(bispppp[0])

            bispxpp, freq, wopt, wt1, wt2 = bispec_wav_new.calculate(sig1, sig2, params)
            bispxpp = np.abs(bispxpp)

            bisppxx = bispec_wav_new.calculate(sig2, sig1, params)
            bisppxx = np.abs(bispppp[0])

            if ns > 0:
                pass  # TODO: continue later


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
    mp_utils.setup_matlab_runtime()
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
