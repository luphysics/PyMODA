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
import sys
import traceback
from typing import Optional

from utils import log_utils
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
        setup_matlab_runtime()  # TODO: remove, since PyMODAlib handles it? May require adding new environment variable to PyMODAlib.

        return func(*args, **kwargs)

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


def monkeypatch_processes() -> None:
    """
    Monkey-patches the Process class to ensure that processes call `sys.excepthook`.

    Without calling this function, it is not possible for processes to log Exceptions.
    """
    from multiprocessing import Process as P1
    from multiprocess.context import Process as P2

    for Process in (P1, P2):
        Process.__run = Process.run
        Process.run = __patched_run


def __patched_run(self):
    try:
        self.__run()
    except Exception as e:
        if OS.is_windows():
            sys.excepthook(*sys.exc_info())
        else:
            # For some reason, `sys.excepthook` doesn't work in processes on *nix (even after monkey-patching)
            # so we'll write the logs manually.
            tb = "".join(traceback.format_tb(e.__traceback__))
            msg = f"\n{type(e)}\n{tb}{e}"

            log_utils.process_write_log(msg)
            raise e
