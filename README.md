<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [PyMODA](#pymoda)
  - [Status](#status)
- [User Guide](#user-guide)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Operating systems](#operating-systems)
  - [Downloading PyMODA](#downloading-pymoda)
  - [Preparing to run](#preparing-to-run)
  - [Running PyMODA](#running-pymoda)
  - [Creating a shortcut](#creating-a-shortcut)
  - [Saving data](#saving-data)
  - [Updating PyMODA](#updating-pymoda)
  - [Performance and efficiency](#performance-and-efficiency)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# PyMODA

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3679258.svg)](https://doi.org/10.5281/zenodo.3679258)

PyMODA is a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis). The user interface is written using PyQt5, and the algorithms are mostly packaged as Python libraries from the existing MATLAB code.

PyMODA is cross-platform and does not require any paid software. To get started, see the [User Guide](#user-guide) or the [Developer Guide](docs/developer-guide.md).

## Status

PyMODA plans to offer all the functionality available in MODA, but development is still in progress. This table shows the current status of different features.

| Window    |  Status | Notes | 
| ----      |   ---------        |   ---------   |  
| Time-Frequency Analysis        |  :heavy_check_mark: | |
| Wavelet Phase Coherence        |  :heavy_check_mark:  | Surrogates require further testing | 
| Ridge Extraction and Filtering |  :heavy_check_mark:  | | 
| Wavelet Bispectrum Analysis    |  :heavy_check_mark:  | Surrogates cannot be plotted yet |
| Dynamical Bayesian Inference   |  Implemented | Results are slightly inaccurate |

# User Guide

This guide is aimed at users wishing to set up and run PyMODA. If you're interested in modifying or contributing to the program, you should use the [Developer Guide](docs/developer-guide.md).

> **Tip:** If you experience any problems, check the [Common Issues](docs/common-issues.md) document.

## Requirements

Much of PyMODA's functionality requires the MATLAB Runtime, version 9.6. If you don't have it installed, PyMODA will prompt you to install it when it launches.

## Installation

### Windows

Download the `PyMODA-win64.zip` file from the `Assets` section on the [Releases](https://github.com/luphysics/PyMODA/releases) page.

Extract the .zip file and launch `PyMODA.exe` from the `PyMODA` folder.

### Linux 

Copy the following command into a terminal, then press enter:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/luphysics/PyMODA/master/dist/linux/install.sh)"
```

PyMODA will be downloaded and will automatically open when the process is complete.

> **Note:** Most terminals require `Ctrl`+`Shift`+`V` instead of `Ctrl`+`V` for pasting.

### macOS

Download the `PyMODA-macOS.dmg` file from the `Assets` section on the [Releases](https://github.com/luphysics/PyMODA/releases) page.

You should be able to mount the `.dmg`, then launch `PyMODA.app`.

## Operating systems

PyMODA should run on Windows, macOS and Linux. Linux performs slightly better than Windows ([see comparison](#windows-vs-linux)).

> **Note:** You should ensure that you are familiar with the [core knowledge](docs/core-knowledge.md) before proceeding.

## Downloading PyMODA

PyMODA can be downloaded as a .zip file. 

- [Click here](https://github.com/luphysics/PyMODA/zipball/release) to download the .zip file. 
- Extract the zip file to a desired location.
- For simplicity of instructions, rename the folder to `PyMODA`.

> :warning: Do not place `PyMODA` in a folder which requires admin permissions, such as `C:\Program Files`.

## Preparing to run

When the code is downloaded and Python is installed, you'll need to install the dependencies. 

Open a terminal in the `PyMODA` folder and run `python packages/install.py`. When prompted, you will then need to press the `Enter` key to proceed.

> :warning: For security reasons, do not run this command with elevated permissions.

## Running PyMODA

To start PyMODA, run `python src/main.py` in the `PyMODA` folder.

> **Note:** Linux users also need to specify the path to the MATLAB Runtime using a command-line argument (see [command-line arguments](/docs/developer-guide.md#command-line-arguments)).

## Creating a shortcut

In the launcher window, click "Create shortcut" to create a shortcut to easily open PyMODA. This has different behaviour on different operating systems.

> **Note:** The shortcut will need to be recreated if the path to the PyMODA folder is changed, if the folder is renamed, or if the path to the Python interpreter changes.

#### Windows

A desktop shortcut will be created, which launches PyMODA with the current Python interpreter. If a shortcut already exists, it will be replaced.

#### macOS/Linux

An alias will be created, which adds the terminal command `pymoda` to launch PyMODA with the current Python interpreter. The alias will be added to `~/.bashrc` for Bash, and if Zsh is installed, to `~/.zshrc`. If the alias already exists, it will be replaced.

> **Note:** This will not take effect in currently open shells. Open a new terminal to try it out. 

> **Tip:** If the `-runtime` argument was provided to the instance of PyMODA which created the alias, it does not need to specified when using the `pymoda` command. 

## Saving data

After performing a calculation, the results can be saved using the options under the `Save` item in the menu bar. Results can be saved to `.mat` (MATLAB) and `.npy` (Numpy) files. 

When a data file is opened, it will have the following format:

- In MATLAB: a struct containing a single struct.
- In Python: a dictionary containing a single dictionary.

For each window, the name of the struct/dictionary is as follows:

| Name | Window | 
| --- | --- |
| `TFData` | Time-Frequency Analysis | 
| `DHData` | Detecting Harmonics |
| `PCData` | Wavelet Phase Coherence |
| `GCData` | Group Phase Coherence |
| `REData` | Ridge Extraction and Filtering | 
| `BAData` | Wavelet Bispectrum Analysis | 
| `DBData` | Dynamical Bayesian Inference |

> **Note:** Saving data is not yet implemented for Dynamical Bayesian Inference.

## Updating PyMODA

PyMODA checks for updates occasionally, and shows a message in the launcher window if updates are available. 

![Screenshot demonstrating the launcher window when an update is available.](/docs/images/update_available.png)

> **Tip:** You can press `Ctrl`+`U` to trigger an immediate check for updates. 

### Applying an update

To apply an update automatically, press the "Update now" button and accept the confirmation. A dialog will show the download progress, and PyMODA will automatically re-open after the update is complete. 

> **Note:** If you've made modifications to the code, you should use Git instead of the built-in updater. 

### Rolling back to the previous version

If an update fails to apply or introduces a new problem, the previous version of PyMODA can be restored from `PyMODA/backup`. Just copy all of the files and folders from `PyMODA/backup` and paste them into `PyMODA`, overwriting if applicable.

## Performance and efficiency

### Concurrency

When performing multiple discrete calculations - for example, the wavelet transform of 6 signals - PyMODA uses multiprocessing to greatly increase efficiency by allocating different calculations to different CPU cores.

Therefore, it is more efficient to transform multiple signals if possible. Efficiency will plateau when the number of signals is higher than the number of CPU cores.

#### AMD Ryzen 3700X

The AMD Ryzen 3700X is an 8-core, 16-thread CPU. These tests were run on Manjaro Linux.

| Operation | Total time: individually ("Transform Single" for all) | Total time: simultaneously ("Transform All") | Performance improvement |
| ------------- | ------------- | ------ | ------ |
| WT on 32 signals | 134s | 19.1s | x7.0 |

#### Intel i7-6700

The Intel i7-6700 is a 4-core, 8-thread CPU. These tests were run on KDE neon.

| Operation | Total time: individually ("Transform Single" for all) | Total time: simultaneously ("Transform All") | Performance improvement |
| ------------- | ------------- | ------ | ------ |
| WT on 2 signals | 10s | 5.4s | x1.9 |
| WT on 6 signals | 30s | 8.4s | x3.6 |
| WT on 32 signals | 160s | 43.1s | x3.7 |

### Windows vs Linux

Linux performs slightly better than Windows with a small number of signals, and significantly better with many signals.

#### AMD Ryzen 3700X

| Operating system | Time: WT on 1 signal | Time: WT on 32 signals |
| ---- | ---- | ---- |
| Windows 10 | 4.7s | 33.1s | 
| Manjaro Linux | 4.2s | 19.1s | 

#### Intel i7-6700

| Operating system | Time: WT on 6 signals | Time: WT on 32 signals |
| ---- | ---- | ---- |
| Windows 10 (VM) | 17.5s | 82s | 
| Manjaro Linux (VM) | 17.4s | 74s |
