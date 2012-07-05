#!/bin/sh

mkdir ../code/eggs
python ./add_egglinks.py

exit 1

rm -rf ../code/bin
rm -rf ../code/develop-eggs
rm -rf ../code/downloads
rm -rf ../code/eggs
rm -rf ../code/include
rm -rf ../code/.installed.cfg
rm -rf ../code/lib
rm -rf ../code/parts

sudo apt-get install haproxy uuid-dev uuid-runtime libevent-dev bzr
sudo apt-get install python2.7-dev swig python-pip libpq-dev python-zdaemon
sudo apt-get install libyaml-dev libxml2-dev libxslt1-dev
sudo apt-get install libatlas-dev libblas3gf libatlas3gf-base libumfpack5.4.0
sudo apt-get install liblapack-dev libgfortran3 liblapack3gf gfortran

sudo pip install --upgrade distribute
sudo pip install --upgrade virtualenv

virtualenv --no-site-packages --extra-search-dir=/usr/local/lib/python2.7/dist-packages/scipy .

./bin/python bootstrap.py
./bin/buildout
echo OK
