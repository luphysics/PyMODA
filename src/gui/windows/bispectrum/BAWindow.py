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
from typing import Optional, Tuple

from PyQt5.QtWidgets import QListWidgetItem

from data import resources
from gui.components.DualSignalComponent import DualSignalComponent
from gui.components.FreqComponent import FreqComponent
from gui.components.SurrogateComponent import SurrogateComponent
from gui.components.VerticalMultiPlotComponent import VerticalMultiPlotComponent
from gui.plotting.plots.AmplitudePlot import AmplitudePlot
from gui.windows.bispectrum.BAPlot import BAPlot
from gui.windows.bispectrum.BAPresenter import BAPresenter
from gui.windows.bispectrum.BAViewProperties import BAViewProperties
from gui.windows.common.BaseTFWindow import BaseTFWindow
from maths.num_utils import float_to_str
from utils.decorators import floaty


class BAWindow(
    BAViewProperties,
    BaseTFWindow,
    DualSignalComponent,
    FreqComponent,
    SurrogateComponent,
    VerticalMultiPlotComponent,
):
    name = "Wavelet Bispectrum Analysis"

    def __init__(self, application):
        BAViewProperties.__init__(self)
        BaseTFWindow.__init__(self, application, BAPresenter(self))

        DualSignalComponent.__init__(self, self.signal_plot())
        FreqComponent.__init__(self, self.line_fmax, self.line_fmin, self.line_res)
        SurrogateComponent.__init__(
            self, self.slider_surrogate, self.line_surrogate, self.checkbox_surr
        )
        VerticalMultiPlotComponent.__init__(self, self.vbox_right)

        self.presenter: BAPresenter = self.presenter
        self.presenter.init()

    def setup_ui(self):
        super(BAWindow, self).setup_ui()
        self.btn_calculate_single.hide()

        self.plot_main.set_mouse_zoom_enabled(False)
        self.plot_main.set_max_crosshair_count(1)
        self.plot_main.add_crosshair_listener(self.on_crosshair_drawn)

        self.btn_select_point.clicked.connect(self.on_select_point_clicked)
        self.btn_add_point.clicked.connect(self.on_add_point_clicked)
        self.btn_clear_plots.clicked.connect(self.on_clear_plots_clicked)

        self.combo_plot_type.currentTextChanged.connect(
            lambda _: self.presenter.update_plots()
        )
        self.listwidget_freq.itemClicked.connect(self.on_freq_selected)

    def on_calculate_started(self):
        super(BAWindow, self).on_calculate_started()
        self.btn_add_point.setEnabled(False)

    def on_calculate_stopped(self):
        super(BAWindow, self).on_calculate_stopped()
        self.btn_add_point.setEnabled(True)

    def on_select_point_clicked(self):
        if not self.is_wt_selected():
            self.plot_main.set_click_crosshair_enabled(True)

    def on_add_point_clicked(self):
        x = self.get_freq_x()
        y = self.get_freq_y()

        if x is not None and y is not None:
            l = self.listwidget_freq
            formatted = f"{float_to_str(x)}, {float_to_str(y)}"

            if formatted not in [l.item(i).text() for i in range(l.count())]:
                l.addItem(formatted)
                l.setCurrentRow(l.count() - 1)

            self.presenter.add_point(x, y)

    def on_clear_plots_clicked(self):
        pass

    def switch_to_triple_plot(self):
        self.plot_right_middle = BAPlot(self)
        self.plot_right_bottom = BAPlot(self)

        self.vplot_remove_all_plots()
        self.vplot_add_plots(self.plot_right_middle, self.plot_right_bottom)

        self.plot_right_top = None

    def switch_to_dual_plot(self):
        self.plot_right_top = AmplitudePlot(self)

        self.vplot_remove_all_plots()
        self.vplot_add_plots(self.plot_right_top)

        self.plot_right_middle = None
        self.plot_right_bottom = None

    def on_crosshair_drawn(self, x: float, y: float):
        x = float_to_str(x)
        y = float_to_str(y)

        self.lineedit_freq_x.setText(x)
        self.lineedit_freq_y.setText(y)

    def is_wt_selected(self):
        return "Wavelet transform" in self.combo_plot_type.currentText()

    def is_amplitude_selected(self):
        pass  # TODO: add checkbox for ampl/power and implement

    def switch_to_all_plots(self):
        pass

    def on_freq_selected(self, _: QListWidgetItem):
        self.presenter.update_plots()

    def get_layout_file(self) -> str:
        return resources.get("layout:window_bispectrum_analysis.ui")

    def get_plot_type(self) -> str:
        return self.combo_plot_type.currentText()

    def get_selected_freq_pair(self) -> Tuple[float, float]:
        items = self.listwidget_freq.selectedItems()
        if items:
            str_freq_x, str_freq_y = items[-1].text().split(", ")
            return float(str_freq_x), float(str_freq_y)

        return None, None

    @floaty
    def get_freq_x(self) -> Optional[int]:
        return self.lineedit_freq_x.text()

    @floaty
    def get_freq_y(self) -> Optional[int]:
        return self.lineedit_freq_y.text()

    @floaty
    def get_nv(self) -> Optional[float]:
        return self.lineedit_nv.text()

    @floaty
    def get_alpha(self) -> Optional[float]:
        return self.lineedit_alpha.text()
