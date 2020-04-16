#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2020 Lancaster University
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
from gui.components.PreprocessComponent import PreprocessComponent
from gui.components.SingleSignalComponent import SingleSignalComponent
from gui.components.SurrogateComponent import SurrogateComponent
from gui.windows.common.BaseTFWindow import BaseTFWindow
from gui.windows.harmonics.DHPresenter import DHPresenter
from gui.windows.harmonics.DHViewProperties import DHViewProperties
from utils.decorators import floaty


class DHWindow(
    DHViewProperties,
    PreprocessComponent,
    BaseTFWindow,
    SingleSignalComponent,
    SurrogateComponent,
):
    """
    The "Detecting Harmonics" window.
    """

    def __init__(self, application):
        DHViewProperties.__init__(self)
        BaseTFWindow.__init__(self, application, DHPresenter(self))
        PreprocessComponent.__init__(self, self.plot_preproc)

        SingleSignalComponent.__init__(self, self.signal_plot())

        SurrogateComponent.__init__(
            self, self.slider_surrogate_2, self.line_surrogate_2
        )

        self.presenter.init()

    def on_calculate_started(self) -> None:
        super(DHWindow, self).on_calculate_started()

    def on_calculate_stopped(self) -> None:
        super(DHWindow, self).on_calculate_stopped()

    def setup_ui(self) -> None:
        super().setup_ui()

        self.combo_plot_type.currentIndexChanged.connect(self.on_plot_type_changed)
        self.radio_preproc_on.toggled.connect(self.on_preprocess_toggled)

    def on_preprocess_toggled(self) -> None:
        if not self.get_preprocess():
            self.plot_preproc.clear()
        else:
            self.presenter.plot_preprocessed_signal()

    def get_layout_file(self) -> str:
        return resources.get("layout:window_harmonics.ui")

    def get_plot_index(self) -> int:
        return self.combo_plot_type.currentIndex()

    def on_plot_type_changed(self) -> None:
        self.presenter.update_plots()

    @floaty
    def get_fmin(self) -> Optional[float]:
        return self.line_fmin.text()

    @floaty
    def get_fmax(self) -> Optional[float]:
        return self.line_fmax.text()

    @floaty
    def get_time_res(self) -> Optional[float]:
        return self.line_res.text()

    @floaty
    def get_sigma(self) -> Optional[float]:
        return self.line_sigma.text()
