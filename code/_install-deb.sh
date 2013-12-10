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

# Always run an update so there are no surprises later on when it actually
# comes to fetching the packages from repositories.
sudo apt-get update

out=$(lsb_release -si)
arch=$(dpkg --print-architecture)


if grep -q wheezy /etc/*-release; then
    lhaproxy=`curl --silent http://packages.debian.org/wheezy-backports/$arch/haproxy/download | grep -o "http://[[:print:]]*_$arch.deb" | head -1`
    curl -O $lhaproxy
    sudo dpkg -i haproxy_*.deb
else
    sudo apt-get install haproxy
fi

sudo apt-get install git bzr gfortran  \
    libatlas-dev libatlas3gf-base libblas3gf \
    libevent-dev libgfortran3 liblapack-dev liblapack3gf \
    libpq-dev libyaml-dev libxml2-dev libxslt1-dev libumfpack5.4.0 \
    openssl python2.7-dev python-numpy python-pip \
    python-scipy python-zdaemon swig uuid-dev uuid-runtime

# On Debian Wheezy the binary goes to /usr/sbin/haproxy so we need to symlink it 
# to a directory that can be easily found on PATH so that starting the load-balancer
# is possible without tweaking its configuration file.

if [ $out == "Debian" ]; then
    sudo ln -sf /usr/sbin/haproxy /usr/bin/haproxy
fi

mkdir $CURDIR/zato_extra_paths

symlink_py 'numpy'
symlink_py 'scipy'

sudo pip install distribute==0.6.49
sudo pip install virtualenv==1.9.1

virtualenv .

$CURDIR/bin/python bootstrap.py -v 1.7.0
$CURDIR/bin/buildout

echo
echo OK
