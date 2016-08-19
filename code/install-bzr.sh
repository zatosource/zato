#!/bin/bash

cd $HOME
mkdir $HOME/bzr
wget https://launchpad.net/bzr/2.7/2.7.0/+download/bzr-2.7.0.tar.gz
tar -xzvf bzr-2.7.0.tar.gz --strip 1 -C $HOME/bzr/
cd $HOME/bzr
$HOME/opt/zato/2.0.7/bin/python2.7 setup.py install --home $HOME
