#!/bin/bash

PYTHON_VER="2.7.13"
PYTHON_URL="https://www.python.org/ftp/python/$PYTHON_VER/Python-$PYTHON_VER.tgz"
PYTHON_PREFIX="/opt/zato/python/$PYTHON_VER"
PATH="$PYTHON_PREFIX/bin:$PATH"

sudo yum -y install \
    bzip2 bzip2-devel cyrus-sasl-devel gcc-c++ git haproxy libev libev-devel \
    libevent-devel libffi libffi-devel libxml2-devel libxslt-devel \
    libyaml-devel openldap-devel openssl openssl-devel patch postgresql-devel \
    python-devel suitesparse swig uuid uuid-devel wget

if ! [ "$(type -p python2.7)" ]
then
    # CentOS 6.x requires python2.7 build.
    (
        cd /tmp
        wget "$PYTHON_URL"
        tar zxf "Python-$PYTHON_VER.tgz"
        cd "Python-$PYTHON_VER"
        ./configure --quiet --prefix="$PYTHON_PREFIX"
        # Travis CI always has at least 2 vCPUs.
        make -j 2 >/dev/null
        sudo make altinstall >/dev/null
    )
fi

wget https://bootstrap.pypa.io/get-pip.py
sudo $(type -p python2.7) get-pip.py
sudo $(type -p python2.7) -m pip install -U setuptools virtualenv==15.1.0

python2.7 -m virtualenv .
source ./bin/activate
source ./_postinstall.sh
