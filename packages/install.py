#!/usr/bin/env python3

"""
Python script which installs all Matlab-packaged libraries and pip dependencies.

IMPORTANT: Moving or renaming this file will break PyMODA's updater.
Check the code in 'src/updater' before making changes to command-line arguments or core functionality.
"""

import os
import platform
import subprocess
import sys
import time
from glob import glob
from os import path
from typing import Tuple

err_msg_python_version = "Error: Python 3.6 or greater is required. Please install a newer version of Python."
assert sys.version_info >= (3, 6,), err_msg_python_version

# Pip parameter for avoiding permission issues.
user_flag = "--user"


def run_command(command: str, verbose=False, dry_run=False) -> Tuple[str, str]:
    """
    Runs a command via the system shell.

    :param command: the command, as a string
    :param verbose: whether to return the output
    :param dry_run: whether to 'dry-run' the command (pretend to run it)
    """
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


def fatal_error(message: str) -> None:
    """
    Prints an error and calls sys.exit().
    """
    print(f"Error: {message}")
    sys.exit(1)


def arg_exists(character: str) -> bool:
    """
    Returns whether a character appears in a command-line argument.

    The arguments in this script are very primitive, and are designed to each be one letter.
    Any combination of letters, with or without spacing, is valid.
    """
    return any(character in arg for arg in sys.argv[1:])


if __name__ == "__main__":
    # Set working directory to here.
    wd = path.dirname(path.abspath(__file__))
    os.chdir(wd)

    print(f"Set working directory to: {os.getcwd()}")

    # Set values from command-line arguments.
    verbose = arg_exists("v")
    matlab_only = arg_exists("m")
    dry_run = arg_exists("d")
    yes = arg_exists("y")
    force_user = arg_exists("u")

    # Whether the OS is Windows.
    is_windows = "Windows" == platform.system()

    # Whether the OS is macOS.
    is_mac = "Darwin" == platform.system()

    # If Python is in a virtual environment, don't use the --user flag.
    # Also, don't use it on macOS unless force-enabled.
    if not force_user and (os.environ.get("VIRTUAL_ENV") or is_mac):
        user_flag = ""

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
            "-y\t\t Yes\t\t Automatically accept confirmations.\n"
            "-v\t\t Verbose\t Prints the output from the commands.\n"
            "-d\t\t Dry-run\t Prints the commands that will be run, but does not run them.\n"
            "-m\t\t MATLAB-only\t Only installs the MATLAB packages. Does not install pip dependencies.\n\n"
            "-u\t\t User flag\t Forces pip commands to run with the '--user' flag. May be useful on macOS.\n\n"
        )

        try:
            input("Press [ENTER] to proceed with current settings, or Ctrl-C to exit.")
        except KeyboardInterrupt:
            sys.exit(0)

        print("\n\n")

    python = sys.executable  # Path to correct python interpreter.
    pip = f"{python} -m pip"  # Pip command for current interpreter.

    if " " in python:
        fatal_error(
            f"Please reinstall Python so that its path does not contain spaces. The current Python path is '{python}'."
        )

    files = []

    # Get all the `setup.py` files for MATLAB packages.
    for file in glob("**/setup.py", recursive=True):
        if "for_redistribution_files_only" in file:
            files.append(os.path.abspath(file))

    for f in files:
        os.chdir(wd)
        os.chdir("/".join(f.replace("\\", "/").split("/")[:-1]))

        out, err = run_command(
            f"{python} setup.py install {user_flag}", verbose=verbose, dry_run=dry_run
        )
        if verbose:
            time.sleep(0.5)

    if not matlab_only:
        msg = "Please wait, the next command may take over a minute."
        asterisks = "*" * len(msg)
        print(f"{asterisks}\n{msg}\n{asterisks}\n")

        os.chdir(f"{wd}/..")
        run_command(
            f"{pip} install -r requirements.txt {user_flag}",
            verbose=verbose,
            dry_run=dry_run,
        )

        if is_windows:
            run_command(
                f"{pip} install winshell pypiwin32 {user_flag}",
                verbose=verbose,
                dry_run=dry_run,
            )

    print("\nInstall script has finished.")
