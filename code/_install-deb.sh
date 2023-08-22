#!/bin/bash

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

# Python version to use needs to be provided by our caller
PY_BINARY=$1
INSTALL_PYTHON=${2:-y}
echo "*** Zato Ubuntu/Debian installation using $PY_BINARY ***"

# Always run an update so there are no surprises later on when it actually
# comes to fetching the packages from repositories.
sudo apt-get update

if ! [ -x "$(command -v lsb_release)" ]; then
  sudo apt-get install -y lsb-release
fi

if [[ "$INSTALL_PYTHON" == "y" ]]; then
  PYTHON_DEPENDENCIES="$PY_BINARY $PY_BINARY-dev $PY_BINARY-pip"
fi

sudo apt-get install -y \
    build-essential curl git haproxy libbz2-dev libev-dev libev4 libevent-dev \
    libffi-dev libkeyutils-dev libldap2-dev libpq-dev \
    libsasl2-dev libssl-dev libxml2-dev libxslt1-dev libyaml-dev openssl \
    swig uuid-dev uuid-runtime wget zlib1g-dev lsb-release ${PYTHON_DEPENDENCIES}

# On Debian and Ubuntu the binary goes to /usr/sbin/haproxy so we need to
# symlink it to a directory that can be easily found on PATH so that starting
# the load-balancer is possible without tweaking its configuration file.
if [[ "$(lsb_release -sir)" =~ '^(Debian|Ubuntu)' ]]
then
    sudo ln -sf /usr/sbin/haproxy /usr/bin/haproxy
fi

curl https://bootstrap.pypa.io/get-pip.py | $(type -p $PY_BINARY)
$PY_BINARY -m pip install -U virtualenv==20.8.1

echo Installing virtualenv in $CURDIR
$PY_BINARY -m virtualenv $CURDIR

echo Activating virtualenv in $CURDIR
source $CURDIR/bin/activate

echo Setting up environment in $CURDIR
$CURDIR/bin/python $CURDIR/util/zato_environment.py install

echo ⭐ Successfully installed `zato --version`
