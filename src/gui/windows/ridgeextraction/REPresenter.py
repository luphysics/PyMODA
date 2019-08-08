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
from gui.windows.timefrequency.TFPresenter import TFPresenter
from maths.algorithms.REParams import REParams
from maths.algorithms.TFParams import create
from utils.cache import Cache


class REPresenter(TFPresenter):
    """
    The presenter in control of the ridge-extraction window.
    """

    def calculate(self, calculate_all: bool):
        self.view.set_ridge_filter_disabled(True)
        super(REPresenter, self).calculate(calculate_all)

    def on_all_transforms_completed(self):
        super(REPresenter, self).on_all_transforms_completed()

        self.view.set_ridge_filter_disabled(False)

    def on_ridge_extraction_clicked(self):
        intervals = self.view.get_intervals()
        if len(intervals) < 1:
            raise Exception("At least one interval must be specified for ridge extraction.")

        print("Starting ridge extraction...")
        data = [s.output_data for s in self.signals]
        transforms = [d.values for d in data]
        frequencies = data[0].freq

        file = Cache().save_data(
            {"cached_wt": transforms, "cached_freq": frequencies}
        )

        self.mp_handler.ridge_extraction(len(transforms),
                                         None,
                                         self.signals.frequency,
                                         self.get_re_params(file),
                                         self.view,
                                         self.on_ridge_completed)

    def on_ridge_completed(self):
        pass

    def on_filter_clicked(self):
        print("Starting filtering...")

    def get_re_params(self, cache_file) -> REParams:
        return create(
            signals=self.signals,
            params_type=REParams,
            cache_file=cache_file,
        )
