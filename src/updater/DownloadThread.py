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
import os
import time
from http.client import HTTPResponse
from urllib.request import urlopen

from PyQt5.QtCore import QThread, pyqtSignal

from updater import update as upd

temp_filename = "pymoda-temp.zip"


class DownloadThread(QThread):
    """
    Thread which handles downloading the new version of PyMODA as a zip file.
    """

    # Signals for displaying progress and success/failure.
    progress_signal = pyqtSignal(object)
    finished_signal = pyqtSignal(bool)

    def __init__(self, window, size):
        super().__init__()
        self.window = window
        self.size = size

    def run(self) -> None:
        """
        Starts the download and emits a signal when it finishes or fails.
        """
        # Pretend to download the file if an environment variable, MOCK_DOWNLOAD, is set.
        if os.environ.get("MOCK_DOWNLOAD") is not None:
            counter = 0
            while counter <= 100:
                self.progress_signal.emit(counter)
                counter += 1
                time.sleep(0.02)

            return self.finished_signal.emit(True)

        try:
            with urlopen(upd.zip_url) as u:
                self.download(u)
        except Exception as e:
            print(f"Exception: {e}")
            self.finished_signal.emit(False)
        else:
            self.finished_signal.emit(True)

    def download(self, response: HTTPResponse) -> None:
        """
        Downloads the zip file and emits progress for the GUI to show.

        :param response: the HTTP response to download the file from
        """
        size = self.size

        if size is not None:
            print(f"Got size from GitHub API: {size} bytes.")
        else:
            size = 10 ** 6 * 44

        with open(temp_filename, "wb") as f:
            downloaded_bytes = 0
            block_size = 1024 * 10

            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break

                f.write(buffer)
                downloaded_bytes += block_size

                self.progress_signal.emit(downloaded_bytes / size * 100)
