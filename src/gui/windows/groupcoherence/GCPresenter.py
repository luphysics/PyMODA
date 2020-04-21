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
from typing import Dict, Optional

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.plotting.plots.GroupCoherencePlot import GroupCoherencePlot
from gui.windows.common.BaseTFPresenter import BaseTFPresenter
from maths.signals.SignalGroups import SignalGroups
from processes.MPHandler import MPHandler
from utils import args
from utils.decorators import override


class GCPresenter(BaseTFPresenter):
    def __init__(self, view):
        super().__init__(view)

        from gui.windows.groupcoherence.GCWindow import GCWindow

        self.view: GCWindow = self.view
        self.results = None
        self.stats = None

    def calculate(self, _: bool) -> None:
        asyncio.ensure_future(self.coro_calculate())
        print("Started calculation. This may take some time...")

    def init(self) -> None:
        self.view.select_file()

    async def coro_calculate(self) -> None:
        self.view.enable_save_data(False)
        self.view.groupbox_stats.setEnabled(False)

        if self.mp_handler:
            self.mp_handler.stop()

        self.is_plotted = False
        self.invalidate_data()

        self.view.main_plot().clear()
        self.view.main_plot().set_in_progress(True)
        self.view.amplitude_plot().clear()
        self.view.amplitude_plot().set_in_progress(True)

        params = self.get_params()
        self.params = params

        self.mp_handler = MPHandler()

        self.view.on_calculate_started()

        sig1a, sig1b, sig2a, sig2b = self.signals.get_all()
        if sig2a is None:
            self.results = (
                await self.mp_handler.coro_group_coherence(
                    sig1a,
                    sig1b,
                    fs=self.signals.frequency,
                    on_progress=self.on_progress_updated,
                    **params,
                )
            )[0]
        else:
            self.results = (
                await self.mp_handler.coro_dual_group_coherence(
                    sig1a,
                    sig1b,
                    sig2a,
                    sig2b,
                    fs=self.signals.frequency,
                    on_progress=self.on_progress_updated,
                    **params,
                )
            )[0]

        self.view.groupbox_stats.setEnabled(True)
        self.enable_save_data(True)
        self.update_plots()
        self.view.on_calculate_stopped()
        self.on_all_tasks_completed()

    def calculate_statistical_test(self) -> None:
        asyncio.ensure_future(self.coro_statistical_test())

    async def coro_statistical_test(self) -> None:
        bands = self.view.get_frequency_bands()
        if not bands:
            return

        try:
            freq, coh1, coh2, _, _ = self.results
        except ValueError:
            freq, coh1, _ = self.results
            coh2 = None

        self.view.on_calculate_started()
        self.stats = await self.mp_handler.coro_statistical_test(
            freq, coh1, coh2, bands, self.on_progress_updated
        )

        self.view.on_calculate_stopped()
        self.update_table()

    def update_table(self) -> None:
        if not self.stats:
            return

        tbl: QTableView = self.view.tbl_stat

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Frequency range", "Significance"])

        tbl.setModel(model)

        for key, value in self.stats.items():
            f1, f2 = key
            model.appendRow([QStandardItem(f"{f1}-{f2}Hz"), QStandardItem(f"{value}")])

        tbl.resizeColumnsToContents()

    def update_plots(self) -> None:
        main: GroupCoherencePlot = self.view.main_plot()
        if not self.results:
            main.clear()
            return

        try:
            freq, coh1, coh2, surr1, surr2 = self.results
            main.plot(
                freq, coh1, coh2, average="median", percentile=self.params["percentile"]
            )
        except ValueError:
            freq, coh1, surr1 = self.results
            main.plot(
                freq, coh1, None, average="median", percentile=self.params["percentile"]
            )

    def load_data(self) -> None:
        self.signals = SignalGroups.from_files(self.open_files)

        if not self.signals.has_frequency():
            freq = FrequencyDialog().run_and_get()

            if freq:
                self.set_frequency(freq)
                self.on_data_loaded()
            else:
                raise Exception("Frequency was None. Perhaps it was mistyped?")

    def on_file_selected(self, files: str):
        self.open_files = files
        print(f"Opening {files}...")
        self.view.update_title()
        self.load_data()

    @override
    async def coro_get_data_to_save(self) -> Optional[Dict]:
        if not self.params:
            return None

        return {"GCData": None}  # TODO GC

    def on_data_loaded(self) -> None:
        self.plot_signal_groups()

    def plot_signal_groups(self) -> None:
        signals = self.signals.get_all()
        times = self.signals.times

        for plot, sig, title in zip(
            (
                self.view.plot_1a,
                self.view.plot_1b,
                self.view.plot_2a,
                self.view.plot_2b,
            ),
            signals,
            (
                "Group 1, signals A",
                "Group 1, signals B",
                "Group 2, signals A",
                "Group 2, signals B",
            ),
        ):
            if sig is not None:
                plot.clear()
                for index in range(sig.shape[0]):
                    plot.plotxy(times, sig[index, :], clear=False)
                    plot.axes.set_title(title)
                    plot.axes.xaxis.set_label_position("bottom")

    def get_params(self) -> Dict:
        """
        Gets the parameters to provide to the group coherence function.
        Includes the keyword-arguments passed to the wavelet transform.

        Returns
        -------
        Dict
            Dictionary with **kwargs for group coherence.
        """
        return {
            "percentile": self.view.get_percentile(),
            "max_surrogates": self.view.get_max_surrogates(),
            "fmin": self.view.get_fmin(),
            "fmax": self.view.get_fmax(),
            "resolution": self.view.get_f0(),
            "cut_edges": self.view.get_cut_edges(),
            "wavelet": self.view.get_wt_wft_type(),
            "preprocess": self.view.get_preprocess(),
            "implementation": "python" if args.python_wt() else "matlab",
        }

    def plot_preprocessed_signal(self) -> None:
        """
        Do nothing.
        """
