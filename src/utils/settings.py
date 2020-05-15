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
import os
import time
from typing import List, Dict, Optional

from easysettings import EasySettings

from updater.check import is_version_newer
from utils import file_utils

_key_recent_files = "recent_files"
_key_recent_frequencies = "recent_freq"
_key_runtime_warning = "runtime_warning"
_key_latest_commit = "latest_commit"
_key_update_available = "update_available"
_key_last_update_check = "last_update_check"
_key_update_source = "update_source"
_key_save_dir = "save_directory"
_key_pymodalib_cache = "pymodalib_cache"
_key_updating = "updating"
_key_version = "pymoda_version"
_key_directory = "last_opened_directory"


class Settings:
    """
    Class which handles saving values to a preferences file.
    """

    def __init__(self):
        filepath = file_utils.settings_path

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

    def get_latest_commits(self) -> Optional[Dict]:
        """
        :returns a dictionary containing the latest commit hash for each branch.
        """
        out = self._settings.get(_key_latest_commit, None)
        branch = self.get_update_branch()

        # In older versions, this is a string rather than a dict.
        if isinstance(out, str):
            out = {branch: out}

        return out or {}

    def get_latest_commit_on_branch(self) -> Optional[str]:
        """
        :returns the latest commit on the branch which is selected as the update source.
        """
        return self.get_latest_commits().get(self.get_update_branch())

    def set_latest_commit(self, latest_commit: str) -> None:
        """
        Sets the latest commit hash for the current update branch.

        :param latest_commit: the latest commit hash
        """
        commits = self.get_latest_commits()
        commits[self.get_update_branch()] = latest_commit

        self._settings.set(_key_latest_commit, latest_commit)
        self._settings.save()

    def set_update_available(self, value: bool) -> None:
        available: Dict = self.get_update_available()
        available[self.get_update_branch()] = value

        self._settings.set(_key_update_available, available)
        self._settings.save()

    def get_update_available_on_branch(self) -> bool:
        return self.get_update_available().get(self.get_update_branch())

    def get_update_available(self) -> Optional[Dict]:
        out = self._settings.get(_key_update_available, False)
        branch = self.get_update_branch()

        if isinstance(out, bool):
            out = {branch: out}

        return out

    def should_check_updates(self) -> bool:
        return time.time() - self._settings.get(_key_last_update_check, 0.0) > 3600 * 6

    def get_last_update_check(self) -> float:
        return self._settings.get(_key_last_update_check, 0)

    def set_last_update_check(self, time: float) -> None:
        self._settings.set(_key_last_update_check, time)
        self._settings.save()

    def set_update_source(self, branch: str) -> None:
        self._settings.set(_key_update_source, branch)
        self._settings.save()

    def get_update_branch(self) -> str:
        return self._settings.get(_key_update_source, "release").lower()

    def get_save_directory(self) -> str:
        return self._settings.get(_key_save_dir, os.getcwd())

    def set_save_directory(self, save_dir: str) -> None:
        self._settings.set(_key_save_dir, save_dir)
        self._settings.save()

    def get_pymodalib_cache(self) -> Optional[str]:
        return self._settings.get(_key_pymodalib_cache, None)

    def set_pymodalib_cache(self, location: str) -> None:
        self._settings.set(_key_pymodalib_cache, location)
        self._settings.save()
        self._settings.reload_file()

    def set_update_in_progress(self, updating: bool) -> None:
        self._settings.set(_key_updating, updating)
        self._settings.save()

    def get_update_in_progress(self) -> bool:
        return self._settings.get(_key_updating, False)

    def get_pymoda_version(self) -> str:
        return self._settings.get(_key_version, None)

    def set_pymoda_version(self, version: str) -> None:
        current = self._settings.get(_key_version)

        if not current or is_version_newer(new=version, old=current):
            self._settings.set(_key_version, version)
            self._settings.save()
        else:
            logging.error(
                f"Trying to set PyMODA version to {version}, but the current value is {current}"
            )

    def set_last_opened_directory(self, directory: str) -> None:
        self._settings.set(_key_directory, directory)
        self._settings.save()

    def get_last_opened_directory(self) -> str:
        return self._settings.get(_key_directory, None)
