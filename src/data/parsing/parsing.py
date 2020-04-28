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

from data.parsing.BaseParser import BaseParser
from data.parsing.CsvParser import CsvParser
from data.parsing.MatParser import MatParser
from data.parsing.NpyParser import NpyParser
from data.parsing.groups.GroupMatParser import GroupMatParser
from data.parsing.groups.GroupNpyParser import GroupNpyParser


def get_lines(filename):
    lines = []
    try:
        with open(filename, mode="r", encoding="utf-8-sig") as f:
            for line in f:
                lines.append(line)
    except FileNotFoundError:
        print(f"File not found at path: '{filename}'")
        raise ParsingException(f"File does not exist: {filename}")

    return lines


def get_parser(filename, groups=False) -> BaseParser:
    """
    Gets the appropriate parser for a given file.

    Parameters
    ----------
    filename : str
        The name of the file which will be parsed.
    groups : Optional[bool]
        (Default = False) Whether the parser is intended to load a signal group, as used by group phase coherence.
    """
    _, extension = os.path.splitext(filename)
    extension = extension.lower()

    if extension == ".mat":
        return MatParser(filename) if not groups else GroupMatParser(filename)
    elif extension == ".csv" or extension == ".txt":
        return CsvParser(filename)
    elif extension == ".npy":
        return NpyParser(filename) if not groups else GroupNpyParser(filename)

    raise ParsingException(f"Cannot parse a file with the extension: {extension}")


class ParsingException(Exception):
    """
    Exception raised when errors are encountered during parsing.
    """
