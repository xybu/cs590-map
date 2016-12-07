#!/bin/bash

sudo apt install python3-tk libcgraph6 graphviz-dev graphviz python-dev python3-dev
wget -O- https://bootstrap.pypa.io/get-pip.py | sudo python3
sudo pip3 install networkx
sudo pip3 install matplotlib
sudo pip3 install git+https://github.com/pygraphviz/pygraphviz.git
