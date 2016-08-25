#!/bin/bash

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=$HOME/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION

cd $HOME
mkdir $HOME/haproxy
wget -N http://www.haproxy.org/download/1.6/src/haproxy-1.6.7.tar.gz
tar -xzvf haproxy-1.6.7.tar.gz --strip 1 -C $HOME/haproxy/
cd $HOME/haproxy
make TARGET=generic USE_OPENSSL=1
