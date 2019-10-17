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

from processes.mp_utils import terminate_tree


class Task:
    """
    A simple class containing a process and an associated queue. The queue should have been
    passed to the process, the process should put its output in the queue.
    """

    def __init__(self, process: Process, queue: Queue, subtasks=0):
        self.process = process
        self.queue = queue

        self.running = False
        self.finished = False

        # The number of processes which will be spawned as part of this task.
        self.subtasks: int = subtasks

    def start(self) -> None:
        """Starts the task."""
        if not self.running and not self.finished:
            self.process.start()
            self.running = True

    def terminate(self) -> None:
        """
        Terminates the task and all running sub-tasks.
        """
        try:
            terminate_tree(self.process)
            self.queue.close()
        except:
            pass
        finally:
            self.running = False

    def total_tasks(self) -> int:
        """
         Returns the total number of tasks associated with this
         instance, including sub-tasks.
         """
        return 1 + self.subtasks

    def update(self) -> None:
        """
        Checks whether the task has finished, and sets properties
        according to the result.
        """
        if self.running and self.has_result():
            self.finished = True
            self.running = False

    def has_result(self) -> bool:
        """Returns whether the task has finished."""
        return not self.queue.empty()
