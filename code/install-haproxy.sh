#!/bin/bash

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=$HOME/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION
HAPROXY_MINOR=1.6
HAPROXY_MICRO=1.6.7

cd /home/foxway
mkdir $HOME/haproxy
wget http://www.haproxy.org/download/$HAPROXY_MINOR/src/haproxy-$HAPROXY_MICRO.tar.gz
tar -xzvf haproxy-$HAPROXY_VERSION.tar.gz --strip 1 -C $HOME/haproxy/
cd $HOME/haproxy
make TARGET=generic USE_OPENSSL=1
