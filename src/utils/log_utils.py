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
import logging
from logging.handlers import RotatingFileHandler

from utils import file_utils


def init() -> None:
    log_path = file_utils.log_path

    logging.basicConfig(filename=log_path, level=logging.INFO)
    log = logging.getLogger("root")

    handler = RotatingFileHandler(log_path, mode="a", maxBytes=1024 * 1024 * 10)
    log.addHandler(handler)
