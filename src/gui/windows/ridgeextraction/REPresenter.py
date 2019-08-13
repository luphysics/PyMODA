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
from gui.windows.ridgeextraction.REView import REView
from gui.windows.timefrequency.TFPresenter import TFPresenter
from maths.params.REParams import REParams
from maths.params.TFParams import create

from maths.signals.TFOutputData import TFOutputData
from maths.signals.TimeSeries import TimeSeries


class REPresenter(TFPresenter):
    """
    The presenter in control of the ridge-extraction window.
    """

    def __init__(self, view: REView):
        super(REPresenter, self).__init__(view)

    def calculate(self, calculate_all: bool):
        self.view.set_ridge_filter_disabled(True)
        super(REPresenter, self).calculate(calculate_all)

    def on_all_transforms_completed(self):
        super(REPresenter, self).on_all_transforms_completed()

        self.view.set_ridge_filter_disabled(False)

    def on_ridge_extraction_clicked(self):
        intervals = self.view.get_interval_strings()
        if len(intervals) < 1:
            raise Exception("At least one interval must be specified for ridge extraction.")

        print("Starting ridge extraction...")
        data = [s.output_data for s in self.signals]
        transforms = [d.values for d in data]
        frequencies = data[0].freq

        self.view.switch_to_three_plots()

        self.mp_handler.ridge_extraction(self.get_re_params(),
                                         self.view,
                                         self.on_ridge_completed)

    def on_ridge_completed(self, name, times, freq, values,
                           ampl, powers, avg_ampl, avg_pow,
                           intervals, tfsupp):

        sig = self.signals.get(name)

        d: TFOutputData = sig.output_data
        d.tfsupp = tfsupp
        d.intervals = intervals
        d.transform = values

        d.ampl = ampl
        d.powers = powers

        d.avg_ampl = avg_ampl
        d.avg_pow = avg_pow

        d.freq = freq
        d.times = times

        if all([i.output_data.has_ridge_data() for i in self.signals]):
            self.on_all_ridge_completed()

    def on_all_ridge_completed(self):
        print("All ridge extraction completed.")
        sig = self.get_selected_signal()
        data = sig.output_data

        top, middle, bottom = data.tfsupp
        times = data.times

        self.view.main_plot().plot(times, data.ampl, data.freq)
        self.view.main_plot().plot_line(times, top)
        # self.view.get_re_bottom_plot().plot(times, bottom)

    def on_filter_clicked(self):
        print("Starting filtering...")

    def get_re_params(self) -> REParams:
        intervals = self.view.get_interval_tuples()

        interval = intervals[0]  # TODO: support multiple intervals.
        fmin, fmax = interval

        return create(
            signals=self.signals,
            params_type=REParams,

            fmin=fmin,
            fmax=fmax,
            f0=self.view.get_f0(),
            fstep=self.view.get_fstep(),
            padding=self.view.get_padding(),

            # Only one of these two will be used, depending on the selected transform.
            window=self.view.get_wt_wft_type(),
            wavelet=self.view.get_wt_wft_type(),

            rel_tolerance=self.view.get_rel_tolerance(),
            cut_edges=self.view.get_cut_edges(),
            preprocess=self.view.get_preprocess(),
            transform=self.view.get_transform_type(),
        )
