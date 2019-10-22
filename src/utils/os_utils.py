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

import platform

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
        return system == "Darwin"
