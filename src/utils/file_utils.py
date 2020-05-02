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
import warnings
from os import path
from os.path import join

from utils.os_utils import OS

pymoda_path = None

username = os.environ.get("USERNAME") or os.environ.get("USER")
home = os.path.expanduser("~")

if OS.is_windows():
    pymoda_path = f"C:\\Users\\{username}\\AppData\\Roaming\\PyMODA"
else:
    pymoda_path = f"{home}/.pymoda"

os.makedirs(pymoda_path, exist_ok=True)

log_path = join(pymoda_path, "pymoda.log")
settings_path = join(pymoda_path, "settings.conf")

_whitelist = ["src", "res"]


def get_root_folder() -> str:
    """
    Returns the absolute path to PyMODA's root folder.

    WARNING: This function relies on the fact that the current working directory points to `src/`.
    """
    _, folder = path.split(os.getcwd())
    # if folder not in _whitelist:
    if not any([f in _whitelist for f in os.listdir(os.getcwd())]):
        import inspect

        warnings.warn(
            f"\nWARNING: function '{inspect.currentframe().f_code.co_name}' is attempting to find "
            f"PyMODA's root directory, but the current working directory may not be the root directory."
            f"The current working directory is '{os.getcwd()}'.",
            RuntimeWarning,
        )

    return os.getcwd()
