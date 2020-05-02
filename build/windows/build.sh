set -e 

python -m pip install -U pip
python -m pip install setuptools wheel
python -m pip install PyInstaller

python packages/install.py -y

python -m PyInstaller main.spec --noconfirm

cd dist
mv main PyMODA

7z a -r PyMODA-win64.zip PyMODA
cd ..

mkdir -p releases
mv dist/PyMODA-win64.zip releases/