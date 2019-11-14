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

from PyQt5.QtWidgets import QVBoxLayout, QProgressBar, QLabel, QWidget

import updater.update as upd
from gui.windows.CentredWindow import CentredWindow
from updater.DownloadThread import temp_filename


class UpdateWindow(CentredWindow):
    """
    Window which displays progress and status when updating PyMODA.
    """

    def __init__(self, app):
        super().__init__(app)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.label = QLabel("Downloading...")
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        from updater.DownloadThread import DownloadThread

        self.thread = DownloadThread(self)
        self.thread.progress_signal.connect(self.on_progress)
        self.thread.finished_signal.connect(self.on_download_finished)
        self.thread.start()

    def on_progress(self, progress: float) -> None:
        self.progress.setValue(progress)

    def on_download_finished(self, success: bool) -> None:
        self.progress.hide()
        if success:
            self.label.setText("Unzipping files...")
            try:
                upd.extract_zip(temp_filename)
            except:
                self.label.setText("Unzip failed. Please try again.")
            else:
                self.start_copy_files()
        else:
            self.label.setText("Download failed. Please try again later.")

    def start_copy_files(self) -> None:
        try:
            self.label.setText("Backing up current version and moving files...")
            upd.copy_files()
        except:
            self.label.setText("Failed to copy files.")
        else:
            self.label.setText("Finished!")
            upd.relaunch_pymoda(success=True)
