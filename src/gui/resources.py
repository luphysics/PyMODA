#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2019  Lancaster University
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


def get_base_path():
    """Returns the path to the resources folder."""
    return "../res/"


def get_img_path():
    """Returns the path to the image folder."""
    return get_base_path() + "img/"


def get_layout_path():
    """Returns the path to the layout folder."""
    return get_base_path() + "layout/"


def get_name():
    """Returns the name of the program."""
    return "PyMODA"


def path_from_file_string(str):
    """
    Returns the file path from a file string which is
    retrieved from a drag-and-drop event.
    """
    return str.replace("file://", "")


def get_ui(name):
    """
    Gets a .ui file from the resources folder. You may
    specify the name with or without the .ui extension.
    """
    extension = ".ui"
    if extension not in name:
        name += extension
    return get_layout_path() + name
