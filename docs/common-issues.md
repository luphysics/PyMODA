<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [Common Issues](#common-issues)
  - ["SyntaxError: invalid syntax"](#syntaxerror-invalid-syntax)
    - [Problem](#problem)
    - [Solution](#solution)
  - ["ImportError: DLL load failed: The specified module could not be found."](#importerror-dll-load-failed-the-specified-module-could-not-be-found)
    - [Problem](#problem-1)
    - [Solution](#solution-1)
  - ["No module named PyQt5.sip"](#no-module-named-pyqt5sip)
    - [Problem](#problem-2)
    - [Solution](#solution-2)
  - ["Could not load the Qt platform plugin "xcb" in "" even though it was found."](#could-not-load-the-qt-platform-plugin-xcb-in--even-though-it-was-found)
    - [Problem](#problem-3)
    - [Solution](#solution-3)
  - ["qt.qpa.xcb: QXcbConnection: XCB error: 13 (BadGC)"](#qtqpaxcb-qxcbconnection-xcb-error-13-badgc)
    - [Problem](#problem-4)
    - [Solution](#solution-4)
  - [Windows: desktop shortcut does not work](#windows-desktop-shortcut-does-not-work)
    - [Problem](#problem-5)
    - [Solution](#solution-5)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Common Issues

This document outlines some common problems and their solutions.

---

### "SyntaxError: invalid syntax"

#### Problem

```
  File "PyMODA/src/main.py", line 28
    Application(sys.argv).exec()
                             ^
SyntaxError: invalid syntax
```

#### Solution

You may be using Python 2.7 accidentally. On many macOS/Linux systems, `python` is Python 2.7 whereas `python3` is Python 3.x; you can check by running `python --version` and `python3 --version`. If this is the case, repeat all previous commands using `python3` instead of `python` and `pip3` or `python3 -m pip` instead of `pip`.

### "ImportError: DLL load failed: The specified module could not be found."

#### Problem

`ImportError: DLL load failed: The specified module could not be found.` when launching PyMODA. This is an error when importing scipy.io on Windows with Python 3.7. 

#### Solution

Uninstalling Python 3.7 and installing Python 3.6 appears to fix the issue. Python 3.8 may also solve the problem when numpy/scipy add support for it.

---

### "No module named PyQt5.sip"

#### Problem

`ModuleNotFoundError: No module named 'PyQt5.sip'` when launching PyMODA. 

#### Solution

```
# Note: on macOS/Linux, replace "pip" with "pip3".
pip install pyqt5-sip
pip install pyqt5
```

---

### "Could not load the Qt platform plugin "xcb" in "" even though it was found."

#### Problem 

This error is caused by conflicts between the MATLAB Runtime's libraries and libraries used by PyQt. The issue is [described in more detail here](https://stackoverflow.com/questions/56758952/matlab-generated-python-packages-conflict-with-pyqt5-on-ubuntu-possible-librar).

This error will occur if you have followed the MATLAB Runtime installer's instruction to export the `LD_LIBRARY_PATH` in `~/.profile` or `~/.bashrc`. 

#### Solution 

Save the value of `LD_LIBRARY_PATH` for later and remove it from `~/.profile` or `~/.bashrc`, then run the command `unset LD_LIBRARY_PATH`. 

Now take the value of the `LD_LIBRARY_PATH` that was exported, and add it as the `-runtime` command-line argument (see [command-line arguments](#command-line-arguments)). 

---

### "qt.qpa.xcb: QXcbConnection: XCB error: 13 (BadGC)"

#### Problem

This issue appears to be a bug in the `xcb` plugin which is used when running PyQt on Linux with the X11 display server. (Switching to Wayland does not seem to be possible due to issues loading the `wayland` plugin, although the `xcb` plugin also runs on Wayland with the same errors.)

#### Solution

This problem usually seems to appear when running bispectrum analysis in PyMODA via PyCharm. PyMODA normally runs from the terminal without issues.

---

### Windows: desktop shortcut does not work

#### Problem

Clicking the desktop shortcut has no effect, or opens a black terminal window for a split-second. This is probably due to the path to the Python interpreter or the PyMODA folder being changed (e.g. if Python is updated or PyMODA or one of its parent folders is renamed). If the path to the Python interpreter or PyMODA contains spaces, this may also cause issues.

You may be able to diagnose other issues by selecting the shortcut, pressing `Alt`+`Enter`, copying the `Target` field and running it in a terminal. 

#### Solution

If the problem is due to the path to the Python interpreter or the PyMODA folder being changed, launching PyMODA manually and creating the shortcut again should fix the issue.

--- 