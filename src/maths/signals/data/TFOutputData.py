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
from numpy import ndarray


class TFOutputData:
    """
    A class which contains the output data from calculations.
    """

    def __init__(
            self,
            times: ndarray,
            values: ndarray,
            ampl: ndarray,
            freq: ndarray,
            powers: ndarray,
            avg_ampl: ndarray,
            avg_pow: ndarray,
            transform: str = "wt",
            overall_coherence: ndarray = None,
            phase_coherence: ndarray = None,
            phase_diff: ndarray = None,
    ):
        self.transform = transform  # The name of the transform (e.g. WT or WFT).
        self.values = values  # The values of the transform (complex numbers).

        # Data plotted in main color mesh in time-frequency common.
        self.times = times
        self.freq = freq
        self.ampl = ampl
        self.powers = powers

        # Data plotted on the RHS of the main color-mesh plot.
        self.avg_ampl = avg_ampl
        self.avg_pow = avg_pow

        # Wavelet phase coherence data.
        self.overall_coherence = overall_coherence
        self.phase_coherence = phase_coherence
        self.phase_diff = phase_diff
        self.surrogate_avg = None

        # Ridge extraction data.
        self.filtered_signal = None
        self.ridge_data = {}

        # Bandpass filter data.
        self.band_data = {}

        # Set to false when the data is invalidated.
        self.valid = True

    def is_valid(self) -> bool:
        """Returns whether the data is valid and should be plotted."""
        return self.valid and len(self.times) > 0 and len(self.freq) > 0 and len(self.ampl) > 0

    def invalidate(self):
        """
        Sets the data to None, which should free up memory when the
        garbage collector runs.
        """
        self.valid = False
        self.times = None
        self.values = None
        self.ampl = None
        self.freq = None
        self.powers = None
        self.avg_ampl = None
        self.avg_pow = None
        self.filtered_signal = None
        self.re_transform = None  # TODO: remove???
        self.ridge_data = {}
        self.band_data = {}

    def has_phase_coherence(self) -> bool:
        return not (self.overall_coherence is None or len(self.freq) != len(self.overall_coherence))

    def has_surrogates(self) -> bool:
        return self.surrogate_avg is not None

    def has_ridge_data(self) -> bool:
        return len(self.ridge_data.keys()) > 0

    def set_ridge_data(self, interval: tuple, filtered, freq, phi):
        self.ridge_data[interval] = (filtered, freq, phi)

    def get_ridge_data(self, interval: tuple) -> tuple:
        data = self.ridge_data.get(interval)
        return data

    def has_band_data(self) -> bool:
        return len(self.band_data.keys()) > 0

    def set_band_data(self, interval: tuple, band, phase, amp):
        self.band_data[interval] = (band, phase, amp,)

    def get_band_data(self, interval: tuple) -> tuple:
        return self.band_data.get(interval)

    @staticmethod
    def empty() -> "TFOutputData":
        """
        Creates an instance of this class with only empty lists as data.
        """
        return TFOutputData(*[[] for _ in range(7)])
