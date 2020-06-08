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
from functools import partial
from typing import Tuple, Optional

from PyQt5 import sip
from PyQt5.QtWidgets import QListWidgetItem, QListWidget

from data import resources
from gui.components.DualSignalComponent import DualSignalComponent
from gui.components.SurrogateComponent import SurrogateComponent
from gui.windows.bayesian.DBPresenter import DBPresenter
from gui.windows.bayesian.DBViewProperties import DBViewProperties
from gui.windows.bayesian.ParamSet import ParamSet
from gui.windows.common.BaseTFWindow import BaseTFWindow
from maths.num_utils import float_to_str
from utils.decorators import floaty, inty


class DBWindow(DBViewProperties, BaseTFWindow, SurrogateComponent, DualSignalComponent):
    name = "Dynamical Bayesian Inference"

    def __init__(self, application):
        DBViewProperties.__init__(self)
        BaseTFWindow.__init__(self, application, DBPresenter(self))

        SurrogateComponent.__init__(
            self, self.slider_surrogate, self.line_surrogate, self.checkbox_surr
        )
        DualSignalComponent.__init__(self, self.signal_plot())

        self.presenter: DBPresenter = self.presenter
        self.presenter.init()

        self.is_triple_plot = False
        self.on_toggle_plots()

    def get_layout_file(self) -> str:
        return resources.get("layout:window_dynamical_bayesian.ui")

    def setup_ui(self):
        super().setup_ui()

        self.btn_calculate_single.hide()
        self.btn_add_paramset.clicked.connect(self.on_add_paramset_clicked)
        self.btn_delete_paramset.clicked.connect(self.on_delete_paramset_clicked)
        self.btn_toggle_plots.clicked.connect(self.on_toggle_plots)

        self.listwidget_freq_band1.itemClicked.connect(
            partial(self.on_paramset_selected, 0)
        )
        self.listwidget_freq_band2.itemClicked.connect(
            partial(self.on_paramset_selected, 1)
        )

        self.slider_time.valueChanged.connect(self.presenter.on_time_slider_changed)
        self.checkbox_mean.toggled.connect(self.on_mean_toggled)
        self.on_mean_toggled()

    def on_toggle_plots(self) -> None:
        """
        The view either displays a 3-plot layout or a 2-plot-layout; this function
         is called when the user toggles between them.
        """
        triple_plot = (self.db_plot_top, self.db_plot_middle, self.db_plot_bottom)
        dual_plot = (self.db3d_grpbox_left, self.db3d_grpbox_right)

        if self.is_triple_plot:
            self.set_visible(triple_plot, False)
            self.set_visible(dual_plot, True)
            self.vbox_all_plots.setStretch(1, 0)
            self.vbox_all_plots.setStretch(2, 7)

        else:
            self.set_visible(triple_plot, True)
            self.set_visible(dual_plot, False)
            self.vbox_all_plots.setStretch(1, 7)
            self.vbox_all_plots.setStretch(2, 0)

        self.is_triple_plot = not self.is_triple_plot
        self.presenter.plot_bayesian()

    def set_visible(self, items, visible: bool) -> None:
        """
        Used to set a list of widgets as visible, or not visible. This is useful
         to set the visiblity of the 3-plot and 2-plot layouts.

        :param items: the widgets to set the visibility of
        :param visible: whether visible, or invisible
        """
        for i in items:
            if visible:
                i.show()
            else:
                i.hide()

    def on_mean_toggled(self):
        self.groupbox_slider.setEnabled(not self.checkbox_mean.isChecked())

        try:
            self.presenter.plot_bayesian()
        except:
            pass

    def on_calculate_started(self):
        super(DBWindow, self).on_calculate_started()
        for p in (self.db_plot_top, self.db_plot_middle, self.db_plot_bottom):
            p.clear()

    def on_calculate_stopped(self):
        super(DBWindow, self).on_calculate_stopped()
        self.btn_calculate_single.hide()
        self.btn_calculate_all.setText("Calculate")

    def get_param_set(self) -> ParamSet:
        """
        Creates a parameter set from the current UI elements. This is used when
        adding a parameter set to the list.
        """
        return ParamSet(
            self.get_freq_range1(),
            self.get_freq_range2(),
            self.get_window_size(),
            self.get_propagation_const(),
            self.get_surr_count(),
            self.get_overlap(),
            self.get_order(),
            self.get_confidence_level(),
        )

    def on_paramset_selected(self, widget_index: int, _: QListWidgetItem) -> None:
        """
        Called when a parameter set is selected in the lists.
        :param widget_index: the index of the list widget that was used (there
         are two list widgets, so this is 0 or 1)
        :param _: (unused) the widget item which was selected
        """
        list_widgets: Tuple[QListWidget, QListWidget] = (
            self.listwidget_freq_band1,
            self.listwidget_freq_band2,
        )

        item_index = list_widgets[widget_index].selectedIndexes()[-1].row()

        # Sets other list widget to have same selection.
        #
        # Since widget_index is always 0 or 1, `not widget_index`
        # can be used to get the other list widget.
        list_widgets[not widget_index].setCurrentRow(item_index)

        text1 = list_widgets[0].selectedItems()[-1].text()
        text2 = list_widgets[1].selectedItems()[-1].text()

        self.fill_paramset_ui(text1, text2)

    def fill_paramset_ui(self, text1, text2) -> None:
        """
        Fills the UI with the values from a parameter set.
        :param text1: the text representation of the first param set
        :param text2: the text representation of the second param set
        """
        params = self.presenter.get_paramset(text1, text2)

        if params:
            self.lineedit_overlap.setText(float_to_str(params.overlap))
            self.lineedit_window_size.setText(float_to_str(params.window))
            self.lineedit_confidence_level.setText(
                float_to_str(params.confidence_level)
            )
            self.lineedit_propagation_const.setText(
                float_to_str(params.propagation_const)
            )
            self.lineedit_order.setText(float_to_str(params.order))

    def on_add_paramset_clicked(self) -> None:
        """
        Called when the user clicks the "add parameter set" button.
        """
        params = self.get_param_set()
        band1, band2 = params.to_string()

        if not self.presenter.has_paramset(band1, band2):
            self.listwidget_freq_band1.addItem(band1)
            self.listwidget_freq_band2.addItem(band2)

            lastIndex = self.listwidget_freq_band1.count() - 1
            self.listwidget_freq_band1.setCurrentRow(lastIndex)
            self.listwidget_freq_band2.setCurrentRow(lastIndex)

            self.presenter.add_paramset(params)

    def on_delete_paramset_clicked(self):
        """
        Called when the user clicks the "Delete parameter set" button.
        """
        try:
            item1 = self.listwidget_freq_band1.selectedItems()[-1]
            item2 = self.listwidget_freq_band2.selectedItems()[-1]
        except IndexError:
            return

        self.presenter.delete_paramset(item1.text(), item2.text())

        self.listwidget_freq_band1.removeItemWidget(item1)
        self.listwidget_freq_band2.removeItemWidget(item2)

        for i in (item1, item2):
            sip.delete(i)

    def setup_radio_preproc(self):
        pass

    def setup_radio_plot(self):
        pass

    def setup_lineedit_fmin(self):
        pass

    def setup_lineedit_fmax(self):
        pass

    def setup_lineedit_res(self):
        pass

    @inty
    def get_time_slider_value(self) -> Optional[int]:
        return self.slider_time.value()

    @floaty
    def get_freq_range1(self) -> Optional[Tuple[float, float]]:
        return (
            self.lineedit_freq_range1_min.text(),
            self.lineedit_freq_range1_max.text(),
        )

    @floaty
    def get_freq_range2(self) -> Optional[Tuple[float, float]]:
        return (
            self.lineedit_freq_range2_min.text(),
            self.lineedit_freq_range2_max.text(),
        )

    @floaty
    def get_window_size(self) -> Optional[float]:
        return self.lineedit_window_size.text()

    @floaty
    def get_propagation_const(self) -> Optional[float]:
        return self.lineedit_propagation_const.text()

    @floaty
    def get_overlap(self) -> Optional[float]:
        return self.lineedit_overlap.text()

    @floaty
    def get_confidence_level(self) -> Optional[float]:
        return self.lineedit_confidence_level.text()

    @inty
    def get_order(self) -> Optional[int]:
        return self.lineedit_order.text()
