"""
Python script which automates the task of publishing an update to PyMODA.

Example usage:
- python publish_update.py v0.6.0
- python publish_update.py v0.6.0 --push
"""
import os
import sys
from typing import List

os.chdir(os.path.abspath(os.path.dirname(__file__)))
args = sys.argv

if len(args) <= 1:
    print("Please supply the new version tag as a command-line argument.")
    sys.exit(0)


tag = sys.argv[1]
if not tag.startswith("v"):
    tag = f"v{tag}"

push = any([a in ["push", "--push"] for a in args[1:]])


def replace_version(lines: List[str]) -> List[str]:
    out = []

    for l in lines:
        if not l.startswith("__version__"):
            out.append(l)
        else:
            out.append(f"__version__ = \"{tag.replace('v', '')}\"\n")

    return out


with open("src/main.py", "r") as f:
    lines = f.readlines()

with open("src/main.py", "w") as f:
    f.writelines(replace_version(lines))

# Run twice to ensure that pre-commit hooks are satisfied.
for _ in range(2):
    os.system(f"git add src/main.py")
    os.system(f"git commit -m \"Bump version to {tag}\"")

print(f"Tagging release as '{tag}'.")
os.system(f"git tag {tag}")

if push:
    os.system("git push -u")
    os.system(f"git push origin {tag}")
