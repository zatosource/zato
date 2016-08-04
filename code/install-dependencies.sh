#!/bin/bash

FOXWAY_HOME=/home/foxway
MIRROR_OS=http://mirror.centos.org/centos/6/os/x86_64/Packages

mkdir $FOXWAY_HOME/rpms
wget -P $FOXWAY_HOME/rpms \
    $MIRROR_OS/unzip-6.0-4.el6.x86_64.rpm \
    $MIRROR_OS/haproxy-1.5.4-3.el6.x86_64.rpm

for file in $(ls /home/foxway/rpms/)
do
rpm2cpio /home/foxway/rpms/$file > /home/foxway/rpms/$file.cpio
done

cd /home/foxway
for cpio in $(ls /home/foxway/rpms/ | grep .cpio)
do
cpio -idmv < /home/foxway/rpms/$cpio
done
