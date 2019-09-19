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
from typing import Tuple, Dict, List

from PyQt5.QtWidgets import QDialog, QListWidgetItem

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.bayesian.ParamSet import ParamSet
from gui.windows.common.BaseTFPresenter import BaseTFPresenter
from maths.multiprocessing.MPHelper import MPHelper
from maths.signals.SignalPairs import SignalPairs
from maths.signals.TimeSeries import TimeSeries


class DBPresenter(BaseTFPresenter):
    """
    Presenter for the dynamical Bayesian inference window.
    """

    def __init__(self, view):
        BaseTFPresenter.__init__(self, view)

        from gui.windows.bayesian.DBWindow import DBWindow

        # Improve type hints.
        self.signals: SignalPairs = self.signals
        self.view: DBWindow = view

        self.paramsets: Dict[Tuple[str, str], ParamSet] = {}

    def calculate(self, calculate_all=True):
        asyncio.ensure_future(self.coro_calculate())

    async def coro_calculate(self):
        if self.mp_handler:
            self.mp_handler.stop()

        self.mp_handler = MPHelper()
        await self.mp_handler.coro_bayesian(self.signals,
                                            self.get_paramsets(),
                                            self.on_progress_updated)

        print("Dynamical Bayesian inference completed.")

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

    def get_paramset(self, text1, text2):
        return self.paramsets.get((text1, text2,))

    def get_paramsets(self) -> List[ParamSet]:
        return list(self.paramsets.values())

    def has_paramset(self, text1, text2):
        return self.get_paramset(text1, text2) is not None

    def add_paramset(self, params: ParamSet):
        self.paramsets[params.to_string()] = params

    def delete_paramset(self, text1: str, text2: str):
        try:
            del self.paramsets[(text1, text2)]
        except KeyError:
            pass

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
