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

echo "export OPS_API_ROOT=http://localhost:11223" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_APPS_ROOTDIR=$HOME/foxway.foxwayops/foxwayid/apps" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_WEB_URLROOT=https://[server host]:11224/ops/apps" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_SERVER_ISOPS=True" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_DB_ENGINE=sqlite" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_DB_NAME=portal.db" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
#echo "export OPS_DB_USERNAME=testuser" \
#    | tee -a $HOME/.bashrc $HOME/.bash_profile
#echo "export OPS_DB_PASSWORD=testadmin" \
#    | tee -a $HOME/.bashrc $HOME/.bash_profile
echo "export OPS_SQLITE_PATH=$HOME/foxway.foxwayops" \
    | tee -a $HOME/.bashrc $HOME/.bash_profile
