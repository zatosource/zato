#!/bin/bash

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

if ! [[ "$(type -p brew)" ]]
then
    echo "install.sh: Mac : please install Homebrew first." >&2
    exit 1
fi

# Python version to use needs to be provided by our caller
PY_BINARY=$1
INSTALL_PYTHON=${2:-y}
echo "*** Zato Mac installation using $PY_BINARY ***"

if [[ "$INSTALL_PYTHON" == "y" ]]; then
    PYTHON_DEPENDENCIES="python3"
fi

brew install \
    autoconf automake bzip2 curl git gsasl haproxy libev libevent libffi libtool \
    libyaml openssl ossp-uuid pkg-config $PYTHON_DEPENDENCIES || true

curl https://bootstrap.pypa.io/get-pip.py | $(type -p $PY_BINARY)
$PY_BINARY -m pip install -U virtualenv==20.8.1

echo Installing virtualenv in $CURDIR
$PY_BINARY -m virtualenv $CURDIR

echo Activating virtualenv in $CURDIR
source $CURDIR/bin/activate

echo Setting up environment in $CURDIR
PIP_DISABLE_PIP_VERSION_CHECK=1 $CURDIR/bin/python $CURDIR/util/zato_environment.py install

echo ⭐ Successfully installed `zato --version`
