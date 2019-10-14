<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [packages](#packages)
  - [install.py](#installpy)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## packages

The `packages` folder contains the MATLAB-packaged Python libraries used by PyMODA.

### install.py

`install.py` is a Python script which installs the Python packages from this folder, and uses pip to install the 
requirements from `requirements.txt` in the root folder.

To specify a particular Python version to use, add it as a command-line argument. For example, `sudo python3 install.py python3.7` will install the packages with `python3.7` even if `python3` is Python 3.6.