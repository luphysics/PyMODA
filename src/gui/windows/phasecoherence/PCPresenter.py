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
from typing import Tuple

from PyQt5.QtWidgets import QListWidgetItem

from gui.windows.common.BaseTFPresenter import BaseTFPresenter
from gui.dialogs.FrequencyDialog import FrequencyDialog
from processes.MPHandler import MPHandler
from maths.params.PCParams import PCParams
from maths.params.TFParams import create
from maths.signals.SignalPairs import SignalPairs
from maths.signals.TFOutputData import TFOutputData
from maths.signals.TimeSeries import TimeSeries


class PCPresenter(BaseTFPresenter):

    def __init__(self, view):
        super().__init__(view)

        from gui.windows.phasecoherence.PCWindow import PCWindow
        self.view: PCWindow = self.view
        self.is_calculating_all = True

    def calculate(self, calculate_all: bool):
        asyncio.ensure_future(self.coro_calculate(calculate_all))
        print("Started calculation...")

    async def coro_calculate(self, calculate_all: bool):
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
        self.surrogate_count = self.view.get_surr_count()
        self.surrogates_enabled = self.view.get_surr_enabled()

        self.mp_handler = MPHandler()

        self.view.main_plot().set_log_scale(logarithmic=True)
        self.view.amplitude_plot().set_log_scale(logarithmic=True)

        self.view.on_calculate_started()
        data = await self.mp_handler.coro_transform(params=params, on_progress=self.on_progress_updated)

        for d in data:
            self.on_transform_completed(*d)

        all_data = await self.coro_phase_coherence(self.signals_calc, params, self.on_progress_updated)

        for d in all_data:
            self.on_phase_coherence_completed(*d)

        self.plot_phase_coherence()
        self.view.on_calculate_stopped()
        self.on_all_tasks_completed()
        print("Finished calculating phase coherence.")

    async def coro_phase_coherence(self, signals, params, on_progress):
        print("Finished wavelet transform. Calculating phase coherence...")
        return await self.mp_handler.coro_phase_coherence(signals, params, on_progress)

    def on_transform_completed(self, name, times, freq, values, ampl, powers, avg_ampl, avg_pow):
        print(f"Calculated wavelet transform for '{name}'")

        t = self.signals.get(name)
        t.output_data = TFOutputData(
            times,
            values,
            ampl,
            freq,
            powers,
            avg_ampl,
            avg_pow,
        )

    def on_phase_coherence_completed(self, signal_pair, tpc, pc, pdiff, surrogate_avg):
        s1, s2 = signal_pair

        d = s1.output_data
        d.overall_coherence = pc
        d.phase_coherence = tpc
        d.surrogate_avg = surrogate_avg

        sig = self.signals.get(s1.name)
        sig.output_data = d

    def plot_phase_coherence(self):
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

    async def coro_load_data(self):
        self.signals = SignalPairs.from_file(self.open_file)

        if not self.signals.has_frequency():
            freq = await FrequencyDialog().coro_get()

            if freq:
                self.set_frequency(freq)
                self.on_data_loaded()
            else:
                raise Exception("Frequency was None. Perhaps it was mistyped?")

    def on_data_loaded(self):
        self.view.update_signal_listview(self.signals.get_pair_names())
        self.plot_signal_pair()

    def plot_signal_pair(self):
        self.view.plot_signal_pair(self.get_selected_signal_pair())

    def get_selected_signal_pair(self) -> Tuple[TimeSeries, TimeSeries]:
        return self.signals.get_pair_by_name(self.selected_signal_name)

    def get_selected_signal_pair_data(self) -> TFOutputData:
        return self.get_selected_signal_pair()[0].output_data

    def on_signal_selected(self, item):
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

    def get_total_tasks_count(self) -> int:
        count = len(self.signals) if self.is_calculating_all else 2
        count += count // 2

        if self.surrogates_enabled:
            count += count * self.surrogate_count // 2

        return count
