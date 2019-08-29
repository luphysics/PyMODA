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

"""
Python script which installs all the custom packages from this directory.
"""
import os
import sys
from glob import glob

packages = "packages"
cwd = os.getcwd()


def find_cwd():
    if packages in os.listdir("."):
        return os.path.join(cwd, packages)
    elif cwd.split("/")[-1] == packages:
        return cwd
    return None


def check_cwd():
    new_cwd = find_cwd()

    if not new_cwd:
        print("ERROR: The script should be executed from the root "
              "source directory or the `packages` folder.")
        sys.exit(1)

    os.chdir(new_cwd)
    return new_cwd


if __name__ == "__main__":
    wd = check_cwd()
    files = []

    for file in glob("**/setup.py", recursive=True):
        if "for_redistribution_files_only" in file:
            files.append(os.path.abspath(file))
           
    for f in files:
        os.chdir(wd)
        os.chdir("/".join(f.split("/")[:-1]))
        os.system(f"python3 setup.py install")
        os.system(f"python setup.py install")

    print("\n")
    print("\n".join([f"Attempted to install package from {f}" for f in files]))
