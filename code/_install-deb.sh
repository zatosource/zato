#!/bin/bash

#set -x

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

# Python version to use needs to be provided by our caller
PY_BINARY=$1
INSTALL_PYTHON=${2:-y}
SKIP_OS=${3:-n}
CLEAR_VENV=${4:-n}
echo "*** Zato installation using $PY_BINARY ***"

if [[ "$SKIP_OS" != "y" ]]; then
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
fi

# Use uv from support-linux/bin
UV_BIN="$CURDIR/support-linux/bin/uv"

if [[ "$CLEAR_VENV" == "y" ]]; then
    echo Clearing existing virtual environment in $CURDIR
    rm -rf $CURDIR/bin $CURDIR/lib $CURDIR/lib64 $CURDIR/include $CURDIR/pyvenv.cfg
fi

echo Creating virtual environment in $CURDIR using uv
$UV_BIN venv "$(realpath $CURDIR)" --python $PY_BINARY --allow-existing

echo Activating virtualenv in $CURDIR
source $CURDIR/bin/activate

echo Setting up environment in $CURDIR
$CURDIR/bin/python $CURDIR/util/zato_environment.py install
echo ⭐ Successfully installed `zato --version`
