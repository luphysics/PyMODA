# PyMODA

## Introduction

PyMODA is a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis). 
The user interface is written using PyQt5, and the algorithms are mostly packaged as Python libraries from the existing MATLAB code.

## User's Guide

This guide is aimed at users wishing to set up and run PyMODA. If you're interested in modifying or contributing to the program, you should use the [Developer's Guide](#developers-guide).

### Requirements
- Python 3.6 or higher.
- [MATLAB Runtime](https://www.mathworks.com/products/compiler/matlab-runtime.html), 
newest version recommended (does not require a licence).

### Downloading the code
To download the code, you can click the green "Clone and download" button on the top-right of the repository page, and then "Download zip". Extract the zip to your desired location; for the sake of easy instructions, the folder should be called `PyMODA`.

### Preparing to run
When the code is downloaded and Python is installed, you'll need to install the dependencies. To do this, open a terminal in the `PyMODA` folder and run the command `python packages/install.py`.

To start PyMODA, run `python src/main.py` from the same terminal.

### Performance and efficiency

When performing multiple discrete calculations - for example, the wavelet transform of 6 signals - PyMODA uses multiprocessing to greatly increase efficiency by allocating 
different calculations to different CPU cores.

Therefore, it is more efficient to transform multiple signals if possible. Efficiency will plateau when the number of signals is higher than the number of CPU cores.

| Operation | CPU cores/threads | Total time: individually ("Transform Single" for all) | Total time: simultaneously ("Transform All") | Performance improvement |
| ------------- | ------------- | ------------- | ------ | ------ |
| WT on 2 signals | i7-6700 (4 cores, 8 threads) | 10s | 5.4s | x1.9 |
| WT on 6 signals | i7-6700 (4 cores, 8 threads) | 30s | 8.4s | x3.6 |
| WT on 32 signals | i7-6700 (4 cores, 8 threads) | 160s | 43.1s | x3.7 |
| WT on 32 signals | Ryzen 3700X (8 cores, 16 threads) | 157s | 34.5s | x4.55 |

Note: the i7-6700 was tested on Linux, while the Ryzen 3700X was running Windows. There may be differences in performance.

## Developer's Guide

This guide is aimed at developers wishing to modify or contribute to the program, and is 
designed to be accessible to programmers with basic to intermediate knowledge of Python.

### Downloading the code
To be able to submit changes to PyMODA, you should [fork the repository](https://help.github.com/en/articles/fork-a-repo). You can then clone your fork to download the code.

### Project structure

```
PyMODA
│   README.md
|   ...
│
└───packages                # Folder containing the MATLAB-generated Python packages.
│   │   install.py          # Installs the Python packages.
│   │
│   └───WT                  # Wavelet transform package.
│   |
|   ...
│
└───res                     # Contains resources used by the program.
|   |
|   └───colours             # Contains colourmaps used by the program.
|   |
|   └───img                 # Contains images used by the program.
|   |
|   └───layout              # Contains PyQt layout files.
|   |
|   └───test                # Contains example data for testing PyMODA.
|
└───src                     # Contains the Python codebase.
    │   main.py             # The entry point of the program.
    |
    └───data                # Contains code related to loading data.
    |
    └───gui                 # Contains code related to the GUI.
    |
    └───maths               # Contains code related to numerical calculations.
    |
    └───utils               # Contains utility code used by the program, e.g. error handling.
```

### Naming conventions and code style

PyMODA code should follow the standard guidelines and naming conventions for Python. Code may be formatted with the PyCharm auto-formatter (by default, the shortcut to format a file is `Ctrl`+`Alt`+`L` while the file is selected but no part is highlighted). 

PyMODA consists of 5 windows, whose names are be abbreviated in the codebase. The abbreviations are as follows:

| Name  | Abbreviation | Example class |
| ------------- | ------------- | ------------- |
| *Time-Frequency* Analysis  | TF | `TFWindow` |
| Wavelet *Phase Coherence* | PC | `PCWindow` |
| *Ridge Extraction* and Filtering  | RE | `REWindow` |
| Wavelet *Bispectrum Analysis*  | BA | `BAWindow` |
| *Dynamical Bayesian* Inference  | DB | `DBWindow` |

### Concurrency

PyMODA uses `multiprocess` and `asyncio`.

#### multiprocess

Multiprocessing is necessary for several reasons:
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

#### asyncio

`asyncio` allows the `Scheduler` class, which schedules the running of multiple processes, 
to run on the main thread without freezing the GUI. `Scheduler` is run in a coroutine using the Qt event loop from `asyncqt`.