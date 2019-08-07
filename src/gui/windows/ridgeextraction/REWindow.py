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

    def __init__(self, parent):
        self.is_marking_region = False

        super(REWindow, self).__init__(parent)

    def init_ui(self):
        super(REWindow, self).init_ui()

        self.setup_btn_mark_region()
        self.setup_btn_add_marked_region()

    def get_layout_file(self) -> str:
        return resources.get("layout:window_ridge_extraction.ui")

    def on_freq_region_updated(self):
        freq = self.get_freq_region()

    def on_mark_region_clicked(self):
        self.is_marking_region = not self.is_marking_region

        if self.is_marking_region:
            text = "Cancel"
        else:
            text = "Mark Region"

        btn = self.get_btn_mark_region()
        btn.setText(text)

    def on_add_region_clicked(self):
        f1, f2 = self.get_freq_region()
        self.mark_region(f1, f2)
        self.get_btn_add_region().setDisabled(True)

    def mark_region(self, freq1, freq2):
        pass

    def get_freq_region(self):
        l1 = self.line_freq1
        l2 = self.line_freq2

        freq = (
            float_or_none(l1),
            float_or_none(l2),
        )

        if None not in freq:
            return sorted(freq)
        return freq

    def on_add_region(self):
        pass

    def get_btn_mark_region(self):
        return self.btn_mark_region

    def get_btn_add_region(self):
        return self.btn_add_region

    def setup_btn_mark_region(self):
        self.get_btn_mark_region().clicked.connect(self.on_mark_region_clicked)

    def setup_btn_add_marked_region(self):
        btn = self.get_btn_add_region()
        btn.setDisabled(True)
        btn.clicked.connect(self.on_add_region)
