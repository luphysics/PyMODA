## Introduction

PyMODA is a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis). The user interface is written using PyQt5, and the algorithms are mostly packaged as Python libraries from the existing MATLAB code.

PyMODA is cross-platform and does not require any paid software. To get started, see the [User Guide](#user-guide) or the [Developer Guide](#developer-guide).

### Status

PyMODA does not yet offer all the functionality available in MODA. This table shows the current status of different features.

| Window    |   Functionality   |  MATLAB-packaged library | Python implementation |
| ----      |   ---------       |   ---------   |  ----- |
| Time-Frequency Analysis      |   Wavelet transform    |  Working | Mostly written |
| Time-Frequency Analysis      |   Windowed Fourier transform    |  Working   | Partially written |
| Wavelet Phase Coherence      |   Phase coherence    |  Working  | Some surrogates written, needs testing |
| Ridge Extraction and Filtering     |   Extract ridges    |  Working   | Not implemented |
| Ridge Extraction and Filtering     |   Bandpass filter    |  Not implemented   | Working |
| Wavelet Bispectrum Analysis     |   Bispectrum analysis    |  Partially implemented   | Not implemented |
| Dynamical Bayesian Inference     |   Bayesian inference    |  Not implemented   | Written, not working |

# User Guide

This guide is aimed at users wishing to set up and run PyMODA. If you're interested in modifying or contributing to the program, you should use the [Developer Guide](#developer-guide).

## Requirements
- Python 3.6 or higher.
- [MATLAB Runtime](https://www.mathworks.com/products/compiler/matlab-runtime.html), 
newest version recommended (does not require a licence).

## Operating systems

PyMODA should run on Windows, macOS and Linux. On macOS and Linux, `python` should be replaced with `python3` in all commands below.

## Downloading the code
To download the code, you can [click here](https://github.com/luphysics/PyMODA/zipball/master). Extract the zip file to your desired location; for the sake of easy instructions, the folder should be renamed to `PyMODA`.

## Preparing to run
When the code is downloaded and Python is installed, you'll need to install the dependencies. To do this, open a terminal in the `PyMODA` folder and run the command `python packages/install.py`. This mas require elevated permissions, e.g. "Run as adminstrator" on Windows or `sudo` on macOS/Linux.

To start PyMODA, run `python src/main.py` from the same terminal. Linux users also need to specify the path to the MATLAB Runtime using a command-line argument (see [command-line arguments](#command-line-arguments)).

## Performance and efficiency

When performing multiple discrete calculations - for example, the wavelet transform of 6 signals - PyMODA uses multiprocessing to greatly increase efficiency by allocating 
different calculations to different CPU cores.

Therefore, it is more efficient to transform multiple signals if possible. Efficiency will plateau when the number of signals is higher than the number of CPU cores.

| Operation | CPU cores/threads | Total time: individually ("Transform Single" for all) | Total time: simultaneously ("Transform All") | Performance improvement |
| ------------- | ------------- | ------------- | ------ | ------ |
| WT on 2 signals | i7-6700 (4 cores, 8 threads) | 10s | 5.4s | x1.9 |
| WT on 6 signals | i7-6700 (4 cores, 8 threads) | 30s | 8.4s | x3.6 |
| WT on 32 signals | i7-6700 (4 cores, 8 threads) | 160s | 43.1s | x3.7 |
| WT on 32 signals | Ryzen 3700X (8 cores, 16 threads) | 157s | 34.5s | x4.55 |

Note: the i7-6700 was tested on Linux, while the Ryzen 3700X was running Windows. This causes differences in performance.

## Common issues

This section outlines some common problems and their solutions.

### No module named PyQt5.sip

If you see `ModuleNotFoundError: No module named 'PyQt5.sip'` when running the program, try executing the following commands:
```
# Note: on macOS/Linux, replace "pip" with "pip3".
pip install pyqt5-sip
pip install pyqt5
```

### Could not load the Qt platform plugin "xcb" in "" even though it was found.

This error is caused by conflicts between the MATLAB Runtime's libraries and libraries used by PyQt. The issue is [described in more detail here](https://stackoverflow.com/questions/56758952/matlab-generated-python-packages-conflict-with-pyqt5-on-ubuntu-possible-librar).

This error will occur if you have followed the MATLAB Runtime's instruction to export the `LD_LIBRARY_PATH` in `~/.profile` or `~/.bashrc`. Save the value for later and remove it from `~/.profile` or `~/.bashrc`, then run the command `unset LD_LIBRARY_PATH`. 

Now take the value of the `LD_LIBRARY_PATH` that was exported, and add it as the `-runtime` command-line argument (see [command-line arguments](#command-line-arguments)). 

### qt.qpa.xcb: QXcbConnection: XCB error: 13 (BadGC)

This issue appears to be a bug in the `xcb` plugin which is used when running PyQt on X11. (Switching to Wayland does not seem to be possible due to other unknown issues with the `wayland` plugin, although `xcb` should also run on Wayland.)

This problem only seems to appear when running bispectrum analysis in PyMODA via PyCharm. PyMODA should run from the terminal without issues.

# Developer Guide

This guide is aimed at developers wishing to modify or contribute to the program, and is 
designed to be accessible to programmers with basic to intermediate knowledge of Python.

## Additional requirements
To develop the program, you may need additional tools:
- Git is used to download the code, save and upload your changes.
- Qt Designer is used to edit the layout files.

## Downloading the code
If you are not registered as a collaborator, you should [fork the repository](https://help.github.com/en/articles/fork-a-repo). You can then clone your fork to download the code. To start running the code, see [preparing to run](#preparing-to-run).

## Command-line arguments

PyMODA has several command-line arguments, which can make development easier. Note that `-runtime` *must be used on Linux*,  but should not be necessary on other operating systems.

`-runtime` is used to specify the `LD_LIBRARY_PATH` for the MATLAB Runtime. The `LD_LIBRARY_PATH` is shown by the Runtime installer after installation, and should be saved but not be added to the environment variables manually. 

Here is an example of PyMODA being run on Linux:

```
python3 src/main.py -runtime "/usr/local/MATLAB/MATLAB_Runtime/v96/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v96/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v96/sys/os/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v96/extern/bin/glnxa64"
```

Below is a table listing the other command-line arguments.

| Argument | Use case | Example |
| ------ | ------ | ------- |
| `--no-maximise` | Prevents windows from opening in a maximised state, allowing easier viewing of console output. | `python src/main.py --no-maximise` |
| `--debug` | Disables error handling. | `python src/main.py --debug` | 
| `-freq` | Specifies the sampling frequency to use. This frequency will be automatically selected in dialogs. | `python src/main.py -freq 10` |
| `-file` | Specifies a data file to use. This file will be automatically selected in dialogs. Only designed for data files in the `res/test` folder, and the file name should be prefixed by `test:`. | `python src.main.py -file "test:many_signal.csv"` | 

Command-line arguments can be specified in PyCharm configurations. For example, you can specify `-runtime` in all and/or create a different configuration for each data file.

## Error handling

By default, PyMODA attempts to catch all exceptions on the main process and display them in a dialog instead of crashing the program. This can make finding issues more difficult while developing, so the `--debug` command-line argument can be used or added to PyCharm configurations to prevent this behaviour (this may not be necessary on Windows).

## Project structure

```
PyMODA
│   README.md
|   ...
│
└───packages        # Folder containing the MATLAB-generated Python packages.
│   │   install.py      # Installs the Python packages.
│   │
│   └───WT              # Wavelet transform package.
│   |
|   ...
│
└───res             # Contains resources used by the program.
|   |
|   └───colours         # Contains colourmaps used by the program.
|   |
|   └───img             # Contains images used by the program.
|   |
|   └───layout          # Contains PyQt layout files.
|   |
|   └───test            # Contains example data for testing PyMODA.
|
└───src             # Contains the Python codebase.
    │   main.py         # The entry point of the program.
    |
    └───data            # Contains code related to loading data.
    |
    └───gui             # Contains code related to the GUI.
    |
    └───maths           # Contains code related to numerical calculations.
    |
    └───utils           # Contains utility code used by the program, e.g. error handling.
```

## Naming conventions and code style

PyMODA code should follow the standard guidelines and naming conventions for Python. Code may be formatted with the PyCharm auto-formatter (by default, the shortcut to format a file is `Ctrl`+`Alt`+`L`). 

PyMODA consists of 5 main windows, whose names are abbreviated in the codebase. The abbreviations are as follows:

| Name  | Abbreviation | Example class |
| ------------- | ------------- | ------------- |
| *Time-Frequency* Analysis  | TF | `TFWindow` |
| Wavelet *Phase Coherence* | PC | `PCWindow` |
| *Ridge Extraction* and Filtering  | RE | `REWindow` |
| Wavelet *Bispectrum Analysis*  | BA | `BAWindow` |
| *Dynamical Bayesian* Inference  | DB | `DBWindow` |

## Concurrency

PyMODA uses `multiprocess` and `asyncio`.

### multiprocess

Multiprocessing is necessary for several reasons:
- It allows long calculations to run without freezing the GUI.
- It allows calculations for multiple signals to be executed simultaneously on different CPU cores,
greatly improving performance.
- It allows the circumvention of [a critical issue](https://stackoverflow.com/questions/56758952/matlab-generated-python-packages-conflict-with-pyqt5-on-ubuntu-possible-librar) 
on Linux caused by conflicting libraries used by PyQt5 and the MATLAB Runtime.

While multithreading could be used to solve the first problem, it would not be ideal for 
the second due to CPython's infamous Global Interpreter Lock. The third problem can only be solved by 
using multiple processes.

PyMODA uses the `multiprocess` module rather than the `multiprocessing` module found in 
the standard library, due to problems with the latter's serialization in Windows. 
`multiprocess` has the same API as `multiprocessing`, so the only changes required are the import statements.

### asyncio

`asyncio` allows the `Scheduler` class, which schedules the running of multiple processes, 
to run on the main thread without freezing the GUI. `Scheduler` is run in a coroutine using the Qt event loop from `asyncqt`.

*Note: the readme is unfinished and will be continued.*
