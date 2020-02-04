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
import os
from urllib.request import urlopen

from PyQt5.QtCore import QThread, pyqtSignal

from updater import update as upd
from updater.download import _chunked_download, _mock_download

temp_filename = "pymoda-temp.zip"


class UpdateThread(QThread):
    """
    Thread which handles updating PyMODA.
    """

    # Signals for displaying progress and success/failure.
    download_progress_signal = pyqtSignal(float)
    download_finished_signal = pyqtSignal(bool)
    extract_finished_signal = pyqtSignal(bool)
    copy_finished_signal = pyqtSignal(bool)

    def __init__(self, window, size):
        super().__init__()
        self.window = window
        self.size = size

    def run(self) -> None:
        """
        Updates PyMODA.
        """
        # Download the zip file.
        success = self.download_zip()
        self.download_finished_signal.emit(success)

        if not success:
            return

        # Extract the zip file.
        success = self.extract_zip()
        self.extract_finished_signal.emit(success)

        if not success:
            return

        # Overwrite the old version with the new version.
        success = self.copy_files()
        self.copy_finished_signal.emit(success)

    def download_zip(self) -> bool:
        """
        Downloads the zip file containing the new version of PyMODA.

        :return: whether the function completed successfully
        """
        # Pretend to download the file if an environment variable, MOCK_DOWNLOAD, is set.
        if os.environ.get("MOCK_DOWNLOAD") is not None:
            _mock_download(self.download_progress_signal)
            return True

        try:
            print(f"Downloading new version of PyMODA from {upd.zip_url}...")
            with urlopen(upd.zip_url) as response:
                _chunked_download(
                    temp_filename, response, self.size, self.download_progress_signal
                )

            success = True
        except Exception as e:
            print(e)
            success = False

        return success

    @staticmethod
    def extract_zip() -> bool:
        """
        Extracts the zip file containing the new version of PyMODA.

        :return: whether the function completed successfully
        """
        try:
            upd.extract_zip(temp_filename)
            success = True
        except Exception as e:
            print(e)
            success = False

        return success

    @staticmethod
    def copy_files() -> bool:
        """
        Overwrites the old version of PyMODA with the new version.

        :return: whether the function completed successfully
        """
        try:
            upd.copy_files()
            success = True
        except Exception as e:
            print(e)
            success = False

        return success
