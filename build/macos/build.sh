#!/bin/bash
set -e 

python3 --version

python3 -m pip install -U pip 
python3 -m pip install PyInstaller

python3 packages/install.py -yv
python3 build/strip_resources.py -y

python3 -m PyInstaller macos.spec --noconfirm

mv dist/PyMODA.app .

tar -zcf PyMODA-macOS.tar.gz PyMODA.app

mkdir -p releases
mv PyMODA-macOS.tar.gz releases/
