#!/bin/sh
rm -rf ../code/bin
rm -rf ../code/develop-eggs
rm -rf ../code/downloads
rm -rf ../code/eggs
rm -rf ../code/include
rm -rf ../code/.installed.cfg
rm -rf ../code/lib
rm -rf ../code/parts

sudo apt-get install haproxy uuid-dev uuid-runtime libevent-dev bzr
sudo apt-get install python2.7-dev swig python-pip libpq-dev
sudo apt-get install libyaml-dev libxml2-dev libxslt1-dev 
sudo pip install --upgrade distribute
sudo pip install --upgrade virtualenv

virtualenv --no-site-packages .
./bin/python bootstrap.py
./bin/buildout
echo OK
