#!/bin/bash

cd /home/foxway
mkdir $HOME/bzr
wget https://launchpad.net/bzr/2.7/2.7.0/+download/bzr-2.7.0.tar.gz
tar -xzvf bzr-2.7.0.tar.gz --strip 1 -C $HOME/bzr/
cd $HOME/bzr
python2.7 setup.py install --home $HOME
