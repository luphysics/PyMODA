#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2019  Lancaster University
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
The entry-point of PyMODA.
"""
from processes import mp_utils

# Monkey-patch processes to ensure that they can use logging.
mp_utils.monkeypatch_processes()

import asyncio
import multiprocessing
import multiprocess
import os
import utils
import signal
import sys

from os import path
from pathlib import Path
from qasync import QEventLoop
from gui.Application import Application
from utils import errorhandling, stdout_redirect, args, log_utils

if __name__ == "__main__":
    # Fix issues when packaged with PyInstaller.
    for m in (multiprocess, multiprocessing):
        m.freeze_support()

    # Set the working directory for consistency.
    if utils.is_frozen:
        # When packaged with PyInstaller.
        location = os.path.abspath(sys._MEIPASS)
    else:
        # When running as a normal Python program.
        location = Path(path.abspath(path.dirname(__file__))).parent

    # Set the working directory to the 'src' directory for consistency.
    os.chdir(location)

    # Fix Ctrl-C behaviour with PyQt.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    args.init()
    log_utils.init()
    errorhandling.init()
    stdout_redirect.init()

    app = Application(sys.argv)

    # Setup asyncio to work with PyQt.
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Fix multiprocessing on macOS.
    mp_utils.set_mp_start_method()

    # Open the launcher window. Must be called after setting the event loop.
    app.start_launcher()

    with loop:
        sys.exit(loop.run_forever())
