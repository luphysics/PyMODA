#!/bin/bash
set -e 

python3 --version

python3 -m pip install -U pip 
python3 -m pip install PyInstaller

python3 packages/install.py -yv

python3 -m PyInstaller macos.spec --noconfirm

mv dist/PyMODA.app .
hdiutil create -srcfolder PyMODA.app PyMODA.dmg

mkdir -p releases
mv PyMODA.dmg releases/