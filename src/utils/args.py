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
from typing import Optional, Tuple

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
        "-files",
        action="store",
        nargs=2,
        default=[None, None],
        help="A preset pair of data files to use when testing group coherence.",
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
        help="**Must be specified on Linux, and may be required on macOS.**"
        "\nThe LD_LIBRARY_PATH, or DYLD_LIBRARY_PATH, used to make libraries run using the MATLAB Runtime. ",
    )
    p.add_argument(
        "--no-maximise",
        action="store_false",
        default=True,
        help="Prevent windows from opening in a maximised state.",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Disable error handling and throw hard exceptions "
        "which will crash the program with a traceback.",
    )
    p.add_argument(
        "--post-update",
        action="store_true",
        default=False,
        help="This argument should not be supplied manually. "
        "It is automatically passed when the PyMODA updater relaunches the program.",
    )
    p.add_argument(
        "--no-update",
        action="store_true",
        default=False,
        help="Ignore potential updates to PyMODA.",
    )
    p.add_argument(
        "--python-wt",
        action="store_true",
        default=False,
        help="Switch to the Python implementation of the wavelet transform.",
    )
    p.add_argument(
        "--create-shortcut",
        action="store_true",
        default=False,
        help="Create a desktop shortcut when PyMODA launches.",
    )
    p.add_argument(
        "--launcher",
        action="store_true",
        default=False,
        help="Passed by the PyMODA launcher when it starts PyMODA.",
    )
    return p


def init():
    """
    Parses the args and sets the global 'args' variable.
    """
    global args
    args = parser().parse_args()


def initargs(func):
    """
    Decorator which automatically initialises 'args' if it is None.
    """
    global args

    def wrapper(*w_args, **kwargs):
        if args is None:
            init()

        return func(*w_args, **kwargs)

    return wrapper


@initargs
def args_file() -> Optional[str]:
    """Gets the file from the args, or returns None."""
    if args and args.file:
        return args.file[0]

    return None


@initargs
def args_files() -> Tuple[Optional[str], Optional[str]]:
    """
    Gets the values passed with the '--files' argument.
    """
    if args and args.files:
        return args.files

    return None, None


@initargs
def args_freq() -> Optional[float]:
    """Gets the frequency from the args, or returns None."""
    if args and args.freq:
        return args.freq[0]

    return None


@initargs
def maximise() -> bool:
    """
    Returns whether a window should be maximised, according to the
    arguments.
    """
    return not args or args.no_maximise


@initargs
def debug() -> bool:
    """Returns whether error handling should be disabled."""
    return args and args.debug


@initargs
def matlab_runtime() -> Optional[str]:
    """
    Returns the LD_LIBRARY_PATH for the Matlab Runtime when it has been set with
    an argument.
    """
    if args and args.runtime:
        return args.runtime[0]

    return None


@initargs
def python_wt() -> bool:
    """
    Returns
    -------
    bool
        Whether to use the MATLAB implementation of the wavelet transform.
    """
    return args and args.python_wt


@initargs
def create_shortcut() -> bool:
    """
    Returns whether the '--create-shortcut' argument has been supplied.
    """
    return args and args.create_shortcut


@initargs
def post_update() -> bool:
    """
    Returns whether an update has just completed. This argument is set by
    the updater when it launches PyMODA after an update.
    """
    return args and args.post_update


@initargs
def set_post_update(value: bool) -> None:
    """
    Sets the boolean associated with `--post-update` to a value.
    This is used after an update has completed, to set the value to False.
    """
    if args:
        args.post_update = value


@initargs
def no_update() -> bool:
    """
    Returns whether PyMODA should avoid showing that updates are available.
    """
    return args and args.no_update


@initargs
def launcher() -> bool:
    """
    Returns whether PyMODA was started via the launcher.
    """
    return args and args.launcher
