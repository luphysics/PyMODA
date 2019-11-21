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
import asyncio

from PyQt5 import QtGui
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QVBoxLayout, QProgressBar, QLabel, QWidget, QPushButton

import updater.update as upd
from gui.windows.CentredWindow import CentredWindow


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

        self.label: QLabel = QLabel("Downloading...")
        layout.addWidget(self.label)

        self.progress: QProgressBar = QProgressBar()
        layout.addWidget(self.progress)

        self.btn_cancel: QPushButton = QPushButton("Cancel")
        layout.addWidget(self.btn_cancel)

        self.btn_cancel.clicked.connect(self.on_cancel_clicked)
        self.can_cancel = True

        self.btn_close: QPushButton = QPushButton("Close")
        layout.addWidget(self.btn_close)

        self.btn_close.clicked.connect(self.on_close_clicked)
        self.btn_close.hide()

        self.btn_continue: QPushButton = QPushButton("Continue")
        layout.addWidget(self.btn_continue)

        self.btn_continue.hide()
        self.btn_continue.clicked.connect(self.on_continue_clicked)

        self.thread: QThread = None
        asyncio.ensure_future(self.start_update())

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Overrides closeEvent to prevent the window from being closed by the user
        while the installation is in progress.
        """
        event.ignore()

    def on_cancel_clicked(self) -> None:
        """
        Called when the cancel button is clicked.
        """
        if self.can_cancel:
            self.thread.quit()
            upd.relaunch_pymoda(success=False)

    def on_close_clicked(self) -> None:
        """
        Called when the close button is clicked. The close button only appears
        when the update has failed.
        """
        self.thread.quit()
        upd.relaunch_pymoda(success=False)

    def on_continue_clicked(self) -> None:
        """
        Called when the continue button is clicked. The continue button only appears
        when the update has been successful and packages are about to be updated.
        """
        upd.update_packages(success=True)

    def on_failed(self) -> None:
        """
        Called when the update fails. Shows the button to close the dialog.
        """
        self.btn_close.show()
        self.btn_cancel.hide()
        self.progress.hide()

    async def start_update(self) -> None:
        """
        Gets the size of the repository from the GitHub API,
        then starts the update thread.
        """
        from updater.UpdateThread import UpdateThread

        size = await upd.get_repo_size()
        print(f"Got size from GitHub API: {size} bytes.")

        self.thread = UpdateThread(self, size)

        self.thread.download_progress_signal.connect(self.on_progress)
        self.thread.download_finished_signal.connect(self.on_download_finished)

        self.thread.extract_finished_signal.connect(self.on_extract_finished)
        self.thread.copy_finished_signal.connect(self.on_copy_finished)

        self.thread.start()

    def on_progress(self, progress: float) -> None:
        """
        Called to update the progress bar with the download progress.
        :param progress: the progress, as a percentage
        """
        self.progress.setValue(progress)

    def on_download_finished(self, success: bool) -> None:
        """
        Called when download the zip file has finished.

        :param success: whether it was successful
        """
        if not success:
            self.label.setText("Download failed. Please try again later.")
            return self.on_failed()

        self.can_cancel = False

        self.btn_cancel.hide()
        self.progress.setRange(0, 0)

        self.label.setText("Unzipping files...")

    def on_extract_finished(self, success: bool) -> None:
        """
        Called when extracting the zip file has finished.

        :param success: whether it was successful
        """
        if not success:
            self.label.setText("Unzip failed. Please try again later.")
            return self.on_failed()

        self.label.setText("Backing up and overwriting files...")

    def on_copy_finished(self, success: bool) -> None:
        """
        Called when overwriting the old PyMODA with the new version has finished.

        :param success: whether it was successful
        """
        if not success:
            self.label.setText("Failed to copy files.")
            return self.on_failed()

        self.progress.hide()
        self.btn_continue.show()

        self.label.setText(
            "The installer window will close while packages are updated.\n"
            "PyMODA will automatically relaunch once the process is complete.\n\n"
            "This may take over a minute."
        )
