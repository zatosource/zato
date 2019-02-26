#!/bin/bash

if ! [[ "$(type -p brew)" ]]
then
    echo "install.sh: OS X: please install Homebrew first." >&2
    exit 1
fi

# Python version to use needs to be provided by our caller
PY_BINARY=$1
echo "*** Zato Mac installation using $PY_BINARY ***"

brew install \
    bzip2 curl bzr git gsasl haproxy libev libevent libffi libxml2 libxslt \
    libyaml openldap openssl ossp-uuid postgresql python2 swig \
    || true

curl https://bootstrap.pypa.io/get-pip.py | sudo /usr/local/bin/$PY_BINARY
sudo /usr/local/bin/$PY_BINARY -m pip install -U setuptools virtualenv==15.1.0

/usr/local/bin/$PY_BINARY -m virtualenv .
source ./bin/activate
source ./_postinstall.sh $PY_BINARY
