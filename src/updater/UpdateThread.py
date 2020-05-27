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
import logging

from PyQt5.QtCore import QThread, pyqtSignal

from updater import Updater
from utils import launcher

temp_filename = "pymoda-temp.zip"


class UpdateThread(QThread):
    """
    Thread which handles updating PyMODA.
    """

    # Signals for displaying progress and success/failure.
    download_progress_signal = pyqtSignal(float)
    downloading_signal = pyqtSignal(bool)
    extracting_signal = pyqtSignal(bool)
    copy_finished_signal = pyqtSignal(bool)
    error_signal = pyqtSignal(bool)

    release_tag = None

    def __init__(self):
        super().__init__()

        self.updater = None

    def run(self) -> None:
        try:
            self.do_update()
        except Exception as e:
            logging.error(e)
            self.error_signal.emit(True)

    def do_update(self) -> None:
        logging.info("Update thread has started.")
        if not self.release_tag:
            return logging.error("No release tag.")

        self.updater = Updater.get_instance(
            self.release_tag, self.download_progress_signal
        )

        if self.updater.is_version_present():
            return logging.warning(
                f"Version {self.release_tag} is already installed. Aborting..."
            )

        # Download launcher if not present.
        if not launcher.is_launcher_present():
            logging.info("Downloading launcher...")
            self.updater.download_launcher()
            logging.info("Launcher downloaded.")

        logging.info("Downloading archive...")
        self.downloading_signal.emit(True)
        self.updater.download_archive(self.release_tag)

        logging.info("Extracting archive...")
        self.extracting_signal.emit(True)
        self.updater.extract_archive()

        logging.info("Moving files from extracted archive...")
        self.updater.move_files()
        self.updater.finish()

        self.copy_finished_signal.emit(True)
        logging.info("Update process complete.")
