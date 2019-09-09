# PyMODA

## Introduction

PyMODA is a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis). 
The user interface is written using PyQt5, and the algorithms are mostly packaged as Python libraries from the existing MATLAB code.

## User's Guide

This guide is aimed at users wishing to set up and run PyMODA. If you're interested in modifying or contributing to the program, you should use the [Developer's Guide](#developers-guide).

#### Requirements
- Python 3.6 or higher.
- [MATLAB Runtime](https://www.mathworks.com/products/compiler/matlab-runtime.html), 
newest version recommended (does not require a licence).

#### Downloading the code
To download the code, you can click the green "Clone and download" button on the top-right of the repository page, and then "Download zip". Extract the zip to your desired location; the folder should be called `PyMODA`.

#### Preparing to run
When the code is downloaded and Python is installed, you'll need to install the dependencies. To do this, open a terminal in the `PyMODA` folder and run the command `pip install -r requirements.txt`.

You'll also need to install the python packages containing the packaged MATLAB code. To do this, open a terminal in the `PyMODA` folder and run the command `python packages/install.py`.

To start PyMODA, run `python src/main.py` from the same terminal.

## Developer's Guide

This guide is aimed at developers wishing to modify or contribute to the program, and is 
designed to be accessible to programmers with basic to intermediate knowledge of Python.

#### Downloading the code
To be able to submit changes to PyMODA, you should [fork the repository](https://help.github.com/en/articles/fork-a-repo). You can then clone your fork to download the code.

#### Multiprocessing

PyMODA uses multiprocessing for several reasons:
- It allows long calculations to run without freezing the GUI.
- It allows calculations for multiple signals to be executed simultaneously on different CPU cores,
greatly improving performance.
- It allows the circumvention of [a critical issue](https://stackoverflow.com/questions/56758952/matlab-generated-python-packages-conflict-with-pyqt5-on-ubuntu-possible-librar) 
on Linux caused by conflicting libraries used by PyQt5 and the 
MATLAB Runtime.

While multithreading could be used to solve the first problem, it would not be ideal for 
the second due to CPython's infamous Global Interpreter Lock. The third problem can only be solved by 
using multiple processes.

PyMODA uses the `multiprocess` module rather than the `multiprocessing` module found in 
the standard library, due to problems with the latter's serialization in Windows. 
`multiprocess` has the same API as `multiprocessing`, so the only changes required are the import statements.
