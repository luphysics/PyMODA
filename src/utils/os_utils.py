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

system = platform.system()

# Variables used to test functionality from different operating systems.
override_windows = "MOCKOS_WINDOWS" in os.environ
override_linux = "MOCKOS_LINUX" in os.environ
override_macos = "MOCKOS_MACOS" in os.environ


class OS:
    @staticmethod
    def is_windows() -> bool:
        """
        Returns whether the current OS is Windows.
        """
        return override_windows or (
            system == "Windows" and not override_macos and not override_linux
        )

    @staticmethod
    def is_linux() -> bool:
        """
        Returns whether the current OS is Linux-based.
        """
        return override_linux or (
            system == "Linux" and not override_macos and not override_windows
        )

    @staticmethod
    def is_mac_os() -> bool:
        """
        Returns whether the current OS is macOS (hopefully).
        """
        return override_macos or (
            system == "Darwin" and not override_linux and not override_windows
        )
