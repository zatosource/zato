#!/bin/bash -eux

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=/home/foxway/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION

wget -P /home/foxway https://www.python.org/ftp/python/2.7.6/Python-2.7.6.tgz
cd /home/foxway
tar -xvzf Python-2.7.6.tgz &> /dev/null
cd /home/foxway/Python-2.7.6
./configure --prefix=$ZATO_TARGET_DIR/code
make && make altinstall
