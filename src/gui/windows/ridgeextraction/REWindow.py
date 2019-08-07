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

from PyQt5.QtWidgets import QListWidget

from data import resources
from gui.windows.ridgeextraction.REView import REView
from gui.windows.timefrequency.TFWindow import TFWindow
from maths.utils import float_or_none


class REWindow(REView, TFWindow):
    """
    The ridge extraction window. Since ridge extraction uses all of
    the time-frequency analysis functionality (except statistics),
    it inherits from TFWindow.
    """

    _mark_region_text = "Mark Region"

    def __init__(self, parent):
        self.is_marking_region = False
        self.most_recent_changed_freq = 0

        super(REWindow, self).__init__(parent)

    def init_ui(self):
        super(REWindow, self).init_ui()

        self.setup_btn_mark_region()
        self.setup_btn_add_marked_region()
        self.setup_freq_boxes()

        self.main_plot().set_max_crosshair_count(2)
        self.main_plot().add_crosshair_listener(self.on_crosshair_drawn)

    def get_layout_file(self) -> str:
        return resources.get("layout:window_ridge_extraction.ui")

    def on_freq_region_updated(self):
        freq_tuple = self.get_freq_region()

        if None not in freq_tuple:
            self.get_btn_add_region().setDisabled(False)

    def on_freq_text_edited(self, text, line_edit):
        freq = float_or_none(text.text())

        if freq is not None:
            print("Changing value manually has not been implemented yet.")

    def on_crosshair_drawn(self, x: float, y: float):
        print(f"Selected frequency: {y} Hz")
        f = f"{y:.6f}"

        f1, f2 = self.get_freq_region()
        if f1 is None:
            self.line_freq1.setText(f)
        else:
            self.line_freq2.setText(f)

        self.on_freq_region_updated()

        # Transform the crosshair into a horizonal line
        # by removing the vertical part.
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
        f1, f2 = self.get_freq_region()
        self.mark_region(f1, f2)
        self.on_mark_region_finished()

        self.get_btn_mark_region().setText(self._mark_region_text)

    def mark_region(self, freq1, freq2):
        l = self.get_intervals_list()
        l.addItem(f"{freq1}, {freq2}")

    def get_freq_region(self):
        l1 = self.line_freq1.text()
        l2 = self.line_freq2.text()

        freq = (
            float_or_none(l1),
            float_or_none(l2),
        )

        if None not in freq:
            return sorted(freq)
        return freq

    def get_btn_mark_region(self):
        return self.btn_mark_region

    def get_btn_add_region(self):
        return self.btn_add_region

    def get_intervals_list(self) -> QListWidget:
        return self.list_intervals

    def setup_btn_mark_region(self):
        self.get_btn_mark_region().clicked.connect(self.on_mark_region_clicked)

    def setup_btn_add_marked_region(self):
        btn = self.get_btn_add_region()
        btn.setDisabled(True)
        btn.clicked.connect(self.on_add_region_clicked)

    def setup_freq_boxes(self):
        l1 = self.line_freq1
        l2 = self.line_freq2

        l1.textEdited.connect(partial(self.on_freq_text_edited, l1))
        l2.textEdited.connect(partial(self.on_freq_text_edited, l2))
