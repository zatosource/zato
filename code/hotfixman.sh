#!/bin/bash

mkdir -p ./hotfixes/backups-1.1
rm -rf ./hotfixes/hotfixes-1.1
curl https://zato.io/hotfixes/hotfixes-1.1.tar.bz2 -o ./hotfixes/hotfixes-1.1.tar.bz2
tar xvfj ./hotfixes/hotfixes-1.1.tar.bz2 -C ./hotfixes
rsync -abvv --suffix=_`date +"%Y%m%d_%H_%M_%S"` --backup-dir ./hotfixes/backups-1.1 hotfixes/hotfixes-1.1/ .