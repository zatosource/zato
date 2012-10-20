#!/bin/bash

function symlink_py {
    ln -s `python -c 'import '${1}', os.path, sys; sys.stdout.write(os.path.dirname('${1}'.__file__))'` ../code/zato_extra_paths
}

rm -rf ../code/bin
rm -rf ../code/develop-eggs
rm -rf ../code/downloads
rm -rf ../code/eggs
rm -rf ../code/include
rm -rf ../code/.installed.cfg
rm -rf ../code/lib
rm -rf ../code/parts
rm -rf ../code/zato_extra_paths

sudo apt-get install haproxy uuid-dev uuid-runtime libevent-dev bzr
sudo apt-get install python2.7-dev swig python-pip libpq-dev python-zdaemon
sudo apt-get install libyaml-dev libxml2-dev libxslt1-dev
sudo apt-get install libatlas-dev libblas3gf libatlas3gf-base libumfpack5.4.0
sudo apt-get install liblapack-dev libgfortran3 liblapack3gf gfortran
sudo apt-get install python-numpy python-scipy

mkdir ../code/zato_extra_paths

symlink_py 'scipy'
symlink_py 'numpy'

sudo pip install --upgrade distribute
sudo pip install --upgrade virtualenv

# Prepare buildout.cfg, taking into account the fact that not everyone uses WebSphere MQ

locate cmqc.h &> /dev/null
CMQC_H_OUT=$?
python ./prepare_buildout.py $CMQC_H_OUT

virtualenv .

./bin/python bootstrap.py
./bin/buildout
echo OK

