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

sudo apt-get install bzr gfortran haproxy  \
    libatlas-dev libatlas3gf-base libblas3gf \
    libevent-dev libgfortran3 liblapack-dev liblapack3gf \
    libpq-dev libyaml-dev libxml2-dev libxslt1-dev libumfpack5.4.0 \
    openssl python2.7-dev python-m2crypto python-numpy python-pip \
    python-scipy python-zdaemon swig uuid-dev uuid-runtime

mkdir ../code/zato_extra_paths

symlink_py 'M2Crypto'
symlink_py 'numpy'
symlink_py 'scipy'

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

