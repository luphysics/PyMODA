#!/bin/bash
set -e 

python3 --version

python3 -m pip install -U pip 
python3 -m pip install PyInstaller

python3 packages/install.py -yv

python3 -m PyInstaller macos.spec --noconfirm

hdiutil create -srcfolder dist/PyMODA.app PyMODA.dmg