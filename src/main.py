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
import asyncio
import signal
import sys

from qasync import QEventLoop

from gui.Application import Application
from utils import errorhandling, stdout_redirect, args

# The entry-point of the program.
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Fixes Ctrl-C behaviour.

    args.init(set_working_dir=True)
    errorhandling.init()
    stdout_redirect.init()

    app = Application(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Must be called after setting the event loop.
    app.start_launcher()

    with loop:
        sys.exit(loop.run_forever())
