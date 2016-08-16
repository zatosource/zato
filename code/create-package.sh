#!/bin/bash

cd $HOME
tar -cvzf zato-2.0.7.tar.gz .bash_profile .bashrc bin/ bzr/ .cache/ \
    haproxy/ include/ lib/ .local/ opt/ .pki/ redis-3.2.3/ \
    extra-libs/ foxway.foxwayops/ server-objects/ services/
