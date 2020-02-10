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
import time
from os import path
from typing import List, Optional

from easysettings import EasySettings

from utils.file_utils import get_root_folder

_key_recent_files = "recent_files"
_key_recent_frequencies = "recent_freq"
_key_runtime_warning = "runtime_warning"
_key_latest_commit = "latest_commit"
_key_update_available = "update_available"
_key_last_update_check = "last_update_check"


class Settings:
    """
    Class which handles saving values to a preferences file.
    """

    def __init__(self):
        location = get_root_folder()
        filepath = path.join(location, "settings.conf")

        self._settings = EasySettings(filepath)

    def get_recent_files(self) -> List[str]:
        files = self._settings.get(_key_recent_files)

        if files and isinstance(files, str):
            return []

        return files or []

    def add_recent_file(self, new_file: str):
        files = self.get_recent_files()

        if new_file:
            if new_file in files:
                files.remove(new_file)

            files.insert(0, new_file)

        self._settings.set(_key_recent_files, files)
        self._settings.save()

    def get_recent_freq(self) -> List[float]:
        freq = self._settings.get(_key_recent_frequencies)
        return freq or []

    def add_recent_freq(self, new_freq: float):
        freq = self.get_recent_freq()

        if new_freq is not None:
            if new_freq in freq:
                freq.remove(new_freq)

            freq.insert(0, new_freq)

        self._settings.set(_key_recent_frequencies, freq)
        self._settings.save()

    def is_runtime_warning_enabled(self) -> bool:
        return self._settings.get(_key_runtime_warning, True)

    def set_runtime_warning_enabled(self, enabled: bool) -> None:
        self._settings.set(_key_runtime_warning, enabled)
        self._settings.save()

    def get_latest_commit(self) -> Optional[str]:
        return self._settings.get(_key_latest_commit, None)

    def set_latest_commit(self, latest_commit: str) -> None:
        self._settings.set(_key_latest_commit, latest_commit)
        self._settings.save()

    def set_update_available(self, value: bool) -> None:
        self._settings.set(_key_update_available, value)
        self._settings.save()

    def get_update_available(self) -> bool:
        return self._settings.get(_key_update_available, False)

    def should_check_updates(self) -> bool:
        return time.time() - self._settings.get(_key_last_update_check, 0.0) > 3600 * 6

    def set_last_update_check(self, time: float) -> None:
        self._settings.set(_key_last_update_check, time)
        self._settings.save()
