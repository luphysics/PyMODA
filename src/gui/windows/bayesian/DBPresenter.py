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

import numpy as np
from PyQt5.QtWidgets import QDialog, QListWidgetItem

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.windows.bayesian.DBOutputData import DBOutputData
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

        # The parameter sets. The key for each param set is the result
        # of `ParamSet.to_string()`.
        self.param_sets: Dict[Tuple[str, str], ParamSet] = {}

    def calculate(self, calculate_all=True):
        asyncio.ensure_future(self.coro_calculate())

    async def coro_calculate(self):
        if self.mp_handler:
            self.mp_handler.stop()

        self.mp_handler = MPHelper()
        data = await self.mp_handler.coro_bayesian(self.signals,
                                                   self.get_paramsets(),
                                                   self.on_progress_updated)

        print("Dynamical Bayesian inference completed.")

        for d in data:
            self.on_bayesian_inference_completed(*d)

        self.plot_bayesian()

    def on_bayesian_inference_completed(self,
                                        signal_name: str,
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
                                        surr_cpl2):
        signal = self.signals.get(signal_name)

        signal.db_data = DBOutputData(tm,
                                      p1,
                                      p2,
                                      cpl1,
                                      cpl2,
                                      cf1,
                                      cf2,
                                      mcf1,
                                      mcf2,
                                      surr_cpl1,
                                      surr_cpl2)

    def plot_bayesian(self):
        signal = self.get_selected_signal_pair()[0]

        times = signal.times
        data: DBOutputData = signal.db_data

        if self.view.is_triple_plot:
            self.plot_bayesian2d(times, data)
        else:
            self.plot_bayesian3d(data)

    def plot_bayesian2d(self, times, data):
        self.view.db_plot_top.plot(times, data.p1)
        self.view.db_plot_middle.plot(times, data.p2)

        self.view.db_plot_bottom.plot(data.tm, data.cpl1)
        self.view.db_plot_bottom.plot(data.tm, data.cpl2)
        self.view.db_plot_bottom.plot(data.tm, data.surr_cpl1)
        self.view.db_plot_bottom.plot(data.tm, data.surr_cpl2)

        self.view.db_plot_bottom.set_xrange(times[0], times[-1])

    def plot_bayesian3d(self, data):
        x1 = np.arange(0, 2 * np.pi, 0.13)
        y1 = x1

        z1 = data.mcf1
        z2 = data.mcf2

        x1, y1 = np.meshgrid(x1, y1)
        x2, y2 = x1, y1

        self.view.db3d_plot_left.plot(x1, y1, z1)
        self.view.db3d_plot_right.plot(x2, y2, z2)

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
        return self.param_sets.get((text1, text2,))

    def get_paramsets(self) -> List[ParamSet]:
        return list(self.param_sets.values())

    def has_paramset(self, text1, text2):
        return self.get_paramset(text1, text2) is not None

    def add_paramset(self, params: ParamSet):
        self.param_sets[params.to_string()] = params

    def delete_paramset(self, text1: str, text2: str):
        try:
            del self.param_sets[(text1, text2)]
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
