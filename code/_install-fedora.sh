#!/bin/bash

#
# Taken from https://gist.github.com/josephwecker/2884332
#
CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

function symlink_py {
    ln -s `python -c 'import '${1}', os.path, sys; sys.stdout.write(os.path.dirname('${1}'.__file__))'` $CURDIR/zato_extra_paths
}

bash $CURDIR/clean.sh

sudo yum -y install git bzr gcc-gfortran haproxy \
    gcc-c++ atlas-devel atlas blas-devel  \
    bzip2 bzip2-devel libffi libffi-devel \
    libevent-devel libev libev-devel libgfortran lapack-devel lapack \
    libyaml-devel libxml2-devel libxslt-devel suitesparse \
    openssl openssl-devel postgresql-devel python-devel numpy \
    scipy swig uuid-devel uuid

curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
sudo python get-pip.py

mkdir $CURDIR/zato_extra_paths

symlink_py 'numpy'
symlink_py 'scipy'

export CYTHON=$CURDIR/bin/cython

sudo pip install --upgrade pip
sudo pip install setuptools==35.0.1
sudo pip install virtualenv==1.9.1
sudo pip install zato-apitest

virtualenv --no-pip --python=python2.7 .

$CURDIR/bin/python bootstrap.py
$CURDIR/bin/buildout

echo
echo OK
