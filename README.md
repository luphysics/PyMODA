# PyMODA

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3679258.svg)](https://doi.org/10.5281/zenodo.3679258)
[![License: GPL](https://img.shields.io/badge/License-GPLv3-10b515.svg)](https://github.com/luphysics/PyMODA/blob/master/LICENSE)

PyMODA is a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis). The user interface is written using PyQt5, and the algorithms are imported from [PyMODAlib](https://github.com/luphysics/PyMODAlib). PyMODA is packaged as a standalone program using PyInstaller.

PyMODA is cross-platform and does not require any paid software. To get started, please see the [User Guide](#user-guide) or the [Developer Guide](docs/developer-guide.md).

## Status

PyMODA plans to offer all the functionality available in MODA, but development is still in progress. This table shows the current status of different features.

| Window    |  Status | Works without MATLAB Runtime | Notes | 
| ----      |   ---------  | ------- |   ---------   |  
| Time-Frequency Analysis        |  :heavy_check_mark: | :heavy_check_mark: | |
| Detecting Harmonics        |  :heavy_check_mark: | :heavy_check_mark: | |
| Wavelet Phase Coherence        |  :heavy_check_mark: | Required for surrogates only | Surrogates not perfected | 
| Group Phase Coherence        |  :heavy_check_mark:  | :heavy_check_mark: | | 
| Ridge Extraction and Filtering |  :heavy_check_mark: | No | | 
| Wavelet Bispectrum Analysis    |  :heavy_check_mark: | No | |
| Dynamical Bayesian Inference   |  Partially implemented | :heavy_check_mark: | Algorithm not perfected |

# User Guide

This guide is aimed at users wishing to set up and run PyMODA. If you're interested in modifying or contributing to the program, you should use the [Developer Guide](docs/developer-guide.md).

## Requirements

Some of PyMODA's functionality requires the MATLAB Runtime, version 9.6. If you don't have it installed, you'll still be able to use the functionality which doesn't depend on it.

## Installation

### Windows

To install PyMODA, download and run the [setup executable](https://github.com/luphysics/pymoda-install/releases/latest/download/setup-win64.exe). If you see a Windows Smartscreen popup, click "More info", then "Run anyway".

If you prefer, you can automate the entire download and installation process using this Powershell command:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; 
iex ((New-Object System.Net.WebClient).DownloadString(
'https://raw.githubusercontent.com/luphysics/pymoda-install/master/windows/install.ps1'
))
```

### Linux 

Copy the following command into a terminal, then press enter:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/luphysics/pymoda-install/master/linux/install.sh)"
```

PyMODA will automatically open when the process is complete. 

> **Tip:** Most terminals require `Ctrl`+`Shift`+`V` instead of `Ctrl`+`V` for pasting.

### macOS

Copy the following command into a terminal, then press enter:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/luphysics/pymoda-install/master/macos/install.sh)"
```

> **Tip:** To open a terminal, press `Cmd`+`Space`, type "terminal" and press enter.

PyMODA will automatically open when the process is complete. 

## Launching PyMODA after installation 

### Windows

On Windows, PyMODA will create a desktop shortcut when it launches for the first time. You can also search for it in the Start menu.

### macOS/Linux

On macOS and Linux, PyMODA adds a command, `pymoda`, to the terminal. You can use this command to launch PyMODA in future.

> **Note:** You may need to restart all open terminals for this to take effect.

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
