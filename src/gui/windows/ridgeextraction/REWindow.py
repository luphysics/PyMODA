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
from typing import List, Tuple

from PyQt5 import sip
from PyQt5.QtWidgets import QListWidget, QVBoxLayout, QListWidgetItem

from data import resources
from gui.windows.ridgeextraction.REPlot import REPlot
from gui.windows.ridgeextraction.REPresenter import REPresenter
from gui.windows.ridgeextraction.REView import REView
from gui.windows.timefrequency.TFWindow import TFWindow
from maths.utils import float_or_none


class REWindow(REView, TFWindow):
    """
    The ridge extraction window. Since ridge extraction uses all of
    the time-frequency analysis functionality (except statistics),
    it inherits directly from TFWindow.
    """

    _mark_region_text = "Mark Region"

    def __init__(self, parent):
        self.is_marking_region = False
        self.most_recent_changed_freq = 0
        self.single_plot_mode = True

        super(REWindow, self).__init__(parent, REPresenter(self))

    def init_ui(self):
        super(REWindow, self).init_ui()

        self.setup_btn_mark_region()
        self.setup_btn_add_marked_region()
        self.setup_freq_boxes()
        self.setup_intervals_list()

        self.setup_btn_ridge_extraction()
        self.setup_btn_filter()

        self.main_plot().set_max_crosshair_count(2)
        self.main_plot().add_crosshair_listener(self.on_crosshair_drawn)

        self.get_button_calculate_single().hide()
        self.set_ridge_filter_disabled(True)

    def get_layout_file(self) -> str:
        return resources.get("layout:window_ridge_extraction.ui")

    def on_calculate_stopped(self):
        super(REWindow, self).on_calculate_stopped()
        self.get_button_calculate_single().hide()

    def on_calculate_started(self):
        super(REWindow, self).on_calculate_started()
        self.set_ridge_filter_disabled(True)

    def set_ridge_filter_disabled(self, disabled: bool):
        buttons = (self.get_btn_filter(), self.get_btn_ridge_extraction())
        for btn in buttons:
            btn.setDisabled(disabled)

    def on_freq_region_updated(self, redraw=False):
        freq_tuple = self.get_freq_region()
        self.btn_add_region.setDisabled(None in freq_tuple)

        if redraw:
            self.redraw_lines(*freq_tuple)

    def redraw_lines(self, f1, f2):
        main = self.main_plot()
        main.remove_crosshairs()

        if f1:
            main.draw_crosshair(1, f1)
            main.remove_line_at(1)

        if f2:
            main.draw_crosshair(1, f2)
            main.remove_line_at(1)

        main.update()

    def on_freq_text_edited(self):
        """
        Called when the frequency is edited in the
        interval QLineEdits.

        :param text: the text entered in the QLineEdit
        :param index: the index of the frequency interval: 0 for "Frequency 1",
        1 for "Frequency 2"
        """
        self.on_freq_region_updated(redraw=True)

    def on_crosshair_drawn(self, x: float, y: float):
        """
        Called when a crosshair is drawn on the main plot
        by the user clicking on it.
        """
        formatter = lambda x: f"{x:.6f}"

        f = formatter(y)
        print(f"Selected frequency: {f} Hz")

        f1, f2 = self.get_freq_region()
        formatted = float(f)

        if f1 is None and f2 != formatted:
            self.line_freq1.setText(f)
        elif f1 != formatted:
            self.line_freq2.setText(f)

        f1, f2 = self.get_freq_region()
        if f1:
            self.line_freq1.setText(formatter(f1))
        if f2:
            self.line_freq2.setText(formatter(f2))

        self.on_freq_region_updated()

        # Transform the crosshair into a horizonal line
        # by removing the vertical component.
        self.main_plot().remove_line_at(x=x)

    def on_mark_region_clicked(self):
        self.is_marking_region = not self.is_marking_region

        if self.is_marking_region:
            text = "Cancel"
        else:
            text = self._mark_region_text
            self.on_mark_region_finished()
            self.clear_freq_boxes()

        btn = self.get_btn_mark_region()
        btn.setText(text)

        self.main_plot().set_click_crosshair_enabled(True)
        self.main_plot().set_mouse_zoom_enabled(False)
        self.get_btn_add_region().setDisabled(True)

    def on_mark_region_finished(self):
        plot = self.main_plot()
        plot.set_click_crosshair_enabled(False)
        plot.set_mouse_zoom_enabled(True)

        plot.remove_crosshairs()
        plot.update()

        self.clear_freq_boxes()

    def clear_freq_boxes(self):
        self.line_freq1.setText("")
        self.line_freq2.setText("")

    def on_add_region_clicked(self):
        f1, f2 = sorted(self.get_freq_region())
        self.mark_region(f1, f2)
        self.on_mark_region_finished()

        self.get_btn_mark_region().setText(self._mark_region_text)
        self.is_marking_region = False
        self.get_btn_add_region().setDisabled(True)

    def switch_to_three_plots(self):
        if not self.single_plot_mode:
            return

        layout: QVBoxLayout = self.get_plot_layout()

        self.re_top = REPlot(self)
        self.re_bottom = REPlot(self)

        layout.insertWidget(0, self.re_top)
        layout.addWidget(self.re_bottom)

        self.single_plot_mode = False

    def switch_to_single_plot(self):
        if self.single_plot_mode:
            return

        layout = self.get_plot_layout()
        for plot in (self.re_top, self.re_bottom):
            if plot is not None:
                layout.removeWidget(plot)
                plot.deleteLater()
                sip.delete(plot)

        self.re_top = None
        self.re_bottom = None

        self.single_plot_mode = True

    def get_re_top_plot(self):
        return self.re_top

    def get_re_bottom_plot(self):
        return self.re_bottom

    def get_plot_layout(self):
        return self.plot_layout

    def clear_all(self):
        for plot in (self.re_top, self.re_bottom, self.main_plot()):
            if plot is not None:
                plot.clear()

    def mark_region(self, freq1, freq2):
        l: QListWidget = self.get_intervals_listwidget()
        l.addItem(f"{freq1}, {freq2}")
        l.setCurrentRow(l.count() - 1)

    def get_freq_region(self):
        l1 = self.line_freq1.text()
        l2 = self.line_freq2.text()

        freq = (
            float_or_none(l1),
            float_or_none(l2),
        )
        return freq

    def get_btn_mark_region(self):
        return self.btn_mark_region

    def get_btn_add_region(self):
        return self.btn_add_region

    def get_btn_filter(self):
        return self.btn_filter

    def get_btn_ridge_extraction(self):
        return self.btn_ridges

    def get_intervals_listwidget(self) -> QListWidget:
        """Gets the intervals list widget."""
        return self.list_intervals

    def get_interval_strings(self) -> list:
        """Gets the items from the intervals list widget as strings."""
        w = self.get_intervals_listwidget()
        return [w.item(i).text() for i in range(w.count())]

    def get_interval_tuples(self) -> List[Tuple[float, ...]]:
        """
        Gets a list of tuples with length 2, each representing
        a selected frequency range.
        """
        strings = filter(lambda i: "None" not in i, self.get_interval_strings())
        return [self._get_interval_tuple(s) for s in strings]

    def _get_interval_tuple(self, item: str) -> tuple:
        return tuple([float(i) for i in item.split(",")])

    def get_selected_interval(self):
        l: QListWidget = self.get_intervals_listwidget()
        indices = l.selectedIndexes()

        tuples = self.get_interval_tuples()
        if indices and len(tuples) > indices[0].row():
            return self.get_interval_tuples()[indices[0].row()]
        return None

    def setup_intervals_list(self):
        l: QListWidget = self.get_intervals_listwidget()
        l.itemSelectionChanged.connect(self.on_interval_selected)

    def on_interval_selected(self):
        self.presenter.on_interval_selected(self.get_selected_interval())

    def setup_btn_mark_region(self):
        self.get_btn_mark_region().clicked.connect(self.on_mark_region_clicked)

    def setup_btn_add_marked_region(self):
        btn = self.get_btn_add_region()
        btn.setDisabled(True)
        btn.clicked.connect(self.on_add_region_clicked)

    def setup_freq_boxes(self):
        l1 = self.line_freq1
        l2 = self.line_freq2

        l1.editingFinished.connect(partial(self.on_freq_text_edited))
        l2.editingFinished.connect(partial(self.on_freq_text_edited))

    def setup_btn_ridge_extraction(self):
        self.get_btn_ridge_extraction().clicked.connect(self.presenter.on_ridge_extraction_clicked)

    def setup_btn_filter(self):
        self.get_btn_filter().clicked.connect(self.presenter.on_filter_clicked)
