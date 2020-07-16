<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [User Manual](#user-manual)
  - [Requirements](#requirements)
  - [Installing PyMODA](#installing-pymoda)
  - [Launching PyMODA after installation](#launching-pymoda-after-installation)
  - [General](#general)
  - [Group Coherence](#group-coherence)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Manual

## Requirements

PyMODA is a standalone program, but some of its functionality requires the MATLAB Runtime version 9.6.

## Installing PyMODA 

### Windows 

To install PyMODA, download and run the [setup executable](https://github.com/luphysics/pymoda-install/releases/latest/download/setup-win64.exe). If you see a Windows Smartscreen popup, click "More info", then "Run anyway".

Alternatively, PyMODA can be installed using Microsoft's official [Windows Package Manager](https://github.com/microsoft/winget-cli): 

```
winget install pymoda
```

### macOS

Copy the following command into a terminal, then press enter:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/luphysics/pymoda-install/master/macos/install.sh)"
```

> **Tip:** To open a terminal, press `Cmd`+`Space`, type "terminal" and press enter.

PyMODA will automatically open when the process is complete. 

### Linux 

Copy the following command into a terminal, then press enter:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/luphysics/pymoda-install/master/linux/install.sh)"
```

PyMODA will automatically open when the process is complete. 

> **Tip:** Most terminals require `Ctrl`+`Shift`+`V` instead of `Ctrl`+`V` for pasting.

## Launching PyMODA after installation 

### Windows

On Windows, PyMODA will create a desktop shortcut when it launches for the first time. You can also search for it in the Start menu.

### macOS/Linux

On macOS and Linux, PyMODA adds a command, `pymoda`, to the terminal. You can use this command to launch PyMODA in future.

> **Note:** You may need to restart all open terminals for this to take effect.

## General

This section sets out information which is generally applicable to all or most PyMODA windows. 

### Loading data

PyMODA allows you to load signals using the following file formats:

| File extension | Notes | 
| --- | --- |
| `.csv`, `.txt` | Comma-delimited text file |
| `.mat` | MATLAB data file |
| `.npy` | Numpy data file |

When you open one of the windows from the launcher, you'll be presented with the "load data" dialog.

#### Loading a signal, or multiple signals

> **Note:** This section applies to all windows except Group Coherence.

When you launch a window, the "Select data file" dialog will open:

![Screenshot of the "load data" dialog.](/docs/images/manual/load_data.png)

This dialog provides multiple methods to select data:

- Drag-and-drop the file from the file explorer.
- Browse for the file.
- Select a file which was recently used.

### Saving data

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

## Group Coherence

### Loading data

![Screenshot of the "load data" dialog for group coherence.](/docs/images/manual/load_data_gc.png)

