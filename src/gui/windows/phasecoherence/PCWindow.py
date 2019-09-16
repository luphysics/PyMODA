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

from PyQt5 import QtGui
from PyQt5.QtWidgets import QComboBox

from data import resources
from gui import Application
from gui.common.BaseTFWindow import BaseTFWindow
from gui.components.FreqComponent import FreqComponent
from gui.components.SurrogateComponent import SurrogateComponent
from gui.windows.phasecoherence.PCPresenter import PCPresenter
from gui.windows.phasecoherence.PCViewProperties import PCViewProperties


class PCWindow(PCViewProperties, BaseTFWindow, SurrogateComponent, FreqComponent):
    """
    The phase coherence window.
    """

    name = "Wavelet Phase Coherence"

    _wavelet_types = ["Lognorm", "Morlet", "Bump"]
    _surrogate_types = ["RP", "FT", "AAFT", "IAAFT1", "IAAFT2", "WIAAFT", "tshift"]

    def __init__(self, application: Application):
        PCViewProperties.__init__(self)
        BaseTFWindow.__init__(self, application, PCPresenter(self))

        SurrogateComponent.__init__(self, self.slider_surrogate, self.line_surrogate)
        FreqComponent.__init__(self, self.line_fmax, self.line_fmin, self.line_res)

        self.presenter.init()

    def init_ui(self):
        super().init_ui()
        self.setup_surr_method()
        self.setup_surr_type()
        self.setup_analysis_type()

        amp = self.amplitude_plot()
        amp.set_xlabel("Overall Coherence")

    def plot_signal_pair(self, pair):
        plot = self.signal_plot()
        plot.plot(pair[0], clear=True)
        plot.plot(pair[1], clear=False)

    def get_layout_file(self) -> str:
        return resources.get("layout:window_phase_coherence.ui")

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        super().closeEvent(e)
        self.presenter.on_close()

    def setup_surr_type(self):
        combo = self.combo_wavelet_type
        combo.clear()

        items = self._wavelet_types
        for i in items:
            combo.addItem(i)

    def setup_analysis_type(self):
        self.radio_analysis_max.setChecked(True)

    def get_wt_wft_type(self) -> str:
        return self.combo_wavelet_type.currentText()

    def get_analysis_type(self) -> str:
        return super().get_analysis_type()

    def get_surr_method(self) -> str:
        combo: QComboBox = self.combo_method
        return combo.currentText()

    def get_surr_enabled(self) -> bool:
        return self.checkbox_surr.isChecked()

    def setup_surr_method(self):
        combo = self.combo_method
        combo.clear()

        items = self._surrogate_types
        for i in items:
            combo.addItem(i)

