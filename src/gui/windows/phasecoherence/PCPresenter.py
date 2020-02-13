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
import asyncio
from typing import Tuple, List, Dict, Optional

import numpy as np
from PyQt5.QtWidgets import QListWidgetItem

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.common.BaseTFPresenter import BaseTFPresenter
from maths.params.PCParams import PCParams
from maths.params.TFParams import create
from maths.signals.SignalPairs import SignalPairs
from maths.signals.TimeSeries import TimeSeries
from maths.signals.data.TFOutputData import TFOutputData
from processes.MPHandler import MPHandler
from utils.decorators import override
from utils.dict_utils import sanitise


class PCPresenter(BaseTFPresenter):
    def __init__(self, view):
        super().__init__(view)

        from gui.windows.phasecoherence.PCWindow import PCWindow

        self.view: PCWindow = self.view
        self.is_calculating_all = True

    def calculate(self, calculate_all: bool) -> None:
        asyncio.ensure_future(self.coro_calculate(calculate_all))
        print("Started calculation...")

    async def coro_calculate(self, calculate_all: bool) -> None:
        self.view.enable_save_data(False)
        self.is_calculating_all = calculate_all

        if self.mp_handler:
            self.mp_handler.stop()

        self.is_plotted = False
        self.invalidate_data()

        self.view.main_plot().clear()
        self.view.main_plot().set_in_progress(True)
        self.view.amplitude_plot().clear()
        self.view.amplitude_plot().set_in_progress(True)

        params = self.get_params(all_signals=calculate_all)
        self.params = params

        self.surrogate_count = self.view.get_surr_count()
        self.surrogates_enabled = self.view.get_surr_enabled()

        self.mp_handler = MPHandler()

        self.view.main_plot().set_log_scale(logarithmic=True)
        self.view.amplitude_plot().set_log_scale(logarithmic=True)

        self.view.on_calculate_started()
        data = await self.mp_handler.coro_transform(
            params=params, on_progress=self.on_progress_updated
        )

        for d in data:
            self.on_transform_completed(*d)

        all_data = await self.coro_phase_coherence(
            self.signals_calc, params, self.on_progress_updated
        )

        for d in all_data:
            self.on_phase_coherence_completed(*d)

        self.plot_phase_coherence()
        self.view.on_calculate_stopped()
        self.on_all_tasks_completed()
        print("Finished calculating phase coherence.")

    async def coro_phase_coherence(self, signals, params, on_progress) -> List[tuple]:
        print("Finished wavelet transform. Calculating phase coherence...")
        return await self.mp_handler.coro_phase_coherence(signals, params, on_progress)

    def on_transform_completed(
        self, name, times, freq, values, ampl, powers, avg_ampl, avg_pow, opt=None
    ) -> None:
        print(f"Calculated wavelet transform for '{name}'")

        if opt:
            self.params.set_item("fmin", opt.get("fmin"))

        t = self.signals.get(name)
        t.output_data = TFOutputData(
            times, values, ampl, freq, powers, avg_ampl, avg_pow
        )

    def on_phase_coherence_completed(
        self, signal_pair, tpc, pc, pdiff, surrogate_avg
    ) -> None:
        s1, s2 = signal_pair

        d = s1.output_data
        d.overall_coherence = pc
        d.phase_coherence = tpc
        d.surrogate_avg = surrogate_avg

        sig = self.signals.get(s1.name)
        sig.output_data = d

        self.enable_save_data(True)

    def plot_phase_coherence(self) -> None:
        data = self.get_selected_signal_pair_data()
        times = data.times
        freq = data.freq
        values = data.phase_coherence

        main = self.view.main_plot()
        ampl = self.view.amplitude_plot()

        if not data.has_phase_coherence():
            main.clear()
            ampl.clear()
            return

        main.update_xlabel("Time (s)")
        main.update_xlabel("Frequency (Hz)")
        main.plot(times, values, freq)

        ampl.update_xlabel("Overall coherence")
        ampl.update_ylabel("Frequency (Hz)")
        ampl.plot(data.overall_coherence, freq, surrogates=data.surrogate_avg)

    def load_data(self) -> None:
        self.signals = SignalPairs.from_file(self.open_file)

        if not self.signals.has_frequency():
            freq = FrequencyDialog().run_and_get()

            if freq:
                self.set_frequency(freq)
                self.on_data_loaded()
            else:
                raise Exception("Frequency was None. Perhaps it was mistyped?")

    @override
    def get_data_to_save(self) -> Optional[Dict]:
        if not self.params:
            return None

        output_data: List[TFOutputData] = [
            s[0].output_data for s in self.signals.get_pairs()
        ]
        cols = len(output_data)

        first = [d for d in output_data if d.is_valid()][0]

        coh = np.empty((*first.phase_coherence.shape, cols))
        avg_coh = np.empty((first.overall_coherence.shape[0], cols))

        avg_surrogates = np.empty((len(first.surrogate_avg), cols))

        amp = np.empty((*first.ampl.shape, cols))
        avg_amp = np.empty((first.avg_ampl.shape[0], cols))

        freq = first.freq
        time = first.times

        preproc = []  # TODO: Save this

        for index, d in enumerate(output_data):
            if d.is_valid():
                avg_surrogates[:, index] = d.surrogate_avg[:, 0]

                coh[:, :, index] = d.phase_coherence[:, :]
                avg_coh[:, index] = d.overall_coherence[:, index]

                amp[:, :, index] = d.ampl[:, :]
                avg_amp[:, index] = d.avg_ampl[:]
            else:
                avg_surrogates[:, index] = np.NAN

                amp[:, :, index] = np.NAN
                coh[:, :, index] = np.NAN

                avg_amp[:, index] = np.NAN
                avg_coh[:, index] = np.NAN

        pc_data = {
            "coherence": coh,
            "avg_coherence": avg_coh,
            "avg_surrogates": avg_surrogates,
            "amplitude": amp,
            "avg_amplitude": avg_amp,
            "frequency": freq,
            "time": time,
            "preprocessed_signals": preproc,
            **self.params.items_to_save(),
        }
        return {"PCData": sanitise(pc_data)}

    def on_data_loaded(self) -> None:
        self.view.update_signal_listview(self.signals.get_pair_names())
        self.plot_signal_pair()

    def plot_signal_pair(self) -> None:
        self.view.plot_signal_pair(self.get_selected_signal_pair())

    def get_selected_signal_pair(self) -> Tuple[TimeSeries, TimeSeries]:
        return self.signals.get_pair_by_name(self.selected_signal_name)

    def get_selected_signal_pair_data(self) -> TFOutputData:
        return self.get_selected_signal_pair()[0].output_data

    def on_signal_selected(self, item) -> None:
        if isinstance(item, QListWidgetItem):
            name = item.text()
        else:
            name = item

        self.signals.reset()
        if name != self.selected_signal_name:
            print(f"Selected '{name}'")
            self.selected_signal_name = name
            self.plot_signal_pair()
            self.view.on_xlim_edited()
            self.plot_phase_coherence()

    def get_params(self, all_signals=True) -> PCParams:
        if all_signals:
            self.signals_calc = self.signals
        else:
            self.signals_calc = self.signals.only(self.selected_signal_name)

        return create(
            params_type=PCParams,
            signals=self.signals_calc,
            fmin=self.view.get_fmin(),
            fmax=self.view.get_fmax(),
            f0=self.view.get_f0(),
            wavelet=self.view.get_wt_wft_type(),
            cut_edges=self.view.get_cut_edges(),
            preprocess=self.view.get_preprocess(),
            transform="wt",
            surr_count=self.view.get_surr_count(),
            surr_method=self.view.get_surr_method(),
            surr_enabled=self.view.get_surr_enabled(),
        )
