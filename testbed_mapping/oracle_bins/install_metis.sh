#!/bin/bash

cd metis-5.1.0
make config shared=1
make -j2
sudo make install

# Install Python binding of METIS also.
sudo pip3 install metis
