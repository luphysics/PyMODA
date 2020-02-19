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
import asyncio
import os
from typing import Dict, List

import numpy as np
from PyQt5.QtWidgets import QFileDialog
from numpy import ndarray
from scipy.io import savemat

from gui.dialogs.ErrorBox import ErrorBox
from gui.windows.common.BaseTFWindow import BaseTFWindow
from maths.signals.Signals import Signals
from maths.signals.TimeSeries import TimeSeries
from processes.MPHandler import MPHandler
from utils import stdout_redirect, errorhandling
from utils.decorators import deprecated
from utils.settings import Settings
from utils.stdout_redirect import WindowLogger


class BaseTFPresenter:
    """
    A base presenter which handles controlling the window.

    This presenter forms the base of all 5 analysis windows' presenters.
    """

    def __init__(self, view: BaseTFWindow):
        self.view: BaseTFWindow = view
        self.is_plotted: bool = False
        self.plot_ampl: bool = True
        self.tasks_completed: int = 0

        self.signals: Signals = None
        self.selected_signal_name: str = None
        self.open_file: str = None
        self.freq: float = None

        self.mp_handler: MPHandler = None
        self.preproc_mp_handler: MPHandler = None

        self._logger: WindowLogger = stdout_redirect.WindowLogger(self.on_log)
        self._can_save_data: bool = False

        self.settings: Settings = Settings()

        errorhandling.subscribe(self.on_error)
        stdout_redirect.subscribe(self._logger)

        # Will be used to record the parameters passed to the algorithms. This is useful when saving data.
        self.params = None

    def init(self) -> None:
        # Add zoom listener to the signal plotting, which is displayed in the top left.
        self.view.signal_plot().add_zoom_listener(self.on_signal_zoomed)

        # Open dialog to select a data file.
        self.view.select_file()

    def calculate(self, calculate_all: bool) -> None:
        """
        Performs the main calculation. To connect as a slot,
        use functools.partial:

        `button.clicked.connect(partial(self.calculate, my_argument))`
        """
        pass

    def enable_save_data(self, enable: bool) -> None:
        self._can_save_data = enable
        self.view.enable_save_data(enable)

    def on_progress_updated(self, current, total) -> None:
        self.view.update_progress(current, total)

    def on_all_tasks_completed(self) -> None:
        self.tasks_completed = 0

    def on_error(self, exc_type, value, traceback) -> None:
        """Called when an error occurs, provided that the debug argument is not in use."""
        self.cancel_calculate()
        ErrorBox(exc_type, value, traceback)

    def on_log(self, text) -> None:
        """Called when a log should occur; tells view to display message in log pane."""
        self.view.set_log_text(text)

    def on_signal_zoomed(self, rect) -> None:
        """Called when the signal plotting (top left) is zoomed, and sets the x-limits."""
        if rect.is_valid():
            self.view.set_xlimits(rect.x1, rect.x2)
            self.signals.set_xlimits(rect.x1, rect.x2)

    def invalidate_data(self) -> None:
        """
        Sets the current data as invalid, so that it is not plotted
        while a calculation is in progress.
        """
        for d in self.signals:
            d.output_data.invalidate()

    def cancel_calculate(self) -> None:
        """
        Cancels the calculation of the desired transform(s),
        killing their processes immediately.
        """
        if self.mp_handler:
            self.mp_handler.stop()
        self.view.on_calculate_stopped()
        self.is_plotted = False
        self.on_all_tasks_completed()
        print("Calculation terminated.")

    @deprecated
    def on_freq_changed(self, freq) -> None:
        """Called when the frequency is changed."""
        self.freq = float(freq)

    def set_frequency(self, freq: float) -> None:
        """Sets the frequency of the time-series."""
        self.signals.set_frequency(freq)

    def on_file_selected(self, file: str):
        """Sets the name of the data file in use, and loads its data."""
        self.open_file = file
        print(f"Opening {self.open_file}...")
        self.view.update_title()
        self.load_data()

    def load_data(self) -> None:
        pass

    async def coro_get_data_to_save(self) -> Dict:
        """
        Returns a dictionary containing the data that will be saved to a file, based on the current results.
        """
        raise Exception("This function should have been implemented by a subclass.")

    def save_data_mat(self) -> None:
        asyncio.ensure_future(self.coro_save_data_mat())

    async def coro_save_data_mat(self) -> None:
        """
        Saves the current results as a .mat file.
        """
        data = await self.coro_get_data_to_save()
        path = self.get_save_location()

        if not path or not data:
            return

        if not path.endswith(".mat"):
            path += ".mat"

        print("Saving data as .mat file...")
        savemat(path, data)
        print(f"Data saved to {path}.")

    def save_data_npy(self) -> None:
        asyncio.ensure_future(self.coro_save_data_npy())

    async def coro_save_data_npy(self) -> None:
        """
        Saves the current results as a .npy file.
        """
        data = await self.coro_get_data_to_save()
        path = self.get_save_location()

        if path:
            print("Saving data as .npy file...")
            np.save(path, data)
            print(f"Data saved to {path}.")

    def get_save_location(self) -> str:
        """
        Uses a dialog to get the desired save location, and returns the path.

        :return: the file path at which the file should be saved
        """
        start_dir = self.settings.get_save_directory()
        path, filetype = QFileDialog.getSaveFileName(self.view, "Save file", start_dir)

        if path:
            save_dir, _ = os.path.split(path)
            self.settings.set_save_directory(save_dir)

        return path

    def get_window_name(self) -> str:
        """
        Gets the name of this window, adding the currently open file
        if applicable.
        """
        title = self.view.name
        if self.open_file:
            title += f" - {self.open_file}"
        return title

    def on_close(self) -> None:
        """Called when the window closes."""
        self.cancel_calculate()
        errorhandling.unsubscribe(self.on_error)

    def get_params(self):
        pass

    def on_data_loaded(self) -> None:
        pass

    def on_signal_selected(self, item) -> None:
        pass

    def get_selected_signal(self) -> TimeSeries:
        """Returns the currently selected signal as a TimeSeries."""
        return self.signals.get(self.selected_signal_name)

    def plot_preprocessed_signal(self) -> None:
        """
        Plots the preprocessed version of the signal.
        """
        asyncio.ensure_future(self.coro_plot_preprocessed_signal())

    async def coro_plot_preprocessed_signal(self) -> None:
        """
        Coroutine to preprocess the currently selected signal and plot the result.
        """
        sig = self.get_selected_signal()
        result = await self.coro_preprocess_selected_signal()

        if result and result[0] is not None:
            self.view.plot_preprocessed_signal(sig.times, sig.signal, result[0])

    async def coro_preprocess_selected_signal(self) -> List[ndarray]:
        """
        Coroutine to preprocess the currently selected signal.

        :return: the preprocessed signal as a 1D array
        """
        sig = self.get_selected_signal()
        fmin = self.view.get_fmin()
        fmax = self.view.get_fmax()

        if not self.preproc_mp_handler:
            self.preproc_mp_handler = MPHandler()

        return await self.preproc_mp_handler.coro_preprocess(sig, fmin, fmax)

    async def coro_preprocess_all_signals(self) -> List[ndarray]:
        """
        Coroutine to preprocess all signals.

        :return: a list containing the preprocessed signals as a 1D array each
        """
        signals = self.signals
        fmin = self.view.get_fmin()
        fmax = self.view.get_fmax()

        if not self.preproc_mp_handler:
            self.preproc_mp_handler = MPHandler()

        return await self.preproc_mp_handler.coro_preprocess(signals, fmin, fmax)
