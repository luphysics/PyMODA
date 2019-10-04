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


class DBOutputData:

    def __init__(self,
                 tm,
                 p1,
                 p2,
                 cpl1,
                 cpl2,
                 cf1,
                 cf2,
                 mcf1,
                 mcf2,
                 surr_cpl1,
                 surr_cpl2):
        self.tm = tm
        self.surr_cpl2 = surr_cpl2
        self.surr_cpl1 = surr_cpl1
        self.mcf2 = mcf2
        self.mcf1 = mcf1
        self.cf2 = cf2
        self.cf1 = cf1
        self.cpl2 = cpl2
        self.cpl1 = cpl1
        self.p2 = p2
        self.p1 = p1
