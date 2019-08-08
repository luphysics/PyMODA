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

import scipy.io


class Cache:

    def __init__(self):
        self.cache = self.get_cache_location()
        try:
            os.mkdir(self.cache)
        except:
            pass

    @staticmethod
    def get_cache_location():
        base = os.getcwd()

        # If current directory is src, then create cache
        # in directory above.
        if base.split("/")[-1] == "src":
            base = f"{base}/.."

        return f"{base}/cache"

    def get_file_names(self) -> list:
        return os.listdir(self.cache)

    def generate_file_name(self, extension=".mat") -> str:
        names = self.get_file_names()
        i = -1
        while True:
            i += 1
            n = self._name_template(i)

            if i not in names:
                break

        return f"{n}{extension}"

    def get_path_to(self, file: str):
        return f"{self.cache}/{file}"

    def save_data(self, data) -> str:
        name = self.generate_file_name()
        path = self.get_path_to(name)
        scipy.io.savemat(path, data)
        return name

    @staticmethod
    def _name_template(index) -> str:
        return f"data{index}"
