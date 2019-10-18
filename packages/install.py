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


def run_command(command: str, verbose=False) -> Tuple[str, str]:
    print(f"Running command: {command}")

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

    print(f"\n{red}Error: {message}{endc}")
    sys.exit(1)


if __name__ == "__main__":
    assert sys.version_info >= (3, 6)

    # Use verbose mode when "-v" is provided as an argument.
    verbose = len(sys.argv) > 1 and "v" in sys.argv[1].lower()
    if verbose:
        print("Launched in verbose mode.\n")
        time.sleep(1)
    else:
        print(
            "Launched in normal mode. Use command-line argument '-v' to launch in verbose mode.\n"
        )

    # Whether the OS is Windows-based.
    is_windows = "Windows" == platform.system()

    python = sys.executable  # Path to correct python interpreter.
    pip = f"{python} -m pip"  # Pip command for current interpreter.

    if " " in python:
        python = f'"{python}"'  # If Python path contains spaces, use quotes.

    wd = check_cwd()
    files = []

    # Get all the `setup.py` files for MATLAB packages.
    for file in glob("**/setup.py", recursive=True):
        if "for_redistribution_files_only" in file:
            files.append(os.path.abspath(file))
 
    for f in files:
        os.chdir(wd)
        os.chdir("/".join(f.replace("\\", "/").split("/")[:-1]))

        out, err = run_command(f"{python} setup.py install", verbose=verbose)
        if "Permission denied" in err:
            fatal_error(
                "Install script must be run with elevated permissions. "
                "Use an administrator terminal on Windows or prefix the command with 'sudo' on macOS/Linux."
            )

    os.chdir(f"{wd}/..")
    run_command(f"{pip} install -r requirements.txt", verbose=verbose)

    if is_windows:
        run_command(f"{pip} install winshell pypiwin32", verbose=verbose)

    print("\nInstall script has finished.")
