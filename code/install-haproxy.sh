#!/bin/bash

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=/home/foxway/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION
HAPROXY_VERSION=1.6.7

cd /home/foxway
mkdir haproxy
mkdir $HOME/haproxy
wget http://www.haproxy.org/download/1.6/src/haproxy-$HAPROXY_VERSION.tar.gz
tar -xzvf haproxy-$HAPROXY_VERSION.tar.gz --strip 1 -C $HOME/haproxy/
cd $HOME/haproxy
make TARGET=generic USE_OPENSSL=1

# Generate config file for haproxy
cat > /home/foxway/haproxy/haproxy.cfg << EOL
global
    log /dev/log    local4

defaults
    log    global
    mode   http
    option httplog
    option dontlognull
    timeout connect 5000
    timeout client 50000
    timeout server 50000

listen http1
    bind 127.0.0.1:80
    mode http
EOL

# Start haproxy in daemon mode
$HOME/haproxy/haproxy -D -f haproxy.cfg
