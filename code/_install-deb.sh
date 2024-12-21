#!/bin/bash

#set -x

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
  PYTHON_DEPENDENCIES="$PY_BINARY $PY_BINARY-dev"
fi

sudo apt-get install -y \
    build-essential curl git haproxy \
    libffi-dev libldap2-dev libpq-dev \
    libsasl2-dev libssl-dev libxml2-dev libxslt1-dev libyaml-dev openssl \
    lsb-release ${PYTHON_DEPENDENCIES}

# On Debian and Ubuntu the binary goes to /usr/sbin/haproxy so we need to
# symlink it to a directory that can be easily found on PATH so that starting
# the load-balancer is possible without tweaking its configuration file.
if [[ "$(lsb_release -sir)" =~ '^(Debian|Ubuntu)' ]]
then
    sudo ln -sf /usr/sbin/haproxy /usr/bin/haproxy
fi

# Make sure we have virtualenv installed
sudo apt-get install -y python3.11-venv 1> /dev/null 2>& 1 || true
sudo apt-get install -y python3.12-venv 1> /dev/null 2>& 1 || true
sudo apt-get install -y python3.13-venv 1> /dev/null 2>& 1 || true
sudo apt-get install -y python3.14-venv 1> /dev/null 2>& 1 || true
sudo apt-get install -y python3.15-venv 1> /dev/null 2>& 1 || true
sudo apt-get install -y python3.16-venv 1> /dev/null 2>& 1 || true
sudo apt-get install -y python3.17-venv 1> /dev/null 2>& 1 || true
sudo apt-get install -y python3.18-venv 1> /dev/null 2>& 1 || true
sudo apt-get install -y python3.19-venv 1> /dev/null 2>& 1 || true

# Needed for Ubuntu 24.04+
sudo rm -rf /usr/lib/python3.*/EXTERNALLY-MANAGED

curl https://bootstrap.pypa.io/get-pip.py | $(type -p $PY_BINARY)
$PY_BINARY -m pip install -U virtualenv==20.8.1 --break-system-packages

echo Installing virtualenv in $CURDIR

# Install virtualenv (in Python 3.11+ it's venv, whereas previously it was virtualenv)
$PY_BINARY -m venv $CURDIR

echo Activating virtualenv in $CURDIR
source $CURDIR/bin/activate

echo Setting up environment in $CURDIR
PIP_DISABLE_PIP_VERSION_CHECK=1 $CURDIR/bin/python $CURDIR/util/zato_environment.py install

echo ⭐ Successfully installed `zato --version`
