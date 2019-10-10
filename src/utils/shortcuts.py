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
import platform
import sys

system = platform.system()


class OS:

    @staticmethod
    def is_windows() -> bool:
        """
        Returns whether the current OS is Windows.
        """
        return system == "Windows"

    @staticmethod
    def is_linux() -> bool:
        """
        Returns whether the current OS is Linux-based.
        """
        return system == "Linux"

    @staticmethod
    def is_mac_os() -> bool:
        """
        Returns whether the current OS is macOS (hopefully).
        """
        return not (OS.is_linux() or OS.is_windows())  # TODO: Improve implementation.


def create_shortcut() -> str:
    """
    Creates a shortcut to launch PyMODA with current arguments. Can be called on any
    operating system.
    """
    if OS.is_windows():
        status = _create_shortcut_windows()
    elif OS.is_linux():
        status = _create_shortcut_linux()
    elif OS.is_mac_os():
        status = _create_shortcut_mac_os()
    else:
        status = "Operating system unknown. Could not create shortcut."

    return status


def _create_shortcut_windows() -> str:
    """
    Creates a desktop shortcut on Windows, which launches PyMODA with the
    current arguments.
    """
    import os
    import winshell

    path = os.path.join(winshell.desktop(), "PyMODA.lnk")
    with winshell.shortcut(path) as s:
        # Path to Python interpreter.
        s.path = sys.executable
        s.description = "Shortcut to launch PyMODA."
        s.arguments = _python_interpreter_arguments()

    return "Created desktop shortcut for PyMODA with current arguments."


def _create_shortcut_linux() -> str:
    """
    Creates a command-line alias to launch PyMODA with current arguments,
    by adding it to ~/.profile.
    """
    with open(_get_profile_abs_path(), "r") as f:
        lines = f.readlines()

    alias_pymoda = "alias pymoda="
    lines = list(filter(lambda l: alias_pymoda not in l, lines))

    lines.append(f"{alias_pymoda}'{sys.executable} {_python_interpreter_arguments()}'")
    with open(_get_profile_abs_path(), "w") as f:
        f.writelines(lines)

    return "Created 'pymoda' alias to launch PyMODA with current arguments. " \
           "Open a new terminal in any folder and try typing 'pymoda'."


def _create_shortcut_mac_os() -> str:
    return "macOS shortcuts are not supported yet."


def _get_profile_abs_path() -> str:
    """
    Returns the absolute path to the `.profile` file on Linux.
    """
    from pathlib import Path
    home = str(Path.home())
    return os.path.join(home, ".profile")


def _python_interpreter_arguments() -> str:
    """
    Returns the path to the main Python file plus all current arguments.
    """
    return " ".join([_abs_path_to_main_py()] + sys.argv[1:])


def _abs_path_to_main_py() -> str:
    """
    Returns the absolute path to the main Python file, `main.py`.
    """
    return os.path.abspath(sys.argv[0])
