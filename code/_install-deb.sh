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

# Ubuntus and Debians require different versions
# of libumfpack package
if command -v lsb_release > /dev/null; then
    release=$(lsb_release -c | cut -f2)
    if [[ "$release" == "precise"  ]] || [[ "$release" == "wheezy"  ]]; then
        LIBUMFPACK_VERSION=5.4.0
    elif [[ "$release" == "xenial"  ]]; then
        LIBATLAS3BASE=libatlas3-base
        LIBBLAS3=libblas3
        LIBLAPACK3=liblapack3
        LIBUMFPACK_VERSION=5.7.1
    else
        LIBATLAS3BASE=libatlas3gf-base
        LIBBLAS3=libblas3gf
        LIBLAPACK3=liblapack3gf
        LIBUMFPACK_VERSION=5.6.2
    fi
fi

# Always run an update so there are no surprises later on when it actually
# comes to fetching the packages from repositories.
sudo apt-get update

sudo apt-get install -y git bzr gfortran haproxy  \
    libatlas-dev $LIBATLAS3BASE $LIBBLAS3 \
    libbz2-dev libev4 libev-dev \
    libevent-dev libgfortran3 liblapack-dev $LIBLAPACK3 \
    libpq-dev libyaml-dev libxml2-dev libxslt1-dev libumfpack$LIBUMFPACK_VERSION \
    openssl python2.7-dev python-numpy python-pip \
    python-scipy python-zdaemon swig uuid-dev uuid-runtime libffi-dev \
    freetds-dev

# On Debian and Ubuntu the binary goes to /usr/sbin/haproxy so we need to symlink it
# to a directory that can be easily found on PATH so that starting the load-balancer
# is possible without tweaking its configuration file.

out=$(lsb_release -si)
if [ $out == "Debian" ] || [ $out == "Ubuntu" ]; then
    sudo ln -sf /usr/sbin/haproxy /usr/bin/haproxy
fi

mkdir $CURDIR/zato_extra_paths

symlink_py 'numpy'
symlink_py 'scipy'

export CYTHON=$CURDIR/bin/cython

sudo pip install --upgrade pip
sudo pip install setuptools==35.0.1
sudo pip install virtualenv==1.9.1
sudo pip install zato-apitest

virtualenv . --no-pip

$CURDIR/bin/python bootstrap.py
$CURDIR/bin/buildout

echo
echo OK
