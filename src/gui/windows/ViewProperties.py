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


class ViewProperties:
    """
    A class which should be overridden to declare the variables which
    will be added when the .ui file is inflated to create a window.

    The only purpose of this class is to provide useful code
    completion in the IDE.

    All variables should be initialised as None in the constructor
    and marked with appropriate type annotations.

    Important: The constructor for a ViewProperties class should be called
    before the .ui file is inflated.
    """
