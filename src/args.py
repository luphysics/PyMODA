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
args = None


def parser():
    """Creates the argument parser for PyMODA."""
    p = ArgumentParser(description="PyMODA argument parser")
    p.add_argument("-files", metavar="test_files", action="store", nargs="+", default=None,
                   help="Test files to load")
    p.add_argument("-freq", metavar="frequency", action="store", type=float, nargs=1, default=None,
                   help="Frequency to use")
    return p


def parse_args():
    """Parses the args and sets the global 'args' variable."""
    global args
    args = parser().parse_args()


def args_file():
    """Gets the files from the args, or returns None."""
    if args and args.files:
        return args.files
    return None


def args_freq():
    """Gets the frequency from the args, or returns None."""
    if args and args.freq:
        return args.freq[0]
    return None
