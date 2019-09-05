# PyMODA

## Introduction

PyMODA is a Python implementation of MODA (Multiscale Oscillatory Dynamics Analysis). 
The user interface is written using PyQt5, and the algorithms are mostly packaged as Python libraries from the existing MATLAB code.

## Getting Started

Requirements:
- Python 3.6 or higher.
- MATLAB Runtime (does not require a licence).

## Developer's Guide

This guide is aimed at developers wishing to modify or contribute to the program, and is 
designed to be accessible to programmers with relatively basic knowledge of Python.

#### Multiprocessing

PyMODA uses multiprocessing for several reasons:
- It allows long calculations to run without freezing the GUI.
- It allows calculations for multiple signals to be executed simultaneously on different CPU cores,
greatly improving performance.
- It allows the circumvention of [a critical issue](https://stackoverflow.com/questions/56758952/matlab-generated-python-packages-conflict-with-pyqt5-on-ubuntu-possible-librar) 
on Linux caused by conflicting libraries used by PyQt5 and the 
MATLAB Runtime.

While multithreading could be used to solve the first problem, it would not be ideal for 
the second due to CPython's infamous Global Interpreter Lock. The third problem can only be solved by 
using multiple processes.

PyMODA uses the `multiprocess` module rather than the `multiprocessing` module found in 
the standard library, due to problems with the latter's serialization in Windows. 
`multiprocess` has the same API as `multiprocessing`.