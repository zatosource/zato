#!/bin/bash

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=/home/foxway/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION
HAPROXY_VERSION=1.6.7

cd /home/foxway
mkdir $HOME/haproxy
wget http://www.haproxy.org/download/1.6/src/haproxy-$HAPROXY_VERSION.tar.gz
tar -xzvf haproxy-$HAPROXY_VERSION.tar.gz --strip 1 -C $HOME/haproxy/
cd $HOME/haproxy
make TARGET=generic USE_OPENSSL=1
