#!/bin/bash

cd $HOME
tar -czf zato-2.0.7.tar .bash_profile .bashrc bin/ bzr/ .cache/ \
    haproxy/ include/ lib/ .local/ opt/ .pki/ redis-3.2.3/ \
    extra-libs/ server_objects/ services/
