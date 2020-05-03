<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [Performance and efficiency](#performance-and-efficiency)
  - [Concurrency](#concurrency)
  - [Windows vs Linux](#windows-vs-linux)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Performance and efficiency

## Concurrency

When performing multiple discrete calculations - for example, the wavelet transform of 6 signals - PyMODA uses multiprocessing to greatly increase efficiency by allocating different calculations to different CPU cores.

Therefore, it is more efficient to transform multiple signals if possible. Efficiency will plateau when the number of signals is higher than the number of CPU cores.

### AMD Ryzen 3700X

The AMD Ryzen 3700X is an 8-core, 16-thread CPU. These tests were run on Manjaro Linux.

| Operation | Total time: individually ("Transform Single" for all) | Total time: simultaneously ("Transform All") | Performance improvement |
| ------------- | ------------- | ------ | ------ |
| WT on 32 signals | 134s | 19.1s | x7.0 |

### Intel i7-6700

The Intel i7-6700 is a 4-core, 8-thread CPU. These tests were run on KDE neon.

| Operation | Total time: individually ("Transform Single" for all) | Total time: simultaneously ("Transform All") | Performance improvement |
| ------------- | ------------- | ------ | ------ |
| WT on 2 signals | 10s | 5.4s | x1.9 |
| WT on 6 signals | 30s | 8.4s | x3.6 |
| WT on 32 signals | 160s | 43.1s | x3.7 |

## Windows vs Linux

Linux performs slightly better than Windows with a small number of signals, and significantly better with many signals.

### AMD Ryzen 3700X

| Operating system | Time: WT on 1 signal | Time: WT on 32 signals |
| ---- | ---- | ---- |
| Windows 10 | 4.7s | 33.1s | 
| Manjaro Linux | 4.2s | 19.1s | 

### Intel i7-6700

| Operating system | Time: WT on 6 signals | Time: WT on 32 signals |
| ---- | ---- | ---- |
| Windows 10 (VM) | 17.5s | 82s | 
| Manjaro Linux (VM) | 17.4s | 74s |
