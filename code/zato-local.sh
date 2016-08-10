#!/bin/bash -eux

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=/home/foxway/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION

getent passwd foxway
if [ $? -eq 0 ]
then
    echo "User foxway exists"
else
    groupadd foxway
    useradd foxway -g foxway
fi

yum -y install git gcc-gfortran \
    gcc-c++ bzip2 bzip2-devel libffi libffi-devel \
    libevent-devel libyaml-devel libxml2-devel libxslt-devel \
    openssl openssl-devel postgresql-devel python-devel swig \
    unzip uuid-devel uuid

sudo su - foxway -c "mkdir -p $ZATO_TARGET_DIR"
sudo su - foxway -c "git clone https://github.com/zatosource/zato.git $ZATO_TARGET_DIR"
sudo su - foxway -c "cd $ZATO_TARGET_DIR && git fetch origin u/foxway"
sudo su - foxway -c "cd $ZATO_TARGET_DIR && git checkout u/foxway"
sudo su - foxway -c "$ZATO_TARGET_DIR/code/install.sh"
