#!/bin/bash

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=$HOME/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION

export PATH=$PATH:$HOME/usr/bin/:$HOME/.local/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib/:$HOME/lib64/:$HOME/usr/lib/:$HOME/usr/lib64/
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$HOME/lib64/pkgconfig/
export CYTHON=$ZATO_TARGET_DIR/code/bin/cython

echo "export PATH=$PATH:$HOME/usr/bin/:$HOME/.local/bin:$HOME/opt/zato/2.0.7/code/bin/:$HOME/redis-3.2.3/src/:$HOME/haproxy/" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib/:$HOME/lib64/:$HOME/usr/lib/:$HOME/usr/lib64/" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$HOME/lib64/pkgconfig/" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export CYTHON=$ZATO_TARGET_DIR/code/bin/cython" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile

ln -s $ZATO_TARGET_DIR/code/bin/python2.7 $ZATO_TARGET_DIR/code/bin/python2
ln -s $ZATO_TARGET_DIR/code/bin/python2.7 $ZATO_TARGET_DIR/code/bin/python
strip -s $ZATO_TARGET_DIR/code/bin/python2.7

wget -P $HOME https://bootstrap.pypa.io/get-pip.py
$ZATO_TARGET_DIR/code/bin/python $HOME/get-pip.py --user

$HOME/.local/bin/pip install --upgrade pip --user
$HOME/.local/bin/pip install virtualenv==1.9.1 --user
$HOME/.local/bin/pip install cffi --user
$HOME/.local/bin/pip install argon2_cffi --user
$HOME/.local/bin/pip install sqlalchemy-utils --user

$HOME/.local/bin/virtualenv $HOME/

cd $ZATO_TARGET_DIR/code/
touch release-info/revision.txt
./bin/python bootstrap.py -v 1.7.0
./bin/buildout

echo
echo OK
