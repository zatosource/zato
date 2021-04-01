#!/bin/bash

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
    autoconf automake bzip2 curl git gsasl haproxy libev libevent libffi libtool libxml2 libxslt \
    libyaml openldap openssl ossp-uuid pkg-config postgresql swig $PYTHON_DEPENDENCIES || true

curl https://bootstrap.pypa.io/get-pip.py | $(type -p $PY_BINARY)
$PY_BINARY -m pip install -U virtualenv --ignore-installed

$PY_BINARY -m virtualenv .
source ./bin/activate
source ./_postinstall.sh $PY_BINARY
