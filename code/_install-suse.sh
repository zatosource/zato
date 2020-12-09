#!/bin/bash

# Python version to use needs to be provided by our caller
PY_BINARY=$1
echo "*** Zato SUSE installation using $PY_BINARY ***"

sudo zypper install -y \
    curl cyrus-sasl-devel gcc gcc-c++ haproxy libbz2-devel libev-devel libev4 \
    libffi-devel keyutils-devel libmemcached-devel libpqxx-devel              \
    openldap2-devel libxml2-devel libxslt-devel libyaml-devel openssl         \
    patch $PY_BINARY $PY_BINARY-devel $PY_BINARY-pip uuid-devel               \
    wget zlib-devel

#    build-essential curl git haproxy libbz2-dev libev-dev libev4 libevent-dev \
#    libffi-dev libkeyutils-dev libldap2-dev libmemcached-dev libpq-dev \
#    libsasl2-dev libssl-dev libxml2-dev libxslt1-dev libyaml-dev openssl \
#    $PY_BINARY $PY_BINARY-dev $PY_BINARY-pip swig uuid-dev uuid-runtime wget \
#    zlib1g-dev lsb-release

curl https://bootstrap.pypa.io/get-pip.py | $(type -p $PY_BINARY)
$PY_BINARY -m pip install       \
    --no-warn-script-location   \
    -U virtualenv

$PY_BINARY -m virtualenv .
source ./bin/activate
source ./_postinstall.sh $PY_BINARY
