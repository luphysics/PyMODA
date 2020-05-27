#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2020 Lancaster University
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
import os
import shutil
import time
from os.path import join

from PyQt5.QtCore import QThread

from utils import launcher, shortcuts


class CleanupThread(QThread):
    """
    Thread which deletes old installations of PyMODA.
    """

    def run(self) -> None:
        time.sleep(5)
        launcher_dir = launcher.get_launcher_directory()

        import re

        pattern = "v[0-9].[0-9].[0-9]"
        versions = filter(lambda i: re.match(pattern, i), os.listdir(launcher_dir))

        versions = sorted(list(versions))
        logging.info(f"Currently installed versions: {versions}.")

        if len(versions) > 1:
            to_delete = versions[:-1]

            import main

            if main.__version__ in to_delete:
                logging.error(
                    f"Cannot delete version {main.__version__}; it is the current version."
                )
                return

            for v in to_delete:
                logging.info(f"Deleting old version: {v}")
                path = join(launcher_dir, v)
                shutil.rmtree(path)

            # Fix issue where shortcut linked to an older version breaks because older version is deleted.
            shortcuts.create_shortcut()
