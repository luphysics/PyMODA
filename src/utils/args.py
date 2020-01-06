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
from argparse import ArgumentParser

# Args are global and should only be modified at startup.
from typing import Optional

from updater import update

args = None


def parser() -> ArgumentParser:
    """
    Creates the argument parser for PyMODA.
    """
    p = ArgumentParser(description="PyMODA argument parser")

    p.add_argument(
        "-file",
        action="store",
        nargs=1,
        default=None,
        help="A preset data file to use when testing.",
    )
    p.add_argument(
        "-freq",
        action="store",
        type=float,
        nargs=1,
        default=None,
        help="A preset sampling frequency to use when testing.",
    )
    p.add_argument(
        "-runtime",
        action="store",
        nargs=1,
        default=None,
        help="***Must be specified on Linux.***"
        "\nThe LD_LIBRARY_PATH used to make libraries run using the MATLAB Runtime. ",
    )
    p.add_argument(
        "--no-maximise",
        action="store_false",
        default=True,
        help="Use this argument to prevent windows from opening in a maximised state.",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Use this argument to disable error handling and throw hard exceptions "
        "which will crash the program with a traceback.",
    )
    p.add_argument(
        update.arg_post_update,
        action="store_true",
        default=False,
        help="This argument should not be supplied manually. "
        "It is automatically passed when the PyMODA updater relaunches the program.",
    )
    p.add_argument(
        "--no-update",
        action="store_true",
        default=False,
        help="Use this argument to make PyMODA ignore potential updates.",
    )
    return p


def init():
    """
    Parses the args and sets the global 'args' variable.
    """
    global args
    args = parser().parse_args()


def args_file() -> Optional[str]:
    """Gets the files from the args, or returns None."""
    if args and args.file:
        return args.file[0]
    return None


def args_freq() -> Optional[float]:
    """Gets the frequency from the args, or returns None."""
    if args and args.freq:
        return args.freq[0]
    return None


def maximise() -> bool:
    """
    Returns whether a window should be maximised, according to the
    arguments.
    """
    return not args or args.no_maximise


def debug() -> bool:
    """Returns whether error handling should be disabled."""
    return args and args.debug


def matlab_runtime() -> Optional[str]:
    """
    Returns the LD_LIBRARY_PATH for the Matlab Runtime when it has been set with
    an argument.
    """
    if args and args.runtime:
        return args.runtime[0]
    return None


def post_update() -> bool:
    """
    Returns whether an update has just completed. This argument is set by
    the updater when it launches PyMODA after an update.
    """
    return args and args.post_update


def no_update() -> bool:
    """
    Returns whether PyMODA should avoid showing that updates are available.
    """
    return args and args.no_update
