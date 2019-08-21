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

from multiprocess import Queue, Process

from maths.multiprocessing.Watcher import Watcher
from maths.multiprocessing.mp_utils import terminate_tree


class Task:

    def __init__(self, process: Process, watcher: Watcher):
        self.process = process
        self.watcher = watcher

    def start(self):
        self.process.start()
        self.watcher.start()

    def kill(self):
        terminate_tree(self.process)
        self.watcher.stop()
