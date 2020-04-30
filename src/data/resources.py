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
import string

"""
Helper file for getting resources related to the application.
The path to a resource should be accessed by calling the get()
function with the filename prefixed by the resource type and a 
colon. 

For example, get("layout:my_window.ui") or get("img:my_image.png").
"""


def get_program_name() -> str:
    """Returns the name of the program."""
    return "PyMODA"


def path_from_file_string(file_string: str) -> str:
    """
    Returns the file path from a file string which is
    retrieved from a drag-and-drop event.
    """
    if file_string is None:
        raise Exception("No file provided.")

    # In the case of drag-and-drop, get the path from the URI.
    result = file_string.replace("file://", "")
    try:
        if ":" == result[2]:  # This is a Windows path; remove initial forward-slash.
            result = result[1:]
    except IndexError:
        result = ""
    return result


def get(resource: string) -> str:
    """
    Gets the path to a resource. Can be supplied with a relative path from the res/ folder,
    or with a name prefixed with the resource type and a colon.

    The following are all valid:
    >>> get("layout:window_time_freq.ui")
    >>> get("layout/window_time_freq.ui")
    >>> get("data:csv/dual_signal.csv")
    >>> get("data/csv/dual_signal.csv")
    """
    split = resource.split(":")
    if len(split) > 2:
        raise ResourceException(
            f"Error finding resource type for '{resource}'. Wrong number of colon separators."
        )

    res_type = split[0]
    name = split[-1]

    if res_type == "test":
        print("Warning: using deprecated prefix 'test' instead of 'data'.")

    folder = resources_dict.get(res_type) or _get_base_path()
    if not folder:
        raise ResourceException(
            f"Requested resource type '{res_type}' has no associated folder."
        )
    return folder + name


def _get_base_path():
    """Returns the path to the resources folder."""
    return "res/"


def _get_img_path():
    """Returns the path to the image folder."""
    return _get_base_path() + "img/"


def _get_layout_path():
    """Returns the path to the layout folder."""
    return _get_base_path() + "layout/"


def _get_data_path():
    return _get_base_path() + "data/"


def _get_colour_path():
    return _get_base_path() + "colours/"


# Used to select the correct path for a given resource type.
resources_dict = {
    "layout": _get_layout_path(),
    "img": _get_img_path(),
    "image": _get_img_path(),
    "test": _get_data_path(),
    "data": _get_data_path(),
    "colours": _get_colour_path(),
}


class ResourceException(Exception):
    """
    An Exception raised when an error occurs while finding resources.
    """
