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
from PyQt5.QtWidgets import QRadioButton, QComboBox

from gui.plotting.plots.PreprocessPlot import PreprocessPlot
from gui.windows.ViewProperties import ViewProperties


class TFViewProperties(ViewProperties):
    def __init__(self):
        self.radio_transform_wt: QRadioButton = None
        self.plot_preproc: PreprocessPlot = None

        self.combo_impl: QComboBox = None
