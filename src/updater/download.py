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

from http.client import HTTPResponse

from PyQt5.QtCore import pyqtSignal

from utils.os_utils import OS


def chunked_download(
    filename: str,
    response: HTTPResponse,
    size: int = None,
    progress_signal: pyqtSignal = None,
) -> None:
    """
    Downloads the zip file and emits progress.

    :param response: the HTTP response to download the file from
    :param size: the size of the download, in bytes; used for progress
    :param progress_signal: the PyQt signal with which to emit download progress
    """
    if not size:
        size = 10 ** 6 * 44

    with open(filename, "wb") as f:
        bytes_downloaded = 0
        block_size = 1024 * 10

        while True:
            buffer = response.read(block_size)
            if not buffer:
                break

            f.write(buffer)
            bytes_downloaded += block_size

            if progress_signal:
                progress_signal.emit(bytes_downloaded / size * 100)


def get_pymoda_download_url() -> str:
    asset = ""

    if OS.is_windows():
        asset = "PyMODA-win64.zip"
    elif OS.is_linux():
        asset = "PyMODA-linux_x86_64.tar.gz"
    elif OS.is_mac_os():
        asset = "PyMODA-macOS.tar.gz"

    return f"https://github.com/luphysics/pymoda/releases/latest/download/{asset}"


def get_launcher_download_url() -> str:
    asset = ""

    if OS.is_windows():
        return ""
    elif OS.is_linux():
        asset = "launcher-linux"
    elif OS.is_mac_os():
        asset = "launcher-macos"

    return (
        f"https://github.com/luphysics/pymoda-launcher/releases/latest/download/{asset}"
    )
