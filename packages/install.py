#!/usr/bin/env python3

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
