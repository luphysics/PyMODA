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
from data.parsing import parsing
from data.parsing.BaseParser import BaseParser


class CSVParser(BaseParser):

    def __init__(self, filename):
        super().__init__(filename)

    def parse(self):
        lines = parsing.get_lines(self.filename)
        data = []
        for l in lines:
            for item in l.split(","):
                data.append(float(item))

        return data
