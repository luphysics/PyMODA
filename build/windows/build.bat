@echo off

"%PYTHON%\python.exe" -m pip install -U setuptools wheel
"%PYTHON%\python.exe" -m pip install -U PyInstaller

"%PYTHON%\python.exe" packages\install.py -y
"%PYTHON%\python.exe" build\strip_resources.py -y

"%PYTHON%\python.exe" -m PyInstaller main.spec --noconfirm

cd dist
move main PyMODA

7z a -r PyMODA-win64.zip PyMODA
cd ..

mkdir releases
move dist\PyMODA-win64.zip releases\