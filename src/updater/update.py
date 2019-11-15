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
from typing import Optional

import aiohttp
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

api_url = "https://api.github.com/repos/luphysics/pymoda"
zip_url = f"{api_url}/zipball/master"

commit_url = f"{api_url}/git/refs/heads/master"
temp = "temp"


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

    sys.exit(0)


def extract_zip(zip_path: str) -> None:
    """
    Called in 'temp'. Extracts the zip file containing a new version of PyMODA.

    This will produce a new folder containing the new version of PyMODA
    in the current folder.

    :param zip_path: the path to the zip file
    """
    import zipfile

    with zipfile.ZipFile(zip_path, "r") as zipref:
        zipref.extractall()


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
    new_path = [f for f in os.listdir(".") if path.isdir(f)][-1]

    # Delete backup folder, then copy current PyMODA folder to 'backup'.
    if path.exists(backup_folder):
        shutil.rmtree(backup_folder)

    shutil.copytree(target, backup_folder)

    # For every file/folder in the new version of PyMODA, delete the old file/folder
    # from the current PyMODA folder and copy the new file/folder to its location.
    for f in os.listdir(new_path):
        if f == "__pycache__" or f.endswith(".pyc") or f == ".idea":
            continue

        old = path.join(target, f)
        try:
            print(f"Removing {old}")
            if path.isdir(old):
                shutil.rmtree(old)
            else:
                os.remove(old)
        except Exception as e:
            print(e)

        try:
            new_file = path.join(new_path, f)
            print(f"Copying {new_file} to {target}")
            if path.isdir(new_file):
                target_folder = path.join(target, path.basename(new_file))
                shutil.copytree(new_file, target_folder)
            else:
                shutil.copy(new_file, target)
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
    args = sys.argv[1:]
    if success:
        args.append(arg_post_update)

    src_main = path.join("src", "main.py")
    root = Path(os.getcwd()).parent

    main_path = path.join(root, src_main)
    subprocess.Popen([sys.executable, main_path] + args)

    sys.exit(0)


def cleanup() -> None:
    """
    Called by PyMODA. Cleans up after an update by deleting the 'temp' folder.
    """
    temp = path.join(Path(os.getcwd()).parent, "temp")
    try:
        shutil.rmtree(temp)
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
