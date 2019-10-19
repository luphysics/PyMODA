<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [Developer Guide](#developer-guide)
  - [Additional requirements](#additional-requirements)
  - [Downloading the code](#downloading-the-code)
  - [Installing Git hooks](#installing-git-hooks)
  - [Command-line arguments](#command-line-arguments)
  - [Error handling](#error-handling)
  - [Project structure](#project-structure)
  - [Naming conventions and code style](#naming-conventions-and-code-style)
  - [Concurrency](#concurrency)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Developer Guide

This guide is aimed at developers wishing to modify or contribute to the program, and is designed to be accessible to programmers with basic to intermediate knowledge of Python.

## Additional requirements
To develop the program, you may need to install additional tools:
- Git is required to download the code, save and upload your changes.
- Qt Designer is required to edit the layout files.

## Downloading the code
If you are not registered as a collaborator, you should [fork the repository](https://help.github.com/en/articles/fork-a-repo). You can then clone your fork to download the code. 

To start running the code, see [preparing to run](/README.md#preparing-to-run).

## Installing Git hooks

Git hooks are used to automatically perform tasks when a commit is made. PyMODA uses `doctoc` to add the table of contents to markdown files, and `black` to format Python files to follow a consistent style.

Commit your current work, if there are changes. Then open a terminal in the `PyMODA` folder and run:

```
pip install pre-commit --user   # Installs the pre-commit tool.
pre-commit install              # Adds the Git hooks to the repository.
```

On Windows, also run `git config core.safecrlf false` in the `PyMODA` folder. This prevents a circular problem where Git cannot commit because it converts line endings to CRLF but doctoc converts line endings back to LF.

Now that the Git hooks are installed, they will automatically run every time a commit changes relevant files.

> :warning: When a hook changes a file, you'll need to add the files and commit again.

Here is an example of committing with the hooks installed. Black formats a Python file, so the commit must be run again.

![Screenshot demonstrating Git hooks.](/docs/images/git_hooks.png)

## Command-line arguments

PyMODA has several command-line arguments, which can make development easier.

> :warning: `-runtime` must be used on Linux, but should not be necessary on other operating systems.

`-runtime` is used to specify the `LD_LIBRARY_PATH` for the MATLAB Runtime. The `LD_LIBRARY_PATH` is shown by the Runtime installer after installation, and should be saved but not be added to the environment variables manually. 

Here is an example of PyMODA being run on Linux:

```
python3 src/main.py -runtime "/usr/local/MATLAB/MATLAB_Runtime/v96/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v96/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v96/sys/os/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v96/extern/bin/glnxa64"
```

> Tip: You can add command-line arguments like `-runtime` to your PyCharm configuration.

Below is a table listing the other command-line arguments.

| Argument | Use case | Example |
| ------ | ------ | ------- |
| `--no-maximise` | Prevents windows from opening in a maximised state, allowing easier viewing of console output. | `python src/main.py --no-maximise` |
| `--debug` | Disables error handling. | `python src/main.py --debug` | 
| `-freq` | Specifies the sampling frequency to use. This frequency will be automatically selected in dialogs. | `python src/main.py -freq 10` |
| `-file` | Specifies a data file to use. This file will be automatically selected in dialogs. Only designed for data files in the `res/data` folder, and the file name should be prefixed by `data:`. | `python src.main.py -file "data:many_signal.csv"` | 

Command-line arguments can be specified in PyCharm configurations. 

> Tip: Create multiple PyCharm configurations with different `-file` and `-freq` args to easily test different datasets. 

## Error handling

By default, PyMODA attempts to catch all exceptions on the main process and display them in a dialog instead of crashing the program. This can make finding issues more difficult while developing, so the `--debug` command-line argument can be used or added to PyCharm configurations to prevent this behaviour (this may not be necessary on Windows).

## Project structure

Many subfolders contain their own README files, describing their contents. When you click on a subfolder, GitHub will render the README below the file structure.

## Naming conventions and code style

PyMODA code should follow the standard guidelines and naming conventions for Python. To ensure that the codebase uses a similar style, Git hooks will automatically format code when it is committed.

PyMODA consists of 5 main windows, whose names are abbreviated in the codebase. The abbreviations are as follows:

| Name  | Abbreviation | Example class |
| ------------- | ------------- | ------------- |
| *Time-Frequency* Analysis  | TF | `TFWindow` |
| Wavelet *Phase Coherence* | PC | `PCWindow` |
| *Ridge Extraction* and Filtering  | RE | `REWindow` |
| Wavelet *Bispectrum Analysis*  | BA | `BAWindow` |
| *Dynamical Bayesian* Inference  | DB | `DBWindow` |

## Concurrency

### Libraries

PyMODA uses `multiprocess` and `asyncio`.

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

> Note: `from multiprocess import Process, Queue` is falsely reported as an error in PyCharm.

#### asyncio

`asyncio` is part of the standard library. `asyncio` adds coroutines, which provide the ability to run asynchronous code on the main thread. 

Coroutines shouldn't be used to run intensive code on the main thread, because it will still be blocked. However, they are very useful for lightweight tasks. 

> Note: Names of async functions, and functions designed to be used in coroutines, are usually prefixed by `coro_` in PyMODA. 

#### asyncqt

`asyncqt` is a library which allows the `asyncio` event loop to be set to a Qt event loop. Coroutines running on this event loop are able to safely interact with the GUI.

### Implementation

PyMODA's concurrency is centred around the `Scheduler`, `Task` and `MPHandler` classes. 

#### Task

`Task` is a simple class which contains a process and a queue. The queue should have been passed to the process when it was instantiated, and the process should put data in the queue instead of returning it. 

Task is able to determine whether it has finished by checking if the queue is empty.

#### Scheduler

`Scheduler` provides an abstract way to execute and receive results from multiple processes. A key feature of `Scheduler` is that it can return results from `Task` objects directly in a coroutine, which greatly simplifies the data flow over a callback-based design. 

A `Scheduler` instance contains a list of `Task` objects, and when started it will handle scheduling the tasks to run efficiently based on CPU core count and CPU usage. A scheduler is started by calling the async function `coro_run()`, which schedules all tasks until complete and then returns the results as a list of tuples. Each tuple in the list corresponds to the result of one task. 

> Note: `coro_run()` now returns ordered results; i.e. the `i`-th item in the returned list will be the result of the `i`-th task added to the Scheduler.

![Diagram demonstrating how Scheduler operates.](/docs/images/scheduler.png)

Below is a simplified code sample demonstrating the basic usage of the Scheduler class. Points to note:

- For simplicity, the code sample makes no reference to PyQt. The `MyWindow` class is not actually a window.
- In PyMODA, code in the window class should not be responsible for handling calculations. This is the presenter's job.
- In PyMODA, the presenter doesn't directly interact with `Scheduler`; it uses `MPHandler`.
- For `asyncio` to work in PyQt, the event loop must be set in the application. This only needs to be done once in the program's lifecycle, and it is already implemented in `Application.py`.

```
class MyWindow:

    def do_calculation(self):
        """
        Starts the coroutine to perform the calculation.
        """
        asyncio.ensure_future(self.coro_calculate())

    async def coro_calculate(self):
        """
        Performs the calculation and plots the result.
        """
        # Store to prevent garbage collection.
        self.scheduler = Scheduler(self.on_progress)

        num_tasks = 16  # The number of processes to run.

        # Generate some random data to supply to the processes.
        inputs = [random.randint(2, 7) for _ in range(num_tasks)]

        for i in range(num_tasks):
            queue = Queue()

            # Tuple containing the arguments which are passed to the process.
            _args = (queue, inputs[i])

            process = Process(target=long_function, args=_args)
            self.scheduler.add_task(Task(process, queue))

        # Now we can start the scheduler and wait for the results without blocking the main thread.
        data: List[tuple] = await self.scheduler.coro_run()

        # Note: `data` is a list containing one tuple from each process.

        # The result from the first process.
        first_result = data[0]
        x, y, status = first_result

        self.plot(x, y) # Plot the result in the GUI. 

    def on_progress(self, num_completed: int, num_total: int):
        """
        This function takes the number of tasks completed 
        and the total number of tasks being run. 
        
        Pretend that it is used to update a progress bar.
        """

    def plot(self, x, y):
        """
        Pretend that this function plots the results.
        """

def long_function(queue: Queue, n: int):
    """
    Function which simulates a long-running calculation.

    This function will be called in another process.
    """
    # Pretend that this is a long, useful calculation.
    time.sleep(n + 1)

    # Pretend that this is a useful result of the calculation.
    x, y, status = 4, 8, "success"
    
    # Instead of returning values, add them to the queue.
    queue.put((
        x,
        y,
        status,
    ))

if __name__ == "__main__":
    window = MyWindow()
    window.do_calculation()
```

#### MPHandler

`MPHandler` is an intermediary between GUI code and `Scheduler`. It contains functions which create a Scheduler and use it to run mathematical operations in a coroutine.

> Note: A reference to an `MPHandler` must be stored in GUI-related code to prevent it from being garbage-collected, and allow the processes to be terminated.

#### Overview

This diagram demonstrates how the GUI code in `TFPresenter`, the class controlling the time-frequency window, interacts with `MPHandler` and `Scheduler`.

![Diagram demonstrating how TFPresenter, MPHandler and Scheduler interact.](/docs/images/multiprocessing.png)
