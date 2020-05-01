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
from typing import Optional, Tuple, List

from PyQt5 import QtGui
from pymodalib.utils.parameters import float_or_none

from data import resources
from gui import Application
from gui.components.FreqComponent import FreqComponent
from gui.windows.common.BaseTFWindow import BaseTFWindow
from gui.windows.groupcoherence.GCPresenter import GCPresenter
from gui.windows.groupcoherence.GCViewProperties import GCViewProperties
from gui.windows.groupcoherence.LoadGroupDataDialog import LoadGroupDataDialog
from utils.decorators import floaty, inty


class GCWindow(GCViewProperties, BaseTFWindow, FreqComponent):
    """
    The group phase coherence window.
    """

    name = "Group Phase Coherence"

    def __init__(self, application: Application):
        GCViewProperties.__init__(self)
        BaseTFWindow.__init__(self, application, GCPresenter(self))

        FreqComponent.__init__(self, self.line_fmax, self.line_fmin, self.line_res)
        self.presenter.init()

    def setup_ui(self):
        super().setup_ui()

        amp = self.amplitude_plot()
        amp.set_xlabel("Overall Coherence")
        amp.hide()

        self.btn_calculate_single.hide()
        self.btn_calculate_all.setText("Calculate coherence")

        self.btn_stat_calc.clicked.connect(self.presenter.calculate_statistical_test)
        self.btn_stat_add.clicked.connect(self.add_frequency_band)
        self.btn_stat_del.clicked.connect(self.delete_frequency_band)
        self.list_stat.itemSelectionChanged.connect(self.on_frequency_band_selected)

        self.groupbox_stats.setEnabled(False)

        for p in (self.plot_1a, self.plot_1b, self.plot_2a, self.plot_2b):
            p.toolbar.hide()

    def get_frequency_bands(self) -> List[Tuple[float, float]]:
        bands = []
        for i in range(self.list_stat.count()):
            text = self.list_stat.item(i).text()

            f1, f2 = text.split(", ")
            f1, f2 = float_or_none(f1), float_or_none(f2)
            bands.append((f1, f2))

        return bands

    def add_frequency_band(self, band=None) -> None:
        f1, f2 = band or self._get_freq_band()
        self.list_stat.addItem(f"{f1}, {f2}")
        self.list_stat.setCurrentRow(self.list_stat.count() - 1)

    def delete_frequency_band(self) -> None:
        to_remove = self._get_freq_band()
        bands = self.get_frequency_bands()

        self.list_stat.clear()
        for b in bands:
            if b != to_remove:
                self.add_frequency_band(b)

    def on_frequency_band_selected(self) -> None:
        try:
            selected = self.list_stat.selectedItems()[0].text()
        except IndexError:
            return

        f1, f2 = selected.split(", ")

        self.line_stat_fmin.setText(f"{f1}")
        self.line_stat_fmax.setText(f"{f2}")

    def _get_freq_band(self) -> Tuple[float, float]:
        """
        Gets the frequency band from the "fmin" and "fmax" QLineEdits.

        Returns
        -------
        Tuple[float, float]
            The frequency band, sorted so the first value will always be smaller than the second.
        """
        f1, f2 = (
            float_or_none(self.line_stat_fmin.text()),
            float_or_none(self.line_stat_fmax.text()),
        )

        if f2 and f1 > f2:
            f1, f2 = f2, f1

        return f1, f2

    def on_calculate_stopped(self) -> None:
        super(GCWindow, self).on_calculate_stopped()
        self.btn_calculate_single.hide()
        self.btn_calculate_all.setText("Calculate coherence")

    def select_file(self) -> None:
        self.files = LoadGroupDataDialog().get_result()
        if self.files:
            self.presenter.on_file_selected(self.files)

    def get_layout_file(self) -> str:
        return resources.get("layout:window_group_coherence.ui")

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        super().closeEvent(e)
        self.presenter.on_close()

    def get_wt_wft_type(self) -> str:
        return self.combo_wavelet_type.currentText()

    def get_analysis_type(self) -> str:
        return super().get_analysis_type()

    @floaty
    def get_percentile(self) -> Optional[float]:
        return self.line_percentile.text()

    def setup_signal_listview(self) -> None:
        """
        Override to do nothing.
        """

    def setup_xlim_edits(self) -> None:
        """
        Override to do nothing.
        """
