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
from PyQt5.QtWidgets import (
    QLineEdit,
    QSlider,
    QComboBox,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QListWidget,
    QCheckBox,
    QRadioButton,
)

from gui.plotting.plots.AmplitudePlot import AmplitudePlot
from gui.plotting.plots.ColorMeshPlot import ColorMeshPlot
from gui.windows.ViewProperties import ViewProperties
from gui.windows.bispectrum.BAPlot import BAPlot


class BAViewProperties(ViewProperties):
    def __init__(self):
        """Define properties introduced by the .ui file."""
        self.line_surrogate: QLineEdit = None
        self.slider_surrogate: QSlider = None

        self.lineedit_alpha: QLineEdit = None
        self.lineedit_nv: QLineEdit = None
        self.lineedit_freq_x: QLineEdit = None
        self.lineedit_freq_y: QLineEdit = None

        self.combo_plot_type: QComboBox = None

        self.grid_main: QGridLayout = None
        self.vbox_left: QVBoxLayout = None
        self.vbox_right: QVBoxLayout = None

        self.plot_right_bottom: BAPlot = None
        self.plot_right_middle: BAPlot = None

        self.plot_right_top: AmplitudePlot = None  # Plots amplitude for WT.
        self.plot_main: ColorMeshPlot = None  # Plots WT or bispectrum.

        self.btn_add_point: QPushButton = None
        self.btn_select_point: QPushButton = None
        self.btn_clear_plots: QPushButton = None

        self.listwidget_freq: QListWidget = None
        self.checkbox_plot_surr: QCheckBox = None

        self.radio_power: QRadioButton = None
        self.radio_ampl: QRadioButton = None
