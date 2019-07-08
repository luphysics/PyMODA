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
import sys
import args

# List of subscribers, all of which can handle every exception.
subscribers = []


def init():
    """
    Overrides the system exception hook with our custom hook,
    unless disabled by a commandline argument.
    """
    if not args.debug():
        sys.excepthook = hook


def hook(exc_type, value, traceback):
    """Notifies all subscribers of an exception."""
    notify_subscribers(exc_type, value, traceback)


def subscribe(subscriber):
    subscribers.append(subscriber)


def unsubscribe(subscriber):
    subscribers.remove(subscriber)


def notify_subscribers(exc_type, value, traceback):
    """Notifies all subscribers with the current exception."""
    for s in subscribers:
        s.notify(exc_type, value, traceback)
    print(f"\n\nerrorhandling.py caught exception:\n****HANDLED EXCEPTION****\n{exc_type}\n{value}\n{traceback}")


def system_exception(exc_type, value, traceback):
    """Throws a normal system exception which will crash the program or process."""
    sys.__excepthook__(exc_type, value, traceback)


class ExceptionSubscriber:
    """
    A class which receives information about exceptions when they are raised.
    """

    def __init__(self, on_error):
        """
        :param on_error: a function which takes 3 parameters of the
        form (exc_type, value, traceback)
        """
        self.on_error = on_error

    def notify(self, exc_type, value, traceback):
        """Notifies the subscriber by calling the on_error function."""
        self.on_error(exc_type, value, traceback)
