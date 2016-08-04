#!/bin/bash

cd /home/foxway
tar -czvf zato-2.0.7.tar.gz .bash_profile .bashrc bin/ .cache/ etc/ \
    include/ lib/ .local/ opt/ redis-3.2.3 usr/ var/
