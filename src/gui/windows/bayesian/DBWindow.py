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
from typing import Tuple, Optional

from data import resources
from gui.common.BaseTFWindow import BaseTFWindow
from gui.components.SurrogateComponent import SurrogateComponent
from gui.windows.bayesian.DBPresenter import DBPresenter
from gui.windows.bayesian.DBViewProperties import DBViewProperties
from maths.num_utils import float_or_none
from maths.signals.TimeSeries import TimeSeries
from utils.decorators import floaty


class DBWindow(DBViewProperties, BaseTFWindow, SurrogateComponent):

    def __init__(self, application):
        DBViewProperties.__init__(self)
        BaseTFWindow.__init__(self, application, DBPresenter(self))

        SurrogateComponent.__init__(self, self.slider_surrogate, self.line_surrogate)

        self.presenter.init()

    def get_layout_file(self) -> str:
        return resources.get("layout:window_dynamical_bayesian.ui")

    def init_ui(self):
        super().init_ui()

        self.btn_calculate_single.hide()
        self.btn_add_paramset.clicked.connect(self.on_add_paramset_clicked)
        self.btn_delete_paramset.clicked.connect(self.on_delete_paramset_clicked)

    def plot_signal_pair(self, pair: Tuple[TimeSeries, TimeSeries]):
        plot = self.signal_plot()
        plot.plot(pair[0], clear=True)
        plot.plot(pair[1], clear=False)

    def on_add_paramset_clicked(self):
        pass

    def on_delete_paramset_clicked(self):
        pass

    def setup_radio_preproc(self):
        pass

    def setup_radio_cut_edges(self):
        pass

    def setup_radio_plot(self):
        pass

    def setup_lineedit_fmin(self):
        pass

    def setup_lineedit_fmax(self):
        pass

    def setup_lineedit_res(self):
        pass

    @floaty
    def get_freq_range1(self) -> Optional[Tuple[float, float]]:
        min = float_or_none(self.lineedit_freq_range1_min.text())
        max = float_or_none(self.lineedit_freq_range1_max.text())
        return min, max

    @floaty
    def get_freq_range2(self) -> Optional[Tuple[float, float]]:
        min = float_or_none(self.lineedit_freq_range2_min.text())
        max = float_or_none(self.lineedit_freq_range2_max.text())
        return min, max

    @floaty
    def get_window_size(self) -> Optional[float]:
        return self.lineedit_window_size.text()

    @floaty
    def get_propagation_const(self) -> Optional[float]:
        return self.lineedit_propagation_const.text()

    @floaty
    def get_num_surrogates(self) -> Optional[float]:
        raise Exception("Not implemented yet.")

    @floaty
    def get_overlap(self) -> Optional[float]:
        return self.lineedit_overlap.text()

    @floaty
    def get_order(self) -> Optional[float]:
        return self.lineedit_order.text()

    @floaty
    def get_confidence_level(self) -> Optional[float]:
        return self.lineedit_confidence_level.text()
