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

from data import resources
from gui import Application
from gui.components.FreqComponent import FreqComponent
from gui.windows.common.BaseTFWindow import BaseTFWindow
from gui.windows.groupcoherence.GCPresenter import GCPresenter
from gui.windows.groupcoherence.GCViewProperties import GCViewProperties
from gui.windows.groupcoherence.LoadGroupDataDialog import LoadGroupDataDialog


class GCWindow(GCViewProperties, BaseTFWindow, FreqComponent):
    """
    The group phase coherence window.
    """

    name = "Group Phase Coherence"
    _wavelet_types = ["Lognorm", "Morlet", "Bump"]

    def __init__(self, application: Application):
        GCViewProperties.__init__(self)
        BaseTFWindow.__init__(self, application, GCPresenter(self))

        FreqComponent.__init__(self, self.line_fmax, self.line_fmin, self.line_res)
        self.presenter.init()

    def setup_ui(self):
        super().setup_ui()

        amp = self.amplitude_plot()
        amp.set_xlabel("Overall Coherence")

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

    def setup_signal_listview(self) -> None:
        """
        Override to do nothing.
        """
