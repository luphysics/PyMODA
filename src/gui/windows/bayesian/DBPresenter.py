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
from typing import Tuple

from PyQt5.QtWidgets import QDialog, QListWidgetItem

from gui.common.BaseTFPresenter import BaseTFPresenter
from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.bayesian.DBView import DBView
from maths.signals.SignalPairs import SignalPairs
from maths.signals.TimeSeries import TimeSeries


class DBPresenter(BaseTFPresenter):
    """
    Presenter for the dynamical Bayesian inference window.
    """

    def __init__(self, view: DBView):
        BaseTFPresenter.__init__(self, view)

        # Improve type hints.
        self.signals: SignalPairs = self.signals
        self.view: DBView = view

    def load_data(self):
        self.signals = SignalPairs.from_file(self.open_file)

        if not self.signals.has_frequency():
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

    def get_selected_signal_pair(self) -> Tuple[TimeSeries, TimeSeries]:
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
