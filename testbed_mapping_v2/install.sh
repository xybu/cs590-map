#!/bin/bash

sudo apt install python3-tk libcgraph6 graphviz-dev graphviz python-dev python3-dev
wget -O- https://bootstrap.pypa.io/get-pip.py | sudo python3
pip3 install -r requirements.txt

# Install METIS from source.
cd /tmp
wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz
tar xvf metis-5.1.0.tar.gz
cd metis-5.1.0
make config shared=1
make -j`nproc`
sudo make install
sudo ldconfig
