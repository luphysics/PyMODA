## Common Issues

This document outlines some common problems and their solutions.

---

### ImportError: DLL load failed: The specified module could not be found.

#### Problem

`ImportError: DLL load failed: The specified module could not be found.` when launching PyMODA. This is an error when importing scipy.io on Windows with Python 3.7. 

#### Solution

Uninstalling Python 3.7 and installing Python 3.6 appears to fix the issue. Python 3.8 may also solve the problem when scipy adds support for it.

---

### No module named PyQt5.sip

#### Problem

`ModuleNotFoundError: No module named 'PyQt5.sip'` when launching PyMODA. 

#### Solution

```
# Note: on macOS/Linux, replace "pip" with "pip3".
pip install pyqt5-sip
pip install pyqt5
```

---

### Could not load the Qt platform plugin "xcb" in "" even though it was found.

#### Problem 

This error is caused by conflicts between the MATLAB Runtime's libraries and libraries used by PyQt. The issue is [described in more detail here](https://stackoverflow.com/questions/56758952/matlab-generated-python-packages-conflict-with-pyqt5-on-ubuntu-possible-librar).

This error will occur if you have followed the MATLAB Runtime installer's instruction to export the `LD_LIBRARY_PATH` in `~/.profile` or `~/.bashrc`. 

#### Solution 

Save the value of `LD_LIBRARY_PATH` for later and remove it from `~/.profile` or `~/.bashrc`, then run the command `unset LD_LIBRARY_PATH`. 

Now take the value of the `LD_LIBRARY_PATH` that was exported, and add it as the `-runtime` command-line argument (see [command-line arguments](#command-line-arguments)). 

---

### qt.qpa.xcb: QXcbConnection: XCB error: 13 (BadGC)

#### Problem

This issue appears to be a bug in the `xcb` plugin which is used when running PyQt on Linux with the X11 display server. (Switching to Wayland does not seem to be possible due to issues loading the `wayland` plugin, although the `xcb` plugin also runs on Wayland with the same errors.)

#### Solution

This problem usually seems to appear when running bispectrum analysis in PyMODA via PyCharm. PyMODA normally runs from the terminal without issues.
