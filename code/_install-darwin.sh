#!/bin/bash

#
# Taken from https://gist.github.com/josephwecker/2884332
#
CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

function symlink_py {
    ln -s $(brew --prefix)/lib/python2.7/site-packages/${1} $CURDIR/zato_extra_paths
}

rm -rf $CURDIR/bin
rm -rf $CURDIR/develop-eggs
rm -rf $CURDIR/downloads
rm -rf $CURDIR/eggs
rm -rf $CURDIR/include
rm -rf $CURDIR/.installed.cfg
rm -rf $CURDIR/lib
rm -rf $CURDIR/parts
rm -rf $CURDIR/zato_extra_paths

mkdir $CURDIR/zato_extra_paths

sudo gem install sass

brew install git
brew install swig
brew install python

pip install --upgrade distribute
pip install --upgrade virtualenv

pip install nose
pip install m2crypto
pip install zdaemon

brew tap samueljohn/python
brew tap homebrew/science

brew install haproxy
brew install gfortran
brew install bzr
brew install libevent
brew install zmq
brew install libyaml
brew install libxml2
brew install libxslt
brew install ossp-uuid
brew install openssl
brew install libpqxx

brew install samueljohn/python/numpy
brew install scipy

symlink_py 'M2Crypto'

virtualenv .

./bin/python bootstrap.py -v 1.7.0
./bin/buildout

echo
echo OK