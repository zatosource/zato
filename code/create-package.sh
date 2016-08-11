#!/bin/bash

cd /home/foxway
tar -czvf zato-2.0.7.tar.gz .bash_profile .bashrc bin/ bzr/ .cache/ \
    haproxy/ include/ lib/ .local/ opt/ .pki/ redis-3.2.3/ \
    server_objects services
