#!/usr/bin/env python3

"""
Python script which installs all the custom packages from this directory and also installs dependencies via pip.
"""
import os
import platform
import sys
from glob import glob

packages = "packages"
cwd = os.getcwd()

python = "python"


def pip(): return f"{python} -m pip"


def find_cwd():
    if packages in os.listdir("."):
        return os.path.join(cwd, packages)
    elif cwd.replace("\\", "/").split("/")[-1] == packages:
        return cwd
    return None


def check_cwd():
    new_cwd = find_cwd()

    if not new_cwd:
        print("ERROR: The script should be executed from the "
              "PyMODA directory or its `packages` subfolder.")
        sys.exit(1)

    os.chdir(new_cwd)
    return new_cwd


if __name__ == "__main__":
    is_windows = "Windows" == platform.system()
    args = sys.argv

    if not is_windows and len(args) == 1:
        print("Using 'python3' instead of 'python'. If this is not desired, call the script with 'python' as an argument.")
        python = "python3"  # For *nix systems, python3 is required.

    # If a particular version is specified, e.g. "python3.8".
    elif len(args) > 1:
        arg = args[1]
        if len(args) > 2:
            print("ERROR: too many arguments.")
            sys.exit(1)
        if "python" not in arg:
            print(
                f"ERROR: arg '{arg}' does not appear to match a python version.")
            if input("Continue anyway? (y/N) ").lower() != "y":
                sys.exit(1)

        python = arg

    wd = check_cwd()
    files = []

    for file in glob("**/setup.py", recursive=True):
        if "for_redistribution_files_only" in file:
            files.append(os.path.abspath(file))

    for f in files:
        os.chdir(wd)
        os.chdir("/".join(f.replace("\\", "/").split("/")[:-1]))
        os.system(f"{python} setup.py install")

    os.chdir(f"{wd}/..")
    os.system(f"{pip()} install -r requirements.txt")

    print("\n")
    print(f"\nInstalled dependencies for {python}.")
    print("\n".join([f"Attempted to install package from {f}" for f in files]))
    print("\nInstalled pip dependencies from requirements.txt")
