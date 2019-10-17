<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [Core knowledge](#core-knowledge)
  - [Opening a terminal](#opening-a-terminal)
  - [Administrator/elevated terminal](#administratorelevated-terminal)
  - [Changing directory](#changing-directory)
  - [Opening a terminal in a specific folder](#opening-a-terminal-in-a-specific-folder)
  - [Using Python from the terminal](#using-python-from-the-terminal)
  - [Using pip from the terminal](#using-pip-from-the-terminal)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Core knowledge

This document contains core knowledge which you should be familiar with before starting to set up PyMODA. 

---

## Opening a terminal

### Windows

On Windows 10, press `Win`+`X` to open the menu over the start button. Then press `I` to open Powershell. 

On older versions of Windows, press `Win`+`R`, type `powershell` and press enter. If this doesn't work, use `cmd` instead of `powershell`.

> Note: You can use either Cmd or Powershell, but Powershell is the default in recent versions of Windows 10. Powershell is preferred, since it is more powerful and user-friendly.

### macOS

Press `Cmd`+`Space` to open Spotlight, then search for "terminal" and press `Enter`.

### Linux

This varies between distributions, but `Ctrl`+`Alt`+`T` is a common shortcut to open a terminal.

---

## Administrator/elevated terminal

Some tasks, such as installing Python packages, may require you to run a command with elevated or administrator privileges.

### Windows

On Windows 10, press `Win`+`X` to open the menu over the start button. Then press `A` to open an administrator Powershell. Any command executed in this window will run with elevated permissions.

On previous versions of Windows, search for Powershell, right-click on it and click "Run as administrator". If Powershell is not available, replace with Command Prompt.

### macOS/Linux

macOS and Linux have a different permissions system to Windows. Instead of opening a new terminal, simply prefix every command with `sudo`.

```
# Needs elevated permissions.
pip3 install numpy   

# Fixed: now runs with elevated permissions. 
sudo pip3 install numpy
```

---

## Changing directory

The terminal always has a working directory. Unless you provide a relative or absolute path to a file, the file can only be accessed when inside the terminal's working directory. The working directory is displayed to the left of the cursor.

To change your working directory, use the `cd` command followed by the relative or absolute path to the target directory. 

> Tip: On most operating systems, you can easily get the path to a folder in the file explorer by pressing `Ctrl`+`L`, then copying the text. You can then paste this after the `cd` command to go to that directory.

> :warning: Avoid paths with spaces, if possible. However, you can include quotes around folder names with spaces, e.g. `cd "python/Test folder"`.

> Tip: Press `Tab` while typing to autocomplete folder and file names.

### Example - Windows

Assume that PyMODA is stored in a `python` folder inside `Documents`. To change directory to PyMODA, the command would be `cd Documents/python/PyMODA` from the default working directory.

From any working directory, the command `cd C:/Users/test/Documents/python/PyMODA`, for a user with username `test`, would also work.

### Example - macOS/Linux

Assume that PyMODA is stored in a `python` folder inside the home directory. To change directory to PyMODA, the command would be `cd python/PyMODA` from the default working directory.

From any working directory, the command cd `~/python/PyMODA` would also work.

> Note: `~` corresponds to the home directory on macOS/Linux.

---

## Opening a terminal in a specific folder

It can often be easier to open a terminal in a specific folder instead of changing directory.

### Windows

In file explorer, ensure that nothing is selected and then `Shift`+`Right-click` on an empty area of the folder. Click `Open Powershell here` in the context menu.

> Note: an elevated terminal cannot be opened in a specific folder. `cd` must be used.

### macOS

macOS does not implement this functionality. You must open a terminal and `cd` to the target directory.

### Linux

This varies between distributions, but the same system as Windows is common.

---

## Using Python from the terminal

Python can be run from the terminal, and should be accessible in any working directory.

> :warning: When following the docs, always substitude `python` with the appropriate command for your system.

### Windows

`python` is the terminal command used to run Python. Try running `python --version` to check the version.

> Note: If this causes an error, check the [Common Issues](/docs/common-issues.md) document.

### macOS/Linux

The command for Python 3.x is usually `python3`, while `python` refers to Python 2. You can check by running `python --version` and `python3 --version`.

Some Linux distributions have a version of `python3` which is too old to meet the requirements. In this case, you may need to install a newer version; for example, on Ubuntu you can use the [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) to install newer Python versions. 

If you've installed a newer Python version, it will have a specific command such as `python3.8`. Use it instead of `python3`.

---

## Using pip from the terminal

`pip` is the Python package manager. It handles downloading and installing Python libraries from PyPI, the Python Package Index.

> Note: The `pip` associated with a Python installation can always be accessed using `{python executable} -m pip`, e.g. `python3 -m pip`.

> :warning: When following the docs, always substitude `pip` with the appropriate command for your system.

### Windows

`pip` is the correct terminal command. If `pip` does not work, try `python -m pip`.

### macOS/Linux

On most systems, `pip3` is the `pip` associated with `python3`. If `pip3` does not work, use `python3 -m pip` instead.

