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

from PyQt5.QtWidgets import QDialog, QListWidgetItem

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.base.analysis.BaseTFPresenter import BaseTFPresenter
from gui.windows.phasecoherence.PCView import PCView
from maths.signals.SignalPairs import SignalPairs
from maths.signals.TFOutputData import TFOutputData
from maths.params.PCParams import PCParams
from maths.params.TFParams import create
from maths.multiprocessing.MPHelper import MPHelper


class PCPresenter(BaseTFPresenter):

    def __init__(self, view: PCView):
        super().__init__(view)

    def calculate(self, calculate_all: bool):
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

        self.mp_handler = MPHelper()
        self.mp_handler.transform(
            params=params,
            window=self.view.get_window(),
            on_result=self.on_transform_completed,
            on_progress=self.on_progress_updated) # TODO: fix progress bar when calculating surrogates.

        self.view.main_plot().set_log_scale(logarithmic=True)
        self.view.amplitude_plot().set_log_scale(logarithmic=True)

        self.view.on_calculate_started()
        print("Started calculation...")

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

        # Whether all signals have finished calculating.
        if all([s.output_data.is_valid() for s in self.signals_calc]):
            self.calculate_phase_coherence()

    def calculate_phase_coherence(self):
        mp = self.mp_handler
        mp.phase_coherence(
            self.signals_calc,
            params=self.get_params(all_signals=self.is_calculating_all),
            window=self.view.get_window(),
            on_result=self.on_phase_coherence_completed,
            on_progress=self.on_progress_updated
        )
        print("Finished wavelet transform. Calculating phase coherence...")

    def on_phase_coherence_completed(self, signal_pair, tpc, pc, pdiff, surrogate_avg):
        s1, s2 = signal_pair

        d = s1.output_data
        d.overall_coherence = pc
        d.phase_coherence = tpc
        d.surrogate_avg = surrogate_avg

        sig = self.signals.get(s1.name)
        sig.output_data = d

        # If all calculations have completed.
        if all([s.output_data.has_phase_coherence() for s in self.signals_calc[::2]]):
            self.plot_phase_coherence()
            self.view.on_calculate_stopped()
            self.on_all_tasks_completed()
            print("Finished calculating phase coherence.")

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

    def load_data(self):
        self.signals = SignalPairs.from_file(self.open_file)
        if not self.signals.get_signals().has_frequency():
            dialog = FrequencyDialog(self.on_freq_changed)
            code = dialog.exec()
            if code == QDialog.Accepted:
                self.set_frequency(self.freq)
                self.on_data_loaded()

    def on_data_loaded(self):
        self.view.update_signal_listview(self.signals.get_pair_names())
        self.plot_signal_pair()

    def plot_signal_pair(self):
        self.view.plot_signal_pair(self.get_selected_signal_pair())

    def get_selected_signal_pair(self):
        return self.signals.get_pair_by_name(self.selected_signal_name)

    def get_selected_signal_pair_data(self):
        return self.get_selected_signal_pair()[0].output_data

    def plot_preprocessed_signal(self):
        """No preprocessing plot in phase coherence window, so remove functionality."""
        pass

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

    def get_params(self, all_signals=True):
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
