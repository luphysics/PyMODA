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

import asyncio
import os
import signal
import sys
from os import path

from qasync import QEventLoop

from gui.Application import Application
from utils import errorhandling, stdout_redirect, args

if __name__ == "__main__":
    # Fix Ctrl-C behaviour with PyQt.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Set the working directory to the 'src' directory for consistency.
    location = path.dirname(path.abspath(__file__))
    os.chdir(location)

    args.init()
    errorhandling.init()
    stdout_redirect.init()

    app = Application(sys.argv)

    # Setup asyncio to work with PyQt.
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Open the launcher window. Must be called after setting the event loop.
    app.start_launcher()

    with loop:
        sys.exit(loop.run_forever())
