#!/bin/bash

# Always run an update so there are no surprises later on when it actually
# comes to fetching the packages from repositories.
sudo apt-get update
sudo apt-get install -y lsb-release

# Debian 7.0 (Wheezy) requires the wheezy-backports repository.
if [[ "$(lsb_release -sir)" =~ '^Debian.7\.' ]]
then
    sudo apt-get install -y apt-transport-https python-software-properties
    sudo apt-add-repository 'deb https://deb.debian.org/debian wheezy-backports main'
    sudo apt-get update
    sudo apt-get install -y --reinstall libffi5
fi

sudo apt-get install -y \
    build-essential git haproxy libbz2-dev libev-dev libev4 libevent-dev \
    libffi-dev libldap2-dev libmemcached-dev libpq-dev libsasl2-dev \
    libssl-dev libxml2-dev libxslt1-dev libyaml-dev openssl python2.7 \
    python2.7-dev swig uuid-dev uuid-runtime wget zlib1g-dev

# On Debian and Ubuntu the binary goes to /usr/sbin/haproxy so we need to
# symlink it to a directory that can be easily found on PATH so that starting
# the load-balancer is possible without tweaking its configuration file.
if [[ "$(lsb_release -sir)" =~ '^(Debian|Ubuntu)' ]]
then
    sudo ln -sf /usr/sbin/haproxy /usr/bin/haproxy
fi

wget https://bootstrap.pypa.io/get-pip.py
sudo python2.7 get-pip.py
sudo python2.7 -m pip install -U setuptools virtualenv==15.1.0

python2.7 -m virtualenv .
source ./bin/activate
source ./_postinstall.sh
