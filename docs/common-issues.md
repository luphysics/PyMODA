## Common issues

This section outlines some common problems and their solutions.

### No module named PyQt5.sip

If you see `ModuleNotFoundError: No module named 'PyQt5.sip'` when running the program, try executing the following commands:
```
# Note: on macOS/Linux, replace "pip" with "pip3".
pip install pyqt5-sip
pip install pyqt5
```

### Could not load the Qt platform plugin "xcb" in "" even though it was found.

This error is caused by conflicts between the MATLAB Runtime's libraries and libraries used by PyQt. The issue is [described in more detail here](https://stackoverflow.com/questions/56758952/matlab-generated-python-packages-conflict-with-pyqt5-on-ubuntu-possible-librar).

This error will occur if you have followed the MATLAB Runtime's instruction to export the `LD_LIBRARY_PATH` in `~/.profile` or `~/.bashrc`. Save the value for later and remove it from `~/.profile` or `~/.bashrc`, then run the command `unset LD_LIBRARY_PATH`. 

Now take the value of the `LD_LIBRARY_PATH` that was exported, and add it as the `-runtime` command-line argument (see [command-line arguments](#command-line-arguments)). 

### qt.qpa.xcb: QXcbConnection: XCB error: 13 (BadGC)

This issue appears to be a bug in the `xcb` plugin which is used when running PyQt on X11. (Switching to Wayland does not seem to be possible due to other unknown issues with the `wayland` plugin, although `xcb` should also run on Wayland.)

This problem only seems to appear when running bispectrum analysis in PyMODA via PyCharm. PyMODA should run from the terminal without issues.
