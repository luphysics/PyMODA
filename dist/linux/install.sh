echo "Downloading PyMODA. Please wait, this may take over a minute..."
curl -fsSL "https://github.com/luphysics/PyMODA/releases/latest/download/PyMODA-linux_x86_64.tar.gz" -o pymoda.tar.gz

echo "Extracting PyMODA..."
mkdir -p ~/.pymoda
tar -xf pymoda.tar.gz -C ~/.pymoda/

echo "Cleaning up..."
rm pymoda.tar.gz

echo "Launching PyMODA..."
~/.pymoda/PyMODA/PyMODA
