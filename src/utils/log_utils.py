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
import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from os.path import join

from utils import file_utils, errorhandling

global_filename = None  # Only used by processes on macOS/Linux.


def init(filepath: str = None) -> None:
    if filepath:
        log_path = filepath
    else:
        log_path = file_utils.log_path

    logging.basicConfig(filename=log_path, level=logging.INFO)
    log = logging.getLogger("root")

    handler = RotatingFileHandler(log_path, mode="a", maxBytes=1024 * 1024 * 10)
    log.addHandler(handler)


def process_init() -> None:
    """
    Initialise logging for a process. Different processes need to log to different files,
    so each process can call this function to start logging.
    """
    filename = str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")
    filename = ".".join(filename.split(".")[:-1])

    filepath = join(file_utils.pymoda_path, "processes")
    os.makedirs(filepath, exist_ok=True)

    global global_filename
    global_filename = join(filepath, f"{filename}.log")

    logging.basicConfig(filename=global_filename, level=logging.INFO)
    errorhandling.init()


def process_write_log(msg: str) -> None:
    """
    Used by processes on macOS/Linux; writes a message to the log file manually.

    Parameters
    ----------
    msg : str
        The text to append to the log file.
    """
    global global_filename

    with open(global_filename, "a+") as f:
        f.write(msg)
