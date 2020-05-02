#!/bin/bash
set -e 

sudo add-apt-repository ppa:deadsnakes/ppa -y

sudo apt-get update
sudo apt-get install python3.7 python3.7-dev -y
sudo apt-get install python3-pip -y

python3.7 --version

python3.7 -m pip install -U pip
python3.7 -m pip install -U setuptools wheel 
python3.7 -m pip install -U PyInstaller 

python3.7 packages/install.py -y
python3.7 -m pip install -U Pillow

python3.7 -m PyInstaller main.spec --noconfirm

cd dist
mv main PyMODA

tar -zcf PyMODA-linux_x86_64.tar.gz PyMODA
cd ..

mkdir -p releases
mv dist/PyMODA-linux_x86_64.tar.gz releases/