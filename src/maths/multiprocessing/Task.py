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

from maths.multiprocessing.mp_utils import terminate_tree


class Task:

    def __init__(self, process: Process, queue: Queue, on_result, subtasks=0):
        self.process = process
        self.queue = queue
        self.on_result = on_result

        self.running = False
        self.finished = False
        self.subtasks: int = subtasks

    def start(self):
        if not self.running and not self.finished:
            self.process.start()
            self.running = True

    def terminate(self):
        try:
            terminate_tree(self.process)
            self.queue.close()
        except:
            pass
        finally:
            self.running = False

    def total_tasks(self) -> int:
        return 1 + self.subtasks

    def update(self):
        if self.has_result():
            self.finished = True
            self.running = False
            self.on_result(*self.queue.get())

    def has_result(self) -> bool:
        return not self.queue.empty()
