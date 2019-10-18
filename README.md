<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [Introduction](#introduction)
  - [Status](#status)
- [User Guide](#user-guide)
  - [Requirements](#requirements)
  - [Operating systems](#operating-systems)
  - [Downloading the code](#downloading-the-code)
  - [Preparing to run](#preparing-to-run)
  - [Running PyMODA](#running-pymoda)
  - [Creating a shortcut](#creating-a-shortcut)
  - [Performance and efficiency](#performance-and-efficiency)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Introduction

PyMODA is a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis). The user interface is written using PyQt5, and the algorithms are mostly packaged as Python libraries from the existing MATLAB code.

PyMODA is cross-platform and does not require any paid software. To get started, see the [User Guide](#user-guide) or the [Developer Guide](docs/developer-guide.md).

## Status

PyMODA does not yet offer all the functionality available in MODA. This table shows the current status of different features.

| Window    |   Functionality   |  MATLAB-packaged library | Python implementation |
| ----      |   ---------       |   ---------   |  ----- |
| Time-Frequency Analysis      |   Wavelet transform    |  :heavy_check_mark: | Mostly written |
| Time-Frequency Analysis      |   Windowed Fourier transform    |  :heavy_check_mark:   | Partially written |
| Wavelet Phase Coherence      |   Phase coherence    |  :heavy_check_mark:  | Some surrogates written, needs testing |
| Ridge Extraction and Filtering     |   Extract ridges    |  :heavy_check_mark:  | Not implemented |
| Ridge Extraction and Filtering     |   Bandpass filter    |  Not implemented   | :heavy_check_mark: |
| Wavelet Bispectrum Analysis     |   Bispectrum analysis    |  :heavy_check_mark:  | Not implemented |
| Dynamical Bayesian Inference     |   Bayesian inference    |  Not implemented   | Written, not working |

# User Guide

This guide is aimed at users wishing to set up and run PyMODA. If you're interested in modifying or contributing to the program, you should use the [Developer Guide](docs/developer-guide.md).

> Tip: If you experience any problems, check the [Common Issues](docs/common-issues.md) document.

## Requirements

- Python 3.6 or higher.
- [MATLAB Runtime](https://www.mathworks.com/products/compiler/matlab-runtime.html), 
version R2019a (9.6). A license is not required.

> :warning: Do not use a newer version of the MATLAB Runtime.

> Note: The Microsoft Store release of Python is incompatible with PyMODA due to the permissions on its folders.

## Operating systems

PyMODA should run on Windows, macOS and Linux. Linux performs slightly better than Windows ([see comparison](#windows-vs-linux)).

> :warning: You should ensure that you are familiar with the [core knowledge](docs/core-knowledge.md) before proceeding.

## Downloading the code

There are two methods to download the code: as a zip file, or by cloning the repository with Git. The advantage of cloning with Git is that you can easily update PyMODA by running `git pull` in the terminal, preserving any added files such as shortcuts, instead of downloading a new zip file.

If you prefer the zip method:

- [Click here](https://github.com/luphysics/PyMODA/zipball/master) to download the .zip file. 
- Extract the zip file to a desired location.
- For simplicity of instructions, rename the folder to `PyMODA`.

If you prefer the Git method:

- [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
- Open a terminal in a desired folder and run `git clone https://github.com/luphysics/PyMODA.git`.
- The code will download as a folder named `PyMODA`.
- Whenever you want to update, open a terminal in `PyMODA` and run `git pull`.

## Preparing to run

When the code is downloaded and Python is installed, you'll need to install the dependencies. Run the command `python packages/install.py` with elevated permissions in the `PyMODA` folder.

> Tip: To diagnose any problems, the `-v` command-line argument can be used to print console output.

## Running PyMODA

To start PyMODA, run `python src/main.py` in the PyMODA folder.

> :warning: Linux users also need to specify the path to the MATLAB Runtime using a command-line argument (see [command-line arguments](/docs/developer-guide.md#command-line-arguments)).

## Creating a shortcut

In the launcher window, click "Create shortcut" to create a shortcut to easily open PyMODA. This has different behaviour on different operating systems:

> :warning: The shortcut will need to be recreated if the path to the PyMODA folder is changed, if the folder is renamed, or if the path to the Python interpreter changes.

#### Windows

A desktop shortcut will be created, which launches PyMODA with the current Python interpreter. If it exists, it will be replaced.

#### macOS/Linux

An alias will be created, which adds the terminal command `pymoda` to launch PyMODA with the current Python interpreter. The alias will be added to `~/.bashrc` for Bash, and if Zsh is installed, to `~/.zshrc`. If the alias already exists, it will be replaced.

> Note: This will not take effect in currently open shells. Open a new terminal to try it out. 

> Tip: If the `-runtime` argument was provided to the instance of PyMODA which created the alias, it does not need to specified when using the `pymoda` command. 

## Performance and efficiency

When performing multiple discrete calculations - for example, the wavelet transform of 6 signals - PyMODA uses multiprocessing to greatly increase efficiency by allocating different calculations to different CPU cores.

Therefore, it is more efficient to transform multiple signals if possible. Efficiency will plateau when the number of signals is higher than the number of CPU cores.

| Operation | CPU cores/threads | Total time: individually ("Transform Single" for all) | Total time: simultaneously ("Transform All") | Performance improvement |
| ------------- | ------------- | ------------- | ------ | ------ |
| WT on 2 signals | i7-6700 (4 cores, 8 threads) | 10s | 5.4s | x1.9 |
| WT on 6 signals | i7-6700 (4 cores, 8 threads) | 30s | 8.4s | x3.6 |
| WT on 32 signals | i7-6700 (4 cores, 8 threads) | 160s | 43.1s | x3.7 |
| WT on 32 signals | Ryzen 3700X (8 cores, 16 threads) | 157s | 34.5s | x4.55 |

> Note: the i7-6700 was tested on Linux, while the Ryzen 3700X was running Windows. This causes differences in performance.

### Windows vs Linux

Linux performs similarly to Windows with 6 signals, but significantly better with 32 signals.

| Operation | Time (Windows) | Time (Linux) | 
| -----     | -----     | -----     |
| WT on 6 signals | 17.5s | 17.4s | 
| WT on 32 signals | 82s | 74s | 

> Note: These tests were performed with a Windows 10 virtual machine and a Manjaro Linux virtual machine. Both were running in Virtualbox with 4 cores and 14GB of memory allocated, on a physical system with an i7-6700.