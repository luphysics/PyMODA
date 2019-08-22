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

from PyQt5.QtCore import QTimer


class Watcher:
    """
    A class which watches for a result from a process.
    """

    def __init__(self, window, queue, delay_seconds, on_result):
        """
        :param window: the QWindow from which the operation is being performed
        :param queue: the queues which will be used to get the result from the other process
        :param delay_seconds: the time between each consecutive check for a result
        :param on_result: a callback which should run on the main process/thread, taking
        the result of the operation
        """
        self.on_result = on_result
        self.queue = queue
        self.running = False

    def trigger_result(self):
        """Trigger the result callback to return data to the main process."""
        if self.has_result():
            self.on_result(*self.queue.get())

    def has_result(self) -> bool:
        return not self.queue.empty()
