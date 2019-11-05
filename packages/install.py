#!/usr/bin/env python3

"""
Python script which installs all Matlab packages and pip dependencies.
"""

import os
import platform
import subprocess
import sys
import time
from glob import glob
from typing import Tuple, Optional

packages = "packages"
cwd = os.getcwd()


def find_cwd() -> Optional[str]:
    if packages in os.listdir("."):
        return os.path.join(cwd, packages)
    elif cwd.replace("\\", "/").split("/")[-1] == packages:
        return cwd
    return None


def check_cwd() -> str:
    new_cwd = find_cwd()

    if not new_cwd:
        fatal_error(
            "The script should be executed from the PyMODA directory or its `packages` subfolder."
        )

    os.chdir(new_cwd)
    return new_cwd


def run_command(command: str, verbose=False, dry_run=False) -> Tuple[str, str]:
    print(f"Working directory: {os.getcwd()}")
    print(f"Running command: {command}", end="\n\n")

    if dry_run:
        return "", ""

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )
    output = result.stdout
    error = result.stderr

    if verbose:
        print(output, end="\n\n")
        if error:
            print(error, end="\n\n")

    return output, error


def fatal_error(message: str):
    # ANSI codes to make the text red.
    red, endc = "\033[91m", "\033[0m"

    print(f"{red}\n\nError: {message}\n\n{endc}")
    sys.exit(1)


if __name__ == "__main__":
    assert sys.version_info >= (3, 6), "You must use Python 3.6 or greater."

    # Set values from command-line arguments.
    verbose = any(["v" in arg for arg in sys.argv[1:]])
    matlab_only = any(["m" in arg for arg in sys.argv[1:]])
    dry_run = any(["d" in arg for arg in sys.argv[1:]])
    yes = any(["y" in arg for arg in sys.argv[1:]])

    if verbose:
        print("Launched in verbose mode.\n")
        time.sleep(1)
    if dry_run:
        print("Launched in dry-run mode. Commands will not actually be executed.\n")
        time.sleep(1)
    if matlab_only:
        print("Launched in Matlab-only mode. Only Matlab packages will be installed.\n")
        time.sleep(1)
    if not dry_run and not matlab_only and not yes:
        print(
            "\nThis script will install the required packages for the current Python interpreter. \n"
            "The MATLAB packages will be installed from the local folders, and pip will be used \n"
            "to install the dependencies from 'requirements.txt'.\n"
        )

        print(
            "Command-line arguments can be used with this script:\n\n"
            "Argument\t Name\t\t Purpose\n"
            "--------\t ----\t\t -------\n"
            "-y\t\t N/A\t\t Runs the script without user intervention.\n"
            "-v\t\t Verbose\t Prints the output from the commands.\n"
            "-d\t\t Dry-run\t Prints the commands that will be run, but does not run them.\n"
            "-m\t\t MATLAB-only\t Only installs the MATLAB packages. Does not install pip dependencies.\n\n"
        )

        try:
            input("Press [ENTER] to proceed with current settings, or Ctrl-C to exit.")
        except KeyboardInterrupt:
            sys.exit(0)

        print("\n\n")

    # Whether the OS is Windows-based.
    is_windows = "Windows" == platform.system()

    python = sys.executable  # Path to correct python interpreter.
    pip = f"{python} -m pip"  # Pip command for current interpreter.

    if " " in python:
        fatal_error(
            f"Please reinstall Python so that its path does not contain spaces. The current Python path is '{python}'."
        )

    wd = check_cwd()
    files = []

    # Get all the `setup.py` files for MATLAB packages.
    for file in glob("**/setup.py", recursive=True):
        if "for_redistribution_files_only" in file:
            files.append(os.path.abspath(file))

    for f in files:
        os.chdir(wd)
        os.chdir("/".join(f.replace("\\", "/").split("/")[:-1]))

        out, err = run_command(
            f"{python} setup.py install --user", verbose=verbose, dry_run=dry_run
        )
        if verbose:
            time.sleep(0.5)

    if not matlab_only:
        msg = "Please wait, the next command may take over a minute."
        asterisks = "*" * len(msg)
        print(f"{asterisks}\n{msg}\n{asterisks}\n")

        os.chdir(f"{wd}/..")
        run_command(
            f"{pip} install -r requirements.txt --user",
            verbose=verbose,
            dry_run=dry_run,
        )

        if is_windows:
            run_command(
                f"{pip} install winshell pypiwin32 --user",
                verbose=verbose,
                dry_run=dry_run,
            )

    print("\nInstall script has finished.")
