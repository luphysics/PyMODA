<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [Developer Guide](#developer-guide)
  - [Additional requirements](#additional-requirements)
  - [Downloading the code](#downloading-the-code)
  - [Git workflow](#git-workflow)
  - [Collaborator](#collaborator)
  - [Non-collaborator](#non-collaborator)
  - [Command-line arguments](#command-line-arguments)
  - [Error handling](#error-handling)
  - [Project structure](#project-structure)
  - [Naming conventions and code style](#naming-conventions-and-code-style)
  - [MATLAB packages](#matlab-packages)
  - [Concurrency](#concurrency)
  - [Update system](#update-system)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Developer Guide

This guide is aimed at developers wishing to modify or contribute to the program, and is designed to be accessible to programmers with basic to intermediate knowledge of Python.

> **Tip:** If you experience any difficulties, you can [create an issue on the dedicated page](https://github.com/luphysics/PyMODA/issues/new).

## Additional requirements

Ensure that your system fulfills the [user requirements](/README.md#requirements). 

To develop the program, you may need to install additional tools:
- Git is required to download the code, save and upload your changes.
- Qt Designer is required to edit the layout files.

## Downloading the code

To download the code, see the section below for [collaborators](/docs/developer-guide.md#collaborator) or [non-collaborators](/docs/developer-guide.md#non-collaborator).

> **Note:** To start running the code, see [preparing to run](/README.md#preparing-to-run).

## Git workflow

| Branch name | Purpose | 
| --- | --- |
| `master` | Main branch of the repository. Can accept pull requests. | 
| `staging` | The pre-release branch. All changes should be pushed to `staging` and tested before being merged into `release`. | 
| `release` | The release branch. PyMODA downloads updates from this branch. |

Force-pushes are disabled for the `master` and `release` branches. This protection should not be removed.

**Any commits pushed to `release` will trigger an update for all users, so changes to this branch should be made carefully.**

## Collaborator

If you are registered as a collaborator, you can clone the repository using one of the following commands:

```bash
# SSH method.
git clone git@github.com:luphysics/PyMODA.git

# HTTPS method.
git clone https://github.com/luphysics/PyMODA.git
```

Developers are encouraged to use their own development branches (e.g. `dev` followed by an identifier) for making changes. If working as the main developer on the project, you may merge your branch directly into `master`; otherwise, pull requests are usually a better approach.

> **Tip:** It is safe to rebase parts of your branch which are ahead of `master`, and force-push your branch, before merging into `master`.

## Non-collaborator

If you are not registered as a collaborator, you should [fork the repository](https://help.github.com/en/articles/fork-a-repo). You can then clone your fork to download the code.

When you make changes, you can open a pull request targeting PyMODA's `master` branch. Do not open a pull request targeting the `release` branch.

### Installing Git hooks

Git hooks are used to automatically perform tasks when a commit is made. PyMODA uses `doctoc` to add the table of contents to markdown files, and `black` to format Python files to follow a consistent style.

Commit your current work, if there are changes. Then open a terminal in the `PyMODA` folder and run:

```
pip install pre-commit --user   # Installs the pre-commit tool.
pre-commit install              # Adds the Git hooks to the repository.
```

On Windows, also run `git config core.safecrlf false` in the `PyMODA` folder. This prevents a circular problem where Git cannot commit because it converts line endings to CRLF but `doctoc` converts line endings back to LF.

Now that the Git hooks are installed, they will automatically run every time a commit changes relevant files.

> :warning: When a hook changes a file, you'll need to add the files and commit again.

Here is an example of committing with the hooks installed. Black formats a Python file, so the commit must be run again. (Note that the `-am` flag stages currently tracked, modified, files before committing.)

![Screenshot demonstrating Git hooks.](/docs/images/git_hooks.png)

> **Note:** If absolutely necessary, hooks can be skipped by adding `--no-verify` to the `git commit` command.

> **Tip:** If `pre-commit` is not a valid command after installing, try `python -m pre-commit` instead.

## Command-line arguments

PyMODA has several command-line arguments, which can make development easier.

> :warning: `-runtime` must be used on Linux, but should not be necessary on other operating systems.

`-runtime` is used to specify the `LD_LIBRARY_PATH` for the MATLAB Runtime. The `LD_LIBRARY_PATH` is shown by the Runtime installer after installation, and should be saved but not be added to the environment variables manually. 

Here is an example of PyMODA being run on Linux:

```
python3 src/main.py -runtime "/usr/local/MATLAB/MATLAB_Runtime/v96/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v96/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v96/sys/os/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v96/extern/bin/glnxa64"
```

> **Tip:** You can add command-line arguments like `-runtime` to your PyCharm configuration.

Below is a table listing the other command-line arguments.

| Argument | Use case | Example |
| ------ | ------ | ------- |
| `--no-maximise` | Prevents windows from opening in a maximised state, allowing easier viewing of console output. | `python src/main.py --no-maximise` |
| `--debug` | Disables error handling. | `python src/main.py --debug` | 
| `-freq` | Specifies the sampling frequency to use. This frequency will be automatically selected in dialogs. | `python src/main.py -freq 10` |
| `-file` | Specifies a data file to use. This file will be automatically selected in dialogs. Only designed for data files in the `res/data` folder, and the file name should be prefixed by `data:`. | `python src.main.py -file "data:many_signal.csv"` | 

Command-line arguments can be specified in PyCharm configurations. 

> **Tip:** Create multiple PyCharm configurations with different `-file` and `-freq` args to easily test different datasets. 

## Error handling

By default, PyMODA attempts to catch all exceptions on the main process and display them in a dialog instead of crashing the program. This can make finding issues more difficult while developing, so the `--debug` command-line argument can be used or added to PyCharm configurations to prevent this behaviour (this may not be necessary on Windows).

## Project structure

Many subfolders contain their own README files, describing their contents. When you click on a subfolder in GitHub, the README will be rendered below the file structure.

## Naming conventions and code style

PyMODA code should follow the standard guidelines and naming conventions for Python. To ensure that the codebase uses a similar style, Git hooks will automatically format code with Black when it is committed.

### Window names

PyMODA consists of 5 main windows, whose names are abbreviated in the codebase. The abbreviations are as follows:

| Name  | Abbreviation | Example class |
| ------------- | ------------- | ------------- |
| *Time-Frequency* Analysis  | TF | `TFWindow` |
| Wavelet *Phase Coherence* | PC | `PCWindow` |
| *Ridge Extraction* and Filtering  | RE | `REWindow` |
| Wavelet *Bispectrum Analysis*  | BA | `BAWindow` |
| *Dynamical Bayesian* Inference  | DB | `DBWindow` |

### Type hints

Type hints are used throughout PyMODA. While not required for local variables, they should be used for most function parameters and all return types (including functions which return `None`).

They serve multiple purposes: 

- The intent of a function is much easier to interpret.
- The input parameters and output of a function are much easier to interpret.
- The auto-completion in the IDE is much better. This is especially useful for member variables.

### ViewProperties

All main windows inherit from a `ViewProperties` class. The only purpose of the `ViewProperties` class is to provide the names and types of member variables which will be instantiated when the GUI is created from the `.ui` file, greatly improving the auto-completion in PyCharm.

Since the constructor of a `ViewProperties` is called before the GUI is created, it can safely initialize values to `None`.

```python
class SampleViewProperties(ViewProperties):

  def __init__(self):
    self.btn: QPushButton = None
    self.lbl: QLabel = None
```

### Float and int decorators

When a function returns a value from the GUI, it is necessary to validate the value and convert to the correct type. This is when the `@floaty` decorator is useful; it ensures that a value is returned as a float if it can be interpreted as a float, or `None` if it cannot.

```python
class Window:

  @floaty
  def get_fmin(self) -> Optional[float]:
    """
    Returns the minimum frequency from the GUI as either a float, 
    if it can be interpreted as such, or `None`.
    """
    fmin: str = self.lineedit_fmin.text()
    return fmin # Return as a string; the decorator will take care of the conversion.
```

The `@inty` decorator is identical to the `@floaty` decorator, except it returns an int or `None` instead of a float or `None`.

## MATLAB packages

Using MATLAB's Library Compiler, MATLAB functions can be packaged as Python libraries which use the MATLAB Runtime. Most of the algorithms in PyMODA use MATLAB libraries from MODA.

### Linux support

MATLAB causes a library collision which prevents PyQt from functioning while the `LD_LIBRARY_PATH` environment variable is set according to its documentation. To solve this, MATLAB-packaged code must always be called from a separate process and the process must call the function `setup_matlab_runtime()`, which sets the `LD_LIBRARY_PATH` for the process, *before* importing MATLAB packages. 

> **Note:** The `process` decorator can now be used instead of calling `setup_matlab_runtime()`. See [process](#process).

### Data types

MATLAB can only handle certain Python data types (see [documentation](https://www.mathworks.com/help/matlab/matlab_external/pass-data-to-matlab-from-python.html)). 

Numpy can convert MATLAB arrays to Numpy arrays, but Numpy arrays must be converted to Python lists before being converted to MATLAB arrays with `matlab.double()`. MATLAB arrays should be converted back to Numpy arrays using PyMODA's `matlab_to_numpy()`, which may be faster than `np.asarray()` in some cases. A tuple of MATLAB arrays can be converted to a tuple of Numpy arrays using `multi_matlab_to_numpy()`.

Although MATLAB can convert single complex numbers, it seems unable to convert a list of complex numbers. Instead of passing a list of complex numbers, a list of the real parts and a list of the complex parts can be passed separately as MATLAB arrays and then combined in the MATLAB code. 

> **Note:** `None` cannot be passed to MATLAB.

### Unspecific errors 

Errors referencing `map::at`, lacking any useful context, appear to be caused by MATLAB being unable to convert Python types to MATLAB types or vice versa. Some MODA algorithms were copied and slightly modified to avoid errors when packaged for PyMODA. This is why `bispecWavPython` exists alongside `bispecWavNew` in MODA; the former is packaged as a Python library.

### Function parameters

MATLAB functions can take optional parameters, adding them to the cell array `varargin`. `varargin` must be dealt with manually, but in MATLAB a common approach is to take optional parameters as alternating strings and values. For example, `WT(sig, fs, "fmin", 0.1, "fmax", 5)` is equivalent to `WT(sig, fs, fmin=0.1, fmax=5)` in Python.

To use `varargin`, a Python dictionary is passed to the MATLAB function. Provided that all the keys are strings and the values can be converted to MATLAB types, this will work correctly.

### Performance issues

There is a large performance overhead due to the conversion of Numpy arrays to lists and then the conversion of lists to MATLAB arrays. Additionally, the conversion of the returned data to Numpy arrays is extremely inefficient.

### Implementation

The `maths.algorithms.matlabwrappers` package contains files which form wrappers around the MATLAB code. Since these files import MATLAB functions, they must also not be imported in the main process.

"Params" classes, such as `TFParams`, exist to simplify passing optional parameters to MATLAB functions. Params objects have a `get()` method which returns a dictionary with all the `None` values removed, so that it can safely be passed to MATLAB. 

## Concurrency

### Libraries

PyMODA uses `multiprocess`, `asyncio`, `qasync` and `AsyncProcessScheduler`.

#### multiprocess

Python offers multiprocessing, which allows a program to create multiple processes which operate like independent programs. Data cannot be directly passed between processes, but it is possible to pass data via a `Queue`.

Multiprocessing is used in PyMODA for several reasons:

- Long calculations can run without freezing the GUI.
- Calculations for multiple signals can be executed simultaneously on different CPU cores,
greatly improving performance.
- [A critical issue](https://stackoverflow.com/questions/56758952/matlab-generated-python-packages-conflict-with-pyqt5-on-ubuntu-possible-librar) 
on Linux - caused by conflicting libraries used by PyQt5 and the MATLAB Runtime - can be mitigated.

While multithreading could be used to solve the first problem, it would not be ideal for 
the second due to CPython's infamous Global Interpreter Lock. The third problem can only be solved by 
using multiple processes.

PyMODA uses the `multiprocess` library rather than the standard library's `multiprocessing`, due to problems with the latter's serialization in Windows. `multiprocess` has the same API as `multiprocessing`, so all documentation and tutorials are still directly applicable; the only changes required are the import statements.

> **Note:** `from multiprocess import Process, Queue` is falsely reported as an error in PyCharm.

#### asyncio

`asyncio` is part of the standard library. `asyncio` adds coroutines, which provide the ability to run asynchronous code on the main thread. 

Coroutines shouldn't be used to run intensive code on the main thread, because it will still be blocked. However, they are very useful for lightweight tasks. 

> **Note:** Names of async functions, and functions designed to be used in coroutines, are usually prefixed by `coro_` in PyMODA. 

#### qasync

`qasync` is a library which allows the `asyncio` event loop to be set to a Qt event loop. Coroutines running on this event loop are able to safely interact with the GUI.

#### AsyncProcessScheduler

`AsyncProcessScheduler` is a library which contains the `Scheduler` and `Task` classes. `Scheduler` provides an easy way to execute and receive results from multiple processes, returning results directly in a coroutine instead of using a callback-based system. See the [documentation](https://github.com/CabbageDevelopment/async-process-scheduler) for more details.

### Implementation

Most of PyMODA's concurrency is provided via the `MPHandler` class. Functions which will be run as separate processes are implemented in `maths.algoritms.multiprocessing`, and must be decorated with `@process` from `processes.mp_utils`.

#### @process

`@process` is a simple decorator with 3 purposes:

- It clearly marks a function as the entry-point of a separate process.
- It calls `setup_matlab_runtime()` to prevent errors with `LD_LIBRARY_PATH` on Linux.

Example usage:

```python

def start_process() -> None:
    """Function which starts a process running `long_calculation`."""
    q = Queue()
    process = Process(target=long_calculation, args=(q,))
    ### [Use process.] ### 

@process
def long_calculation(queue: Queue, input: ndarray) -> None:
    ### [Long calculation which produces x, y.] ###
    queue.put((x,y))
```

#### MPHandler

`MPHandler` is an intermediary between GUI code and `Scheduler`. It contains functions which create a Scheduler and use it to run mathematical operations in a coroutine.

> :warning: A reference to an `MPHandler` must be stored in GUI-related code to prevent it from being garbage-collected, and allow the processes to be terminated.

#### Overview

This diagram demonstrates how the GUI code in `TFPresenter`, the class controlling the time-frequency window, interacts with `MPHandler` and `Scheduler`. TFPresenter runs `coro_calculate()` as a coroutine on the main thread, which then waits for the results using `await` and shows them in the GUI.

![Diagram demonstrating how TFPresenter, MPHandler and Scheduler interact.](/docs/images/TFPresenter.png)

## Update system

PyMODA features a built-in updater, which is able to automatically download a new version of PyMODA and replace the old version. 

> **Note:** When the `.git` folder is present in PyMODA's root directory, the updater will not check for updates unless `Ctrl`+`U` is pressed while the launcher window is in focus.

### Checking for updates

To prevent excess work on the part of the developer, PyMODA will automatically detect updates based on changes to the `release` branch of the GitHub repository.

When PyMODA checks for updates, it uses GitHub's API to retrieve the latest commit's hash. If the hash is not the same as the previously recorded hash, the update system reports that an update is available. This ensures that every commit to `release` triggers an update.

> **Note:** On first launch, the latest commit hash is recorded as the previous hash.

### Applying updates

The process of applying an update is as follows:

- PyMODA copies the contents of the `src/updater/` folder to a temporary folder, `temp/`.
- PyMODA launches `temp/update.py` as a new program with the same Python interpreter and command-line arguments. This will be referenced to as *Updater*.
- PyMODA exits.
- *Updater* downloads the PyMODA repository as a .zip file to `temp/`.
- *Updater* extracts the .zip file to a folder inside `temp/`.
- *Updater* deletes the `backup/` folder, then copies the current contents of the `PyMODA` folder (excluding `temp/`) to `backup/`. 
- For each item in the first level of the `PyMODA` folder: if it exists, it is deleted by *Updater*; then the new file/folder is copied from the folder inside `temp/` to its new location.
- *Updater* starts a shell command which will update the packages used by PyMODA using `packages/install.py` and then launch PyMODA with the same Python interpreter and command-line arguments. If the update was judged to be successful, another command-line argument, `--post-update`, is added.
- *Updater* exits, leaving the shell command running.
- After the packages are updated, PyMODA launches. If the `--post-update` argument is present, PyMODA removes the `temp/` folder and records the latest commit hash from GitHub. The `--post-update` argument is then removed from `sys.argv`.

> **Note:** All paths specified in this section are relative to PyMODA's root directory.

### Modifying the update system

***Take care when modifying the update system***, because if a bug is introduced:

- Users will be stranded on a broken version of the program, which will be **unable to apply the fixes which are required**.
- Problems will not be noticed until the new version of the program attempts to update, i.e. until the first change after the broken release.
- Depending on the bug, users may not be made aware that updates are failing; this may lead to confusing feedback about bugs which have been fixed.

**Changing the name of relevant files/folders such as `updater` and `update.py` will break the update system.** If name changes are necessary, ensure that all references to names in the code are searched for and changed.

> **Note:** Any file/folder changes outside `src/updater` should be completely safe.

When testing changes to the update system, remember that a successful update will replace the new code with the older code from the GitHub repository. This means that *changes made to the post-update behaviour will not occur when testing an update*, but can be verified by supplying the `--post-update` argument manually.

To test a full update, it is recommended to copy the PyMODA folder to a temporary location; then delete its `.git` folder, launch PyMODA from the new location and apply an update.