#!/bin/bash

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=$HOME/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION

export PATH=$PATH:/home/foxway/usr/bin/:/home/foxway/.local/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/foxway/lib/:/home/foxway/lib64/:/home/foxway/usr/lib/:/home/foxway/usr/lib64/
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/home/foxway/lib64/pkgconfig/
export CYTHON=$ZATO_TARGET_DIR/code/bin/cython

echo "export PATH=$PATH:/home/foxway/usr/bin/:/home/foxway/.local/bin:/home/foxway/opt/zato/2.0.7/code/bin/:/home/foxway/redis-3.2.3/src/:/home/foxway/haproxy/" \
    | tee -a /home/foxway/.bashrc /home/foxway/.bash_profile
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/foxway/lib/:/home/foxway/lib64/:/home/foxway/usr/lib/:/home/foxway/usr/lib64/" \
    | tee -a /home/foxway/.bashrc /home/foxway/.bash_profile
echo "export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/home/foxway/lib64/pkgconfig/" \
    | tee -a /home/foxway/.bashrc /home/foxway/.bash_profile
echo "export CYTHON=$ZATO_TARGET_DIR/code/bin/cython" \
    | tee -a /home/foxway/.bashrc /home/foxway/.bash_profile

ln -s $ZATO_TARGET_DIR/code/bin/python2.7 $ZATO_TARGET_DIR/code/bin/python2
ln -s $ZATO_TARGET_DIR/code/bin/python2.7 $ZATO_TARGET_DIR/code/bin/python
strip -s $ZATO_TARGET_DIR/code/bin/python2.7

wget -P /home/foxway https://bootstrap.pypa.io/get-pip.py
$ZATO_TARGET_DIR/code/bin/python /home/foxway/get-pip.py --user

/home/foxway/.local/bin/pip install --upgrade pip --user
/home/foxway/.local/bin/pip install virtualenv==1.9.1 --user
/home/foxway/.local/bin/pip install cffi --user
/home/foxway/.local/bin/pip install argon2_cffi --user
/home/foxway/.local/bin/pip install sqlalchemy-utils --user

/home/foxway/.local/bin/virtualenv /home/foxway/

cd $ZATO_TARGET_DIR/code/
touch release-info/revision.txt
./bin/python bootstrap.py -v 1.7.0
./bin/buildout

echo
echo OK
