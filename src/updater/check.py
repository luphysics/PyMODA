#  PyMODA, a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis).
#  Copyright (C) 2020 Lancaster University
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
from typing import List, Tuple

from github import Github
from github.GitRelease import GitRelease

g = Github()


def _tuple_version(version_tag: str) -> Tuple[int, int, int]:
    return tuple([int(v) for v in version_tag.replace("v", "").split(".")])


def is_update_available() -> Tuple[bool, str]:
    import main

    releases = get_releases()

    latest = releases[0]
    return _tuple_version(latest.title) > _tuple_version(main.__version__), latest.title


def get_releases() -> List[GitRelease]:
    repo = g.get_repo("luphysics/PyMODA")

    releases = repo.get_releases()
    return releases
