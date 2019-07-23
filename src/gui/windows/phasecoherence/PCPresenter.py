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
from maths.algorithms.params import TFParams
from maths.algorithms.wpc import tlphcoh
from maths.multiprocessing.MPHelper import MPHelper


class PCPresenter(BaseTFPresenter):

    def __init__(self, view: PCView):
        super().__init__(view)

    def calculate(self):
        self.finished = []

        if self.mp_handler:
            self.mp_handler.stop()

        self.is_plotted = False
        self.view.main_plot().clear()
        self.view.main_plot().set_in_progress(True)
        self.invalidate_data()

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

    def on_transform_completed(self, name, times, freq, ampl, powers, avg_ampl, avg_pow):
        t = self.signals.get(name)
        t.output_data = TFOutputData(
            times,
            ampl,
            freq,
            powers,
            avg_ampl,
            avg_pow,
        )

        print(f"Calculated wavelet transform for '{name}'")
        self.finished.append(name)

        if len(self.finished) == len(self.signals):
            self.on_all_transforms_completed()

    def on_all_transforms_completed(self):
        s1, s2 = self.signals.get_pair_by_index(0)

        wt1 = s1.output_data.ampl
        wt2 = s2.output_data.ampl

        freq = s2.output_data.freq
        fs = s2.frequency

        tpc = tlphcoh(wt1, wt2, freq, fs)

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
            self.plot_output()

    def plot_output(self):
        pass  # TODO: implement

    def get_params(self):
        return TFParams.create(
            signals=self.signals,
            fmin=self.view.get_fmin(),
            fmax=self.view.get_fmax(),
            f0=self.view.get_f0(),
            wavelet=self.view.get_wt_wft_type(),
            cut_edges=self.view.get_cut_edges(),
            preprocess=self.view.get_preprocess(),
        )
