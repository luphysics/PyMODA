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

from data import resources
from gui.windows.base.analysis.BaseTFWindow import BaseTFWindow
from gui.windows.bayesian.DBPresenter import DBPresenter
from gui.windows.bayesian.DBView import DBView
from maths.signals.TimeSeries import TimeSeries


class DBWindow(BaseTFWindow, DBView):

    def __init__(self, application, presenter: DBPresenter = None):
        DBView.__init__(self, application, presenter or DBPresenter(self))
        BaseTFWindow.__init__(self, application)

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
