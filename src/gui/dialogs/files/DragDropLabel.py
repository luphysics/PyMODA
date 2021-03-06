#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2019  Lancaster University
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
from typing import Callable

from PyQt5 import QtGui
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import QLabel


class DragDropLabel(QLabel):
    """
    A label which accepts drag-and-drop events for files. When a drop
    succeeds, the filename is shown in the label. The label changes
    colour while a drag event is in progress.
    """

    def __init__(self, parent):
        self.drop_callback: Callable = None
        super().__init__(parent)

    def dropEvent(self, event: QDropEvent) -> None:
        """Called when a drop event occurs."""
        file_path = event.mimeData().text().rstrip()
        if self.drop_callback:
            self.drop_callback(file_path)

        self.show_selected_file(file_path)

    def show_selected_file(self, file_path) -> None:
        file_name = file_path.split("/")[-1].split("\\")[-1]
        self.setText(f"File selected:\n{file_name}")
        self.set_background(highlighted=False)

    def dragLeaveEvent(self, e: QtGui.QDragLeaveEvent) -> None:
        self.set_background(highlighted=False)

    def set_background(self, highlighted: bool) -> None:
        background = "grey" if highlighted else "transparent"
        self.setStyleSheet(
            f"QLabel {{ background-color : {background}; color : black; }}"
        )

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        """Called when a drag event enters the label."""
        if event.mimeData().hasText():
            event.accept()
            self.set_background(highlighted=True)
        else:
            event.ignore()

    def set_drop_callback(self, callback: Callable[[str], None]) -> None:
        """Sets a callback for when the drop is complete."""
        self.drop_callback = callback
