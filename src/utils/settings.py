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
from typing import List

from easysettings import EasySettings

_settings = EasySettings("settings.conf")

_key_recent_files = "recent_files"
_key_recent_frequencies = "recent_freq"


def get_recent_files() -> List[str]:
    files = _settings.get(_key_recent_files)
    return files or []


def add_recent_file(new_file: str):
    files = get_recent_files()

    if new_file:
        if new_file in files:
            files.remove(new_file)

        files.insert(0, new_file)

    _settings.set(_key_recent_files, files)
    _settings.save()


def get_recent_freq() -> List[float]:
    freq = _settings.get(_key_recent_frequencies)
    return freq or []


def add_recent_freq(new_freq: float):
    freq = get_recent_freq()

    if new_freq is not None:
        if new_freq in freq:
            freq.remove(new_freq)

        freq.insert(0, new_freq)

    _settings.set(_key_recent_frequencies, freq)
    _settings.save()
