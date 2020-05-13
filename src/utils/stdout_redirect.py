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
import datetime
import logging
import sys
import threading


class StdOut:
    def write(self, text):
        # Output text as normal.
        sys_out.write(text)

        # Write to log file.
        logging.info(msg=text)

        # Notify subscribers.
        for s in subscribers:
            if threading.current_thread() is threading.main_thread():
                if isinstance(s, WindowLogger):
                    s.update(text)
                else:
                    s(text)

    def flush(self):
        return


subscribers = []  # List of subscribers to be notified when stdout is used.

out = StdOut()  # The redirected stdout.
sys_out = sys.__stdout__  # The original system stdout.


def init():
    sys.stdout = out


def subscribe(subscriber):
    subscribers.append(subscriber)


def unsubscribe(subscriber):
    subscribers.remove(subscriber)


class WindowLogger:
    """
    A class which handles logging to a log pane safely,
    without excessive memory usage. When the number of
    logged lines exceeds the max size, the first half
    of the lines are deleted.
    """

    def __init__(self, func, max_lines=200):
        self.func = func
        self.lines = []
        self.max_lines = max_lines

    def update(self, text):
        if text == "\n":
            return

        self.lines.append(f"{self.get_time()} - {text}")
        count = len(self.lines)

        if count > self.max_lines:
            # Remove the first half of the lines to save memory.
            self.lines = self.lines[count // 2 :]

        self.func("\n".join(self.lines))

    @staticmethod
    def get_time() -> str:
        time = datetime.datetime.now()
        return f"{time:%H:%M:%S}"
