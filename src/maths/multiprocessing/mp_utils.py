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

import psutil as psutil
from multiprocess import Process
from multiprocess.process import current_process

from utils.args import matlab_runtime

"""
Contains functions to help with multiprocessing.
"""


def terminate_tree(process: Process):
    """
    Terminates a process along with all of its child processes.
    """
    try:
        pid = process.pid
        for child in psutil.Process(pid).children(recursive=True):
            child.terminate()
    except psutil.NoSuchProcess:
        pass
    finally:
        process.terminate()


def is_main_process() -> bool:
    """Returns whether the current process is the main process."""
    return current_process().name == "MainProcess"


def setup_matlab_runtime():
    """
    Sets the LD_LIBRARY_PATH variable to the value provided
    in the arguments. Required on Linux, but can be safely called
    on other operating systems.

    Should not be executed in the main process, because this will
    crash PyQt on Linux.
    """
    if is_main_process():
        raise MultiProcessingException("Do not set the LD_LIBRARY_PATH environment variable on the main process; "
                                       "it will break the program on Linux. Instead, call MATLAB code from "
                                       "another process using Task and Scheduler. See MPHandler for examples"
                                       "of this.")
    path = matlab_runtime()
    if path:
        os.environ["LD_LIBRARY_PATH"] = path
        print(f"Set LD_LIBRARY_PATH to {path}")


class MultiProcessingException(Exception):
    """
    Exception thrown when an error is made with multiprocessing.
    """
