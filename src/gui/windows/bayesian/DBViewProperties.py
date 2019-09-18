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
from PyQt5.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QSlider, QListWidget

from gui.windows.ViewProperties import ViewProperties
from gui.windows.bayesian.DBPlot import DBPlot


class DBViewProperties(ViewProperties):

    def __init__(self):
        self.btn_add_paramset: QPushButton = None
        self.btn_delete_paramset: QPushButton = None

        self.lineedit_freq_range1_min: QLineEdit = None
        self.lineedit_freq_range1_max: QLineEdit = None
        self.lineedit_freq_range2_min: QLineEdit = None
        self.lineedit_freq_range2_max: QLineEdit = None

        self.lineedit_window_size: QLineEdit = None
        self.lineedit_overlap: QLineEdit = None
        self.lineedit_order: QLineEdit = None
        self.lineedit_confidence_level: QLineEdit = None
        self.lineedit_propagation_const: QLineEdit = None

        self.vbox_triple_plot: QVBoxLayout = None

        self.slider_surrogate: QSlider = None
        self.line_surrogate: QLineEdit = None

        self.listwidget_freq_band1: QListWidget = None
        self.listwidget_freq_band2: QListWidget = None

        self.db_plot_top: DBPlot = None
        self.db_plot_middle: DBPlot = None
        self.db_plot_bottom: DBPlot = None
