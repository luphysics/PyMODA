"""
Script which deletes unwanted resources in the 'res' folder to reduce the size
of the packaged executable.
"""
import os
from os.path import join
from pathlib import Path
import sys
import shutil
from typing import List

args = sys.argv[1:]
delete = "-y" in args

if not delete:
    print(
        "Please note, files will not actually be "
        "deleted unless the '-y' argument is used.",
        end="\n\n"
    )

wd = str(Path(os.path.abspath(os.path.dirname(__file__))).parent)
assert wd == os.getcwd(), "Working directory must be the root of the repository."

build_dir = os.path.abspath(os.path.dirname(__file__))
wd = os.getcwd()
res_dir = join(wd, "res")


def load_ignores() -> List[str]:
    out = []

    with open(join(build_dir, ".resignore")) as f:
        for line in f:
            if not line.startswith("#"):
                out.append(line.rstrip("\n"))

    return [i for i in out if i]


ignores = load_ignores()

for pattern in ignores:
    for f in Path(res_dir).rglob(f"{pattern}"):
        print(f"Deleting resource: '{f}'")

        if delete:
            try:
                os.remove(f)
            except:
                shutil.rmtree(f)
