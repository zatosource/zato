#!/bin/bash

# Create Zato quickstart
mkdir -p $HOME/env/qs-1
zato quickstart create $HOME/env/qs-1 sqlite localhost \
    6379 \
    --kvdb_password '' \
    --verbose

# Start Zato components
cd $HOME/env/qs-1
zato start load-balancer
sleep 10
zato start server1
sleep 20
zato start server2
sleep 20
zato start web-admin
