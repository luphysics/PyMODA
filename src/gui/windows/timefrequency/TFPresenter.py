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
from typing import Union, Dict, List, Optional

import numpy as np
from PyQt5.QtWidgets import QListWidgetItem

from gui.dialogs.FrequencyDialog import FrequencyDialog
from gui.plotting.plots.Rect import Rect
from gui.windows.common.BaseTFPresenter import BaseTFPresenter
from maths.params.TFParams import TFParams, _wt, _wft, create
from maths.signals.Signals import Signals
from maths.signals.data.TFOutputData import TFOutputData
from processes.MPHandler import MPHandler
from utils.decorators import override
from utils.dict_utils import sanitise


class TFPresenter(BaseTFPresenter):
    """
    The presenter in control of the time-frequency window.
    """

    def __init__(self, view):
        super(TFPresenter, self).__init__(view)

        from gui.windows.timefrequency import TFWindow

        self.view: TFWindow = view
        self.is_calculating_all = True

    def calculate(self, calculate_all: bool) -> None:
        """
        Calculates the desired transform(s), and plots the result.
        """
        # If WFT parameters are incorrect, show error.
        if not self.view.get_fmin() and not self.view.is_wavelet_transform_selected():
            return self.view.show_wft_error()

        asyncio.ensure_future(self.coro_calculate(calculate_all))
        print("Started calculation...")

    async def coro_calculate(self, calc_all: bool) -> None:
        """
        Coroutine to calculate all results.
        """
        self.is_calculating_all = calc_all

        self.mp_handler = MPHandler()
        self.mp_handler.stop()

        params = self.get_params(all_signals=calc_all)
        if params.transform == _wft:
            if self.view.get_fmin() is None:
                raise Exception("Minimum frequency must be defined for WFT.")

        self.params = params

        self.is_plotted = False
        self.view.main_plot().clear()
        self.view.main_plot().set_in_progress(True)
        self.invalidate_data()

        log: bool = (params.transform == _wt)
        self.view.main_plot().set_log_scale(logarithmic=log)
        self.view.amplitude_plot().set_log_scale(logarithmic=log)

        self.view.on_calculate_started()

        all_data = await self.mp_handler.coro_transform(
            params, self.on_progress_updated
        )

        for d in all_data:
            self.on_transform_completed(*d)

    def on_transform_completed(
        self, name, times, freq, values, ampl, powers, avg_ampl, avg_pow, opt=None
    ) -> None:
        """
        Called when the calculation of the desired transform(s) is completed.
        """
        self.view.on_calculate_stopped()

        # Get the returned minimum frequency, because otherwise it is unknown if not specified in the GUI.
        if opt:
            self.params.set_item("fmin", opt.get("fmin"))

        t = self.signals.get(name)
        t.output_data = TFOutputData(
            times, values, ampl, freq, powers, avg_ampl, avg_pow
        )

        print(f"Finished calculation for '{name}'.")

        # Plot result if all signals finished.
        if self.all_transforms_completed():
            self.on_all_transforms_completed()

    def all_transforms_completed(self) -> bool:
        """Returns whether all transforms have been completed."""
        return all([s.output_data.is_valid() for s in self.signals_calc])

    def on_all_transforms_completed(self) -> None:
        """Called when all transforms have been completed."""
        self.enable_save_data(True)
        self.plot_output()
        self.on_all_tasks_completed()

    @override
    def get_data_to_save(self) -> Optional[Dict]:
        """
        Gets all the data which will be saved in a file, and returns it as a dictionary.

        :return: a dictionary containing the current results
        """
        if not self.params:
            return None

        output_data: List[TFOutputData] = [s.output_data for s in self.signals]
        cols = len(output_data)

        first = [d for d in output_data if d.is_valid()][0]

        amp = np.empty((*first.ampl.shape, cols))
        avg_amp = np.empty((first.avg_ampl.shape[0], cols))

        freq = first.freq
        time = first.times
        preproc = []  # TODO: Save this and other params

        for index, d in enumerate(output_data):
            if d.is_valid():
                avg_amp[:, index] = d.avg_ampl[:]
                amp[:, :, index] = d.ampl[:]
            else:
                avg_amp[:, index] = np.NAN
                amp[:, :, index] = np.NAN

        tfr_data = {
            "amplitude": amp,
            "avg_amplitude": avg_amp,
            "frequency": freq,
            "time": time,
            "preprocessed_signals": preproc,
            **self.params.items_to_save(),
        }
        return {"TFData": sanitise(tfr_data)}

    def get_values_to_plot(self, amplitude=None) -> tuple:
        """
        Returns the data needed to plotting the transform.
        :param amplitude: overrides the normal value of whether to plotting amplitude instead of power
        :return: the times, frequencies, amplitudes/powers, and average amplitudes/powers
        """
        amp: bool = self.plot_ampl
        if amplitude is not None:
            amp = amplitude

        tf_data = self.get_selected_signal().output_data
        if not tf_data.is_valid():
            return None, None, None, None

        if amp:  # Plot amplitudes.
            values = tf_data.ampl
            avg_values = tf_data.avg_ampl
        else:  # Plot powers.
            values = tf_data.powers
            avg_values = tf_data.avg_pow

        return tf_data.times, tf_data.freq, values, avg_values

    def set_plot_type(self, amplitude_selected=True) -> None:
        """
        Set the type of plot to display (power or amplitude). This affects
        the main plot and the amplitude plot.

        :param amplitude_selected: whether to set the plot type as amplitude (not power)
        """
        self.plot_ampl = amplitude_selected
        if self.is_plotted:
            t, f, values, avg_values = self.get_values_to_plot()
            self.plot(t, f, values, avg_values)

    def plot(self, times, freq, values, avg_values) -> None:
        self.view.main_plot().plot(times, values, freq)
        self.view.amplitude_plot().plot(avg_values, freq)

    def plot_output(self) -> None:
        """
        Plots the output of the WT/WFT calculations for the currently selected signal.
        """
        t, f, values, avg_values = self.get_values_to_plot()

        if t is not None and f is not None:
            self.plot(t, f, values, avg_values)
            self.is_plotted = True
        else:
            self.view.main_plot().clear()
            self.view.amplitude_plot().clear()

    def get_params(self, all_signals=True) -> TFParams:
        """
        Creates the parameters to use when performing the calculations.
        """
        if all_signals:
            self.signals_calc = self.signals
        else:
            self.signals_calc = self.signals.only(self.selected_signal_name)

        return create(
            params_type=TFParams,
            signals=self.signals_calc,
            fmin=self.view.get_fmin(),
            fmax=self.view.get_fmax(),
            f0=self.view.get_f0(),
            # Only one of these two will be used, depending on the selected transform.
            window=self.view.get_wt_wft_type(),
            wavelet=self.view.get_wt_wft_type(),
            cut_edges=self.view.get_cut_edges(),
            preprocess=self.view.get_preprocess(),
            transform=self.view.get_transform_type(),
        )

    def load_data(self) -> None:
        self.signals = Signals.from_file(self.open_file)

        if not self.signals.has_frequency():
            freq = FrequencyDialog().run_and_get()

            if freq:
                self.set_frequency(freq)
                self.on_data_loaded()

    def plot_signal(self) -> None:
        """Plots the signal on the SignalPlot."""
        self.view.plot_signal(self.get_selected_signal())

    def on_data_loaded(self) -> None:
        """Called when the time-series data has been loaded."""
        self.view.update_signal_listview(self.signals.names())
        self.plot_signal()

    def on_signal_zoomed(self, rect: Rect) -> None:
        """
        Override callback to also plot the preprocessed version of
        the x-limited signal instead of the whole signal.

        :param rect: the rectangle which has been zoomed to
        """
        super().on_signal_zoomed(rect)
        self.plot_preprocessed_signal()

    def on_signal_selected(self, item: Union[QListWidgetItem, str]) -> None:
        """
        Called when a signal is selected in the QListWidget.
        Plots the new signal in the top-left plotting and, if
        transform data is available, plots the transform and
        amplitude/power in the main plots.
        """
        if isinstance(item, QListWidgetItem):
            name = item.text()
        else:
            name = item

        self.signals.reset()
        if name != self.selected_signal_name:
            print(f"Selected signal: '{name}'")
            self.selected_signal_name = name
            self.plot_signal()
            self.view.on_xlim_edited()
            self.plot_output()

            self.plot_preprocessed_signal()
