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
      - [Windows](#windows)
      - [macOS/Linux](#macoslinux)
  - [Running PyMODA](#running-pymoda)
  - [Creating a shortcut](#creating-a-shortcut)
      - [Windows](#windows-1)
      - [macOS/Linux](#macoslinux-1)
  - [Performance and efficiency](#performance-and-efficiency)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

PyMODA is a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis). The user interface is written using PyQt5, and the algorithms are mostly packaged as Python libraries from the existing MATLAB code.

PyMODA is cross-platform and does not require any paid software. To get started, see the [User Guide](#user-guide) or the [Developer Guide](docs/developer-guide.md).

### Status

PyMODA does not yet offer all the functionality available in MODA. This table shows the current status of different features.

| Window    |   Functionality   |  MATLAB-packaged library | Python implementation |
| ----      |   ---------       |   ---------   |  ----- |
| Time-Frequency Analysis      |   Wavelet transform    |  Working :heavy_check_mark: | Mostly written |
| Time-Frequency Analysis      |   Windowed Fourier transform    |  Working :heavy_check_mark:   | Partially written |
| Wavelet Phase Coherence      |   Phase coherence    |  Working :heavy_check_mark:  | Some surrogates written, needs testing |
| Ridge Extraction and Filtering     |   Extract ridges    |  Working :heavy_check_mark:  | Not implemented |
| Ridge Extraction and Filtering     |   Bandpass filter    |  Not implemented   | Working :heavy_check_mark: |
| Wavelet Bispectrum Analysis     |   Bispectrum analysis    |  Working :heavy_check_mark:  | Not implemented |
| Dynamical Bayesian Inference     |   Bayesian inference    |  Not implemented   | Written, not working |

# User Guide

This guide is aimed at users wishing to set up and run PyMODA. If you're interested in modifying or contributing to the program, you should use the [Developer Guide](docs/developer-guide.md).

> Tip: If you experience any problems, check the [Common Issues](docs/common-issues.md) document.

## Requirements
- Python 3.6 or higher.
- [MATLAB Runtime](https://www.mathworks.com/products/compiler/matlab-runtime.html), 
newest version recommended (does not require a licence).

## Operating systems

PyMODA should run on Windows, macOS and Linux. 

> :warning: On macOS and Linux, `python` should be replaced with the appropriate command - usually `python3` - in all commands below.

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

When the code is downloaded and Python is installed, you'll need to install the dependencies. 

#### Windows

Open an administrator terminal in the `PyMODA` folder, and run the command `python packages/install.py`.

#### macOS/Linux

Open a terminal in the `PyMODA` folder. Run the command `sudo python3 packages/install.py`.

> :warning: When using a particular Python version, the python command/path must be added as a command-line argument. For example, 
run `sudo python3.7 packages/install.py python3.7` to install dependencies for `python3.7`.

## Running PyMODA

To start PyMODA, run `python src/main.py` from the same terminal.

> :warning: Linux users also need to specify the path to the MATLAB Runtime using a command-line argument (see [command-line arguments](docs/developer-guide.md#command-line-arguments)).

## Creating a shortcut

In the launcher window, press "Create shortcut" to create a shortcut to easily open PyMODA. This has different behaviour on different operating systems:

#### Windows

A desktop shortcut will be created, which launches PyMODA with the current Python interpreter.

> :warning: The shortcut will need to be recreated if the path to the PyMODA folder is changed, if the folder is renamed, or if the path to the Python interpreter changes.

#### macOS/Linux

An alias will be created, which adds the terminal command `pymoda` to launch PyMODA. The alias will be added to `~/.bashrc` for Bash, and if Zsh is installed, to `~/.zshrc`.

> Note: This will not take effect in currently open shells. Open a new terminal to try it out. 

> Tip: The `-runtime` argument does not need to be specified when using the `pymoda` command, as long as it was provided to the instance of PyMODA which created the alias. 

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

> Note: the i7-6700 was tested on Linux, while the Ryzen 3700X was running Windows. This causes differences in performance.