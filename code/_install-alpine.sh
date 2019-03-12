#!/bin/bash

# Python version to use needs to be provided by our caller
PY_BINARY=$1
echo "*** Zato Alpine installation using $PY_BINARY ***"

# Alpine does not use glibc, so pip disables binary wheels, therefore we also
# need SciPy dependencies.
sudo apk add \
    build-base bzip2 bzip2-dev cyrus-sasl-dev curl gfortran git haproxy \
    keyutils-dev lapack-dev libev-dev libevent-dev libffi-dev libressl \
    libressl-dev libuuid libxml2-dev libxslt-dev linux-headers openldap-dev \
    patch postgresql-dev python2 python2-dev suitesparse swig wget yaml-dev

curl https://bootstrap.pypa.io/get-pip.py | sudo $PY_BINARY
sudo $PY_BINARY -m pip install -U setuptools virtualenv==15.1.0

$PY_BINARY -m virtualenv .
source ./bin/activate
source ./_postinstall.sh $PY_BINARY
