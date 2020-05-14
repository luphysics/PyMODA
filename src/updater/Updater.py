#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2020 Lancaster University
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
import shutil
import stat
import tarfile
import warnings
import zipfile
from abc import ABC, abstractmethod
from os.path import join
from typing import Iterable
from urllib.request import urlopen

import updater.download
from updater.download import chunked_download
from utils import launcher
from utils.os_utils import OS


class Updater(ABC):
    def __init__(self, tag: str):
        self.tag = tag

    @abstractmethod
    def download_launcher(self) -> None:
        pass

    @abstractmethod
    def download_archive(self, release_tag: str) -> None:
        pass

    @abstractmethod
    def extract_archive(self) -> None:
        pass

    @abstractmethod
    def move_files(self) -> None:
        pass

    def finish(self) -> None:
        self._write_latest_file()

    def is_version_present(self) -> bool:
        latest_files = self._get_latest_files()

        return latest_files and any([self.tag in f for f in latest_files])

    def _download_url(self) -> str:
        return updater.download.get_pymoda_download_url()

    def _get_latest_files(self) -> Iterable[str]:
        return list(
            filter(
                lambda f: "latest-" in f, os.listdir(launcher.get_launcher_directory())
            )
        )

    def _write_latest_file(self) -> None:
        launcher_dir = launcher.get_launcher_directory()

        latest_files = self._get_latest_files()
        for f in latest_files:
            os.remove(join(launcher_dir, f))

        with open(join(launcher_dir, f"latest-{self.tag}"), "w") as f:
            f.write("")


class WindowsUpdater(Updater):
    def download_launcher(self) -> None:
        warnings.warn("Cannot download launcher on Windows.")

    def download_archive(self, release_tag: str) -> None:
        try:
            os.remove("pymoda-temp.zip")
        except:
            pass

        url = self._download_url()
        with urlopen(url) as response:
            chunked_download(filename="pymoda-temp.zip", response=response)

    def extract_archive(self) -> None:
        try:
            shutil.rmtree("pymoda-temp")
        except:
            pass

        with zipfile.ZipFile("pymoda-temp.zip") as f:
            f.extractall("pymoda-temp")

        os.remove("pymoda-temp.zip")

    def move_files(self) -> None:
        launcher_dir = launcher.get_launcher_directory()

        os.rename(join("pymoda-temp", "PyMODA"), join("pymoda-temp", self.tag))
        shutil.move(join("pymoda-temp", self.tag), launcher_dir)


class NixUpdater(Updater, ABC):
    def download_launcher(self) -> None:
        launcher_dir = launcher.get_launcher_directory()
        url = updater.download.get_launcher_download_url()

        try:
            os.remove("launcher-temp")
        except:
            pass

        if url:
            with urlopen(url) as response:
                chunked_download(filename="launcher-temp", response=response)

        try:
            os.remove(join(launcher_dir, "launcher"))
        except:
            pass

        # Move 'launcher-temp' to the launcher directory as 'launcher'.
        shutil.move("launcher-temp", join(launcher_dir, "launcher"))

        # Make launcher executable. ('rwx' permissions for owner.)
        os.chmod(join(launcher_dir, "launcher"), stat.S_IRWXU)

    def download_archive(self, release_tag: str) -> None:
        try:
            os.remove("pymoda-temp.tar.gz")
        except:
            pass

        url = self._download_url()

        with urlopen(url) as response:
            chunked_download(filename="pymoda-temp.tar.gz", response=response)

    def extract_archive(self) -> None:
        try:
            shutil.rmtree("pymoda-temp")
        except:
            pass

        with tarfile.open("pymoda-temp.tar.gz") as f:
            f.extractall("pymoda-temp")

        os.remove("pymoda-temp.tar.gz")


class LinuxUpdater(NixUpdater):
    def move_files(self) -> None:
        launcher_dir = launcher.get_launcher_directory()
        shutil.move(join("pymoda-temp", "PyMODA"), join(launcher_dir, self.tag))


class MacUpdater(NixUpdater):
    def move_files(self) -> None:
        launcher_dir = launcher.get_launcher_directory()
        shutil.move("pymoda-temp", join(launcher_dir, self.tag))


def get_instance(tag) -> Updater:
    """
    Creates the Updater for the current OS.

    Parameters
    ----------
    tag : str
        The release tag of the latest release.

    Returns
    -------
    Updater
        The Updater for the current OS.
    """
    if OS.is_windows():
        return WindowsUpdater(tag)
    elif OS.is_linux():
        return LinuxUpdater(tag)
    else:
        return MacUpdater(tag)
