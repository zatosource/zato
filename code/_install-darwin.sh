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

bash $CURDIR/clean.sh

mkdir $CURDIR/zato_extra_paths

brew install git
brew install swig
brew install python

pip install distribute==0.6.49
pip install virtualenv==1.9.1

pip install nose
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

symlink_py 'scipy'
symlink_py 'numpy'

virtualenv .

./bin/python bootstrap.py -v 1.7.0
./bin/buildout -c buildout-darwin.cfg

echo
echo OK
