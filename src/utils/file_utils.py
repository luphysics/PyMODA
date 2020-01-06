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
from os import path
from pathlib import Path

_whitelist = ["src", "temp"]


def get_root_folder() -> str:
    """
    Returns the absolute path to PyMODA's root folder.

    WARNING: This function relies on the fact that the current working directory points to `src/`.
    """
    _, folder = path.split(os.getcwd())
    if folder not in _whitelist:
        import inspect

        print(
            f"\nWARNING: function '{inspect.currentframe().f_code.co_name}' is attempting to find "
            f"PyMODA's root directory, but the current working directory should be one of: "
            f"{[f'PyMODA/{folder}' for folder in _whitelist]} for this to work correctly.\n"
            f"The current working directory is '{os.getcwd()}'.",
            end="\n\n",
        )

    return Path(os.getcwd()).parent
