#!/bin/bash
set -e 

python3 --version

python3 -m pip install -U pip
python3 -m pip install PyInstaller 

python3 packages/install.py -yv

python3 -m PyInstaller main.spec --noconfirm

cd dist
mv main PyMODA

tar -zcf PyMODA-linux_64.tar.gz PyMODA
cd ..

mkdir -p releases
mv dist/PyMODA-linux_64.tar.gz releases/