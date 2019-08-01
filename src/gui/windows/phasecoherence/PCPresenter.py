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
from maths.SignalPairs import SignalPairs
from maths.TFOutputData import TFOutputData
from maths.algorithms.PCParams import PCParams
from maths.algorithms.TFParams import TFParams, create
from maths.multiprocessing.MPHelper import MPHelper


class PCPresenter(BaseTFPresenter):

    def __init__(self, view: PCView):
        super().__init__(view)

    def calculate(self):
        if self.mp_handler:
            self.mp_handler.stop()

        self.is_plotted = False
        self.invalidate_data()

        self.view.main_plot().clear()
        self.view.main_plot().set_in_progress(True)
        self.view.amplitude_plot().clear()
        self.view.amplitude_plot().set_in_progress(True)

        params = self.get_params()

        self.mp_handler = MPHelper()
        self.mp_handler.wft(
            params=params,
            window=self.view.get_window(),
            on_result=self.on_transform_completed)

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
        if all([s.output_data.is_valid() for s in self.signals]):
            self.calculate_phase_coherence()

    def calculate_phase_coherence(self):
        mp = self.mp_handler
        mp.wpc(
            self.signals,
            params=self.get_params(),
            window=self.view.get_window(),
            on_result=self.on_phase_coherence_completed
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
        if all([s.output_data.has_phase_coherence() for s in self.signals[::2]]):
            self.plot_phase_coherence()
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

        main.set_xlabel("Time (s)")
        main.set_xlabel("Frequency (Hz)")
        main.plot(times, values, freq)

        ampl.set_xlabel("Overall coherence")
        ampl.set_ylabel("Frequency (Hz)")
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

    def plot_output(self):
        pass  # TODO: implement

    def get_params(self):
        return create(
            params_type=PCParams,
            signals=self.signals,
            fmin=self.view.get_fmin(),
            fmax=self.view.get_fmax(),
            f0=self.view.get_f0(),
            wavelet=self.view.get_wt_wft_type(),
            cut_edges=self.view.get_cut_edges(),
            preprocess=self.view.get_preprocess(),
            transform="wt",

            # TODO: add code to fetch from GUI
            surr_count=19,
            surr_method="RP"
        )
