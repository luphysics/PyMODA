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
import sys


class StdOut:

    def write(self, text):
        sys_out.write(text)  # Output text as normal.
        for s in subscribers:  # Notify subscribers.
            if isinstance(s, WindowLogger):
                s.update(text)
            else:
                s(text)

    def flush(self):
        return


subscribers = []

out = StdOut()
sys_out = sys.__stdout__


def init():
    sys.stdout = out


def subscribe(subscriber):
    subscribers.append(subscriber)


def unsubscribe(subscriber):
    subscribers.remove(subscriber)


class WindowLogger:

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
            self.lines = self.lines[count // 2:]

        self.func("\n".join(self.lines))

    def get_time(self) -> str:
        time = datetime.datetime.now()
        return f"{time:%H:%M:%S}"
