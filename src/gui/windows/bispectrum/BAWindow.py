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
from typing import Optional

from data import resources
from gui.components.DualSignalComponent import DualSignalComponent
from gui.components.FreqComponent import FreqComponent
from gui.components.SurrogateComponent import SurrogateComponent
from gui.windows.bispectrum.BAPresenter import BAPresenter
from gui.windows.bispectrum.BAViewProperties import BAViewProperties
from gui.windows.common.BaseTFWindow import BaseTFWindow
from utils.decorators import floaty


class BAWindow(BAViewProperties, BaseTFWindow, DualSignalComponent, FreqComponent, SurrogateComponent):
    name = "Wavelet Bispectrum Analysis"

    def __init__(self, application):
        BAViewProperties.__init__(self)
        BaseTFWindow.__init__(self, application, BAPresenter(self))

        DualSignalComponent.__init__(self, self.signal_plot())
        FreqComponent.__init__(self, self.line_fmax, self.line_fmin, self.line_res)
        SurrogateComponent.__init__(self, self.slider_surrogate, self.line_surrogate)

        self.presenter.init()

    def setup_ui(self):
        super(BAWindow, self).setup_ui()
        self.btn_calculate_single.hide()

    def get_layout_file(self) -> str:
        return resources.get("layout:window_bispectrum_analysis.ui")

    @floaty
    def get_nv(self) -> Optional[float]:
        return self.lineedit_nv.text()

    @floaty
    def get_alpha(self) -> Optional[float]:
        return self.lineedit_alpha.text()
