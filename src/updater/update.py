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
Entry-point of the PyMODA updater. Also contains functions which can be called from PyMODA.

The update process is as follows:
    - PyMODA calls `start_update()`.
    - This folder is copied to a temporary folder, 'temp' in PyMODA's root directory.
    - The copy of this file is executed in 'temp' using PyMODA's command-line arguments.
    - PyMODA exits.
    - This file downloads the new version of PyMODA from GitHub and overwrites the old version.
    - PyMODA is launched using the same arguments which were passed in from the original PyMODA.
"""

import os

# Fix issue where imports fail when launching from 'temp'.
os.environ["PYTHONPATH"] = "."

import asyncio
import json
import shutil
import subprocess
import sys
from os import path
from pathlib import Path
from typing import Optional, List

import aiohttp
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

api_url = "https://api.github.com/repos/luphysics/pymoda"
zip_url = f"{api_url}/zipball/master"

commit_url = f"{api_url}/git/refs/heads/master"
temp = "temp"

# The folder where the new version of PyMODA will be unzipped.
unzip_target = "pymoda_new"


async def get_latest_commit() -> Optional[str]:
    """
    Called by PyMODA. Performs a GitHub API request and returns the hash
    of the latest commit on the 'master' branch.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(commit_url) as response:
            text = await response.text()
            obj = json.loads(text).get("object")

            if not obj:
                return None

            return obj.get("sha")


async def get_repo_size() -> Optional[int]:
    """
    Called in 'temp' to get the size of the PyMODA repository before
    downloading as a zip file. This is usually less than the actual size
    of the zip file, but GitHub uses chunked encoding so there is no
    "Content-Length" header to provide the size of the zip file while
    downloading it.

    :return: the size in bytes
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            text = await response.text()

            size = json.loads(text).get("size")
            if size is not None:
                size *= 1000  # Convert to bytes.

            return size


def start_update(root_directory: str) -> None:
    """
    Called by PyMODA to trigger an update. Copies the update scripts to 'temp',
    starts an instance of the updater in 'temp' and exits PyMODA.

    :param root_directory: the root PyMODA folder.
    """
    temp_path = path.join(root_directory, temp)
    try:
        shutil.rmtree(temp_path)
    except FileNotFoundError:
        pass

    current_path = path_here()
    shutil.copytree(current_path, temp_path)

    updater_path = path.join(temp_path, path.basename(__file__))
    print(f"Launching updater at: {updater_path}")
    subprocess.Popen([sys.executable, updater_path, *sys.argv[1:]])

    from PyQt5.QtCore import QCoreApplication

    QCoreApplication.quit()

    sys.exit(0)


def extract_zip(zip_path: str) -> None:
    """
    Called in 'temp'. Extracts the zip file containing a new version of PyMODA.

    This will produce a new folder containing the new version of PyMODA
    in the current folder.

    :param zip_path: the path to the zip file
    """
    import zipfile

    try:
        # Just in case the target folder already exists, try deleting it.
        shutil.rmtree(unzip_target)
    except:
        # It doesn't exist; no problem.
        pass

    # Extract the zip file.
    with zipfile.ZipFile(zip_path, "r") as zipref:
        zipref.extractall(unzip_target)


def copy_files() -> None:
    """
    Called in 'temp'. Replaces the current version of PyMODA with the new version. Any files/folders with
    the same name as files/folders in the new version will be deleted before the new version
    is copied into their location.

    If a file exists in the root directory of the current version but not the old version,
    it will not be deleted. All files inside a directory will be deleted and replaced if the
    directory exists in the new version.
    """
    # PyMODA folder. Working directory has already been set correctly.
    target = Path(os.getcwd()).parent

    print(f"Current directory: {os.getcwd()}")
    print(f"Target directory: {target}")

    # Backup folder.
    backup_folder = path.join(target, f"backup")

    # Path to new files. This will be where the new version of PyMODA has been extracted.
    # The PyMODA code will be in the only folder inside `unzip_target`.
    pymoda_new = [path.join(unzip_target, f) for f in os.listdir(unzip_target)][0]
    print(f"New files are at: {pymoda_new}")

    # Delete current backup folder.
    try:
        shutil.rmtree(backup_folder)
    except:
        # If the folder doesn't exist, ignore the exception.
        pass

    # Copy current PyMODA folder to 'backup', creating backup of current PyMODA.
    shutil.copytree(target, backup_folder, ignore=shutil.ignore_patterns(".git"))

    # For every file/folder in the new version of PyMODA, delete the old file/folder
    # from the current PyMODA folder and copy the new file/folder to its location.
    for f in os.listdir(pymoda_new):
        if f == "__pycache__" or f.endswith(".pyc") or f == ".idea":
            continue

        # Remove old file/folder from target directory.
        old = path.join(target, f)
        print(f"Removing {old}")
        _remove_file(old)

        # Copy new version of file/folder to target directory.
        file_path = path.join(pymoda_new, f)
        print(f"Copying {file_path} to {target}")
        _copy_new_file(file_path, target)


def _remove_file(file_path: str) -> None:
    """
    Removes a file/folder.

    :param file_path: the path to the file/folder
    """
    try:
        if path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
    except Exception as e:
        print(e)


def _copy_new_file(file_path: str, target: str) -> None:
    """
    Copies a file/folder to a new location.

    :param file_path: the path to the file/folder
    :param target: the new location
    """
    try:
        if path.isdir(file_path):
            target_folder = path.join(target, path.basename(file_path))
            shutil.copytree(file_path, target_folder)
        else:
            shutil.copy(file_path, target)
    except Exception as e:
        print(e)


def path_here() -> str:
    """
    Returns the absolute path to the location of this file.

    WARNING: When running in temp/, it actually seems to return the path to the original
    file in src/updater/.
    """
    return path.dirname(path.abspath(__file__))


def relaunch_pymoda(success: bool) -> None:
    """
    Called in 'temp' to relaunch PyMODA after an update.

    This will launch PyMODA's 'main.py' with all command-line arguments except the first (which
    is the current filename). The '--post-update' argument will be added if the update was a success.

    :param success: whether the update was successful
    """
    args = _get_relaunch_args(success)
    subprocess.Popen(_get_relaunch_command(args), shell=True)

    from PyQt5.QtCore import QCoreApplication

    QCoreApplication.quit()
    sys.exit(0)


def update_packages(success: bool) -> None:
    """
    Calls the install script at packages/install.py, quits the program and relaunches PyMODA with
    the current command-line arguments.

    :param success: whether the update was a success
    """
    # PyMODA directory.
    root = Path(os.getcwd()).parent

    # PyMODA/packages.
    packages = os.path.join(root, "packages")

    # PyMODA/packages/install.py.
    install_script = os.path.join(packages, "install.py")

    # Command to run install.py with the current interpreter.
    install_command = f"{sys.executable} {install_script} -y"

    args = _get_relaunch_args(success)
    relaunch_command = _get_relaunch_command(args)

    # Run the commands. '&&' should work on all OSes.
    subprocess.Popen(f"{install_command} && {relaunch_command}", shell=True)

    from PyQt5.QtCore import QCoreApplication

    QCoreApplication.quit()
    sys.exit(0)


def _get_relaunch_command(args: List[str]) -> str:
    """
    Gets the command used to relaunch PyMODA.

    :param args: the command-line arguments to use
    :return: the shell command
    """
    src_main = path.join("src", "main.py")

    root = Path(os.getcwd()).parent
    main_path = path.join(root, src_main)

    args_string = " ".join(args)
    return f"{sys.executable} {main_path} {args_string}"


def _get_relaunch_args(success: bool) -> List[str]:
    """
    Gets the command-line arguments to use when relaunching PyMODA.

    :param success: whether the update was successful
    """
    args = sys.argv[1:]
    if success:
        args.append(arg_post_update)

    return args


def cleanup() -> None:
    """
    Called by PyMODA. Cleans up after an update by deleting the 'temp' folder.
    """
    _temp_folder = path.join(Path(os.getcwd()).parent, temp)
    try:
        shutil.rmtree(_temp_folder)
    except:
        pass


arg_post_update = "--post-update"

if __name__ == "__main__":
    # Change working directory to this file's location.
    new_wd = path.dirname(path.abspath(sys.argv[0]))
    os.chdir(new_wd)

    app = QApplication(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    from updater.UpdateWindow import UpdateWindow

    window = UpdateWindow(app)
    window.show()

    with loop:
        sys.exit(loop.run_forever())
