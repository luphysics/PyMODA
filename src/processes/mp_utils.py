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
from typing import Optional

from utils.args import matlab_runtime
from utils.os_utils import OS

"""
Contains functions to help with multiprocessing.
"""


def process(func):
    """
    Decorator which denotes that a function should run in a separate process.
    This decorator ensures that the LD_LIBRARY_PATH for the MATLAB Runtime is
    set correctly for the process when provided as a command-line argument.
    """

    def wrapper(*args, **kwargs):
        setup_matlab_runtime()
        result = func(*args, **kwargs)
        return result

    return wrapper


def setup_matlab_runtime():
    """
    Sets the LD_LIBRARY_PATH variable to the value provided
    in the arguments. Required on Linux, but can be safely called
    on other operating systems.

    Should not be executed in the main process, because this will
    crash PyQt on Linux.
    """
    path = matlab_runtime()
    if path:
        if OS.is_linux():
            os.environ["LD_LIBRARY_PATH"] = path
        elif OS.is_mac_os():
            os.environ["DYLD_LIBRARY_PATH"] = path


def _get_start_method() -> Optional[str]:
    """
    Gets the start method, which depends on the current OS. For Windows and Linux, the
    defaults ('spawn' and 'fork' respectively) are fine.

    For macOS, the default was 'fork' until Python 3.8 but this causes errors:

    "The process has forked and you cannot use this CoreFoundation functionality safely. You MUST exec().
    Breakon__THE_PROCESS_HAS_FORKED_AND_YOU_CANNOT_USE_THIS_COREFOUNDATION_FUNCTIONALITY___YOU_MUST_EXEC__() to debug."

    Therefore, the start method is set to 'spawn' on macOS.
    """
    if OS.is_mac_os():
        return "spawn"

    return None


def set_mp_start_method() -> None:
    """
    Sets the multiprocessing start method.
    """
    start_method = _get_start_method()
    if not start_method:
        return

    import multiprocessing
    import multiprocess

    multiprocessing.set_start_method(start_method)
    multiprocess.set_start_method(start_method)
