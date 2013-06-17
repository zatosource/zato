#!/bin/bash

VERSION=1.1

mkdir -p ./hotfixes/backups-$VERSION
rm -rf ./hotfixes/hotfixes-$VERSION
curl https://zato.io/hotfixes/hotfixes-$VERSION.tar.bz2 -o ./hotfixes/hotfixes-$VERSION.tar.bz2
tar xvfj ./hotfixes/hotfixes-$VERSION.tar.bz2 -C ./hotfixes
rsync -abvv --suffix=_`date +"%Y%m%d_%H_%M_%S"` --backup-dir ./hotfixes/backups-$VERSION hotfixes/hotfixes-$VERSION/ .