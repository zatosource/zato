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

sudo apt-get install -y git bzr gfortran haproxy \
    libatlas-dev libatlas3-base libblas3 \
    libbz2-dev libev4 libev-dev \
    libevent-dev libgfortran3 liblapack-dev liblapack3 libldap2-dev \
    libpq-dev libsasl2-dev libyaml-dev libxml2-dev libxslt1-dev \
    libumfpack* openssl python2.7-dev python-numpy python-pip \
    python-scipy python-zdaemon swig uuid-dev uuid-runtime libffi-dev libssl-dev

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
sudo pip install distribute==0.7.3
sudo pip install virtualenv==15.1.0
sudo pip install zato-apitest

virtualenv $CURDIR
$CURDIR/bin/pip install --upgrade pip

$CURDIR/bin/python bootstrap.py -v 1.7.0
$CURDIR/bin/pip install setuptools==31.0.1
$CURDIR/bin/pip install cython==0.22
$CURDIR/bin/buildout

echo
echo OK
