#!/bin/bash

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=$HOME/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION

cd $HOME
wget -N http://download.redis.io/releases/redis-3.2.3.tar.gz
tar -xvzf redis-3.2.3.tar.gz
cd redis-3.2.3/
make
