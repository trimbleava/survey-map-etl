#!/bin/bash

# Usage: ./install_python3.8.sh
# Note:  

echo "Entered $0 ...................."
echo

#
# setup for python 3.8 installation
#
echo "installing python3.8 ...................."
sudo apt-add -repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get -y install python3.8 python3.8-venv python3.8-dev
sudo apt-get -y install python3.8-distutils
python3.8 -m pip install --upgrade pip setuptools wheel

# dpkg -S python3.8    # where is installed? /usr/lib
echo
echo "pip version .................... "
pip --version
echo

