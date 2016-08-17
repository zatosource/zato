#!/bin/bash

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=$HOME/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION

echo "export PATH=$PATH:$HOME/usr/bin/:$HOME/.local/bin:$ZATO_TARGET_DIR/code/bin/:$HOME/redis-3.2.3/src/:$HOME/haproxy/" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib/:$HOME/lib64/:$HOME/usr/lib/:$HOME/usr/lib64/" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$HOME/lib64/pkgconfig/" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export CYTHON=$ZATO_TARGET_DIR/code/bin/cython" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile

echo "export OPS_API_ROOT=http://localhost:8000" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_APS_ROOTDIR=$HOME/foxway.foxwayops" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_WEB_URLROOT=http://localhost:8000/app" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_SERVER_ISOPS=True" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_DB_NAME=sqlite" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_DB_SQLLITE_PATH=$HOME/foxway.foxwayops/portal.db" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
