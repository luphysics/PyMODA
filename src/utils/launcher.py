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
import os
import subprocess
import sys
from os.path import join

from utils import file_utils
from utils.os_utils import OS


def get_launcher_directory() -> str:
    return file_utils.pymoda_path


def is_launcher_present() -> bool:
    return any(
        [
            name in os.listdir(get_launcher_directory())
            for name in ["launcher", "launcher.exe"]
        ]
    )


def get_launcher_path() -> str:
    folder = get_launcher_directory()

    target = join(folder, _get_launcher_name())

    if os.path.exists(target):
        return target
    else:
        return None


def _get_launcher_name() -> str:
    return "launcher.exe" if OS.is_windows() else "launcher"


def start_via_launcher() -> None:
    target = get_launcher_path()
    if not target:
        return

    subprocess.Popen([target, *sys.argv[1:]])
