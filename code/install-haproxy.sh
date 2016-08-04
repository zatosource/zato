#!/bin/bash

ZATO_VERSION=2.0.7
ZATO_ROOT_DIR=/home/foxway/opt/zato
ZATO_TARGET_DIR=$ZATO_ROOT_DIR/$ZATO_VERSION
HAPROXY_VERSION=1.6.7

cd /home/foxway
mkdir haproxy
sudo su - foxway -c "mkdir $HOME/haproxy"
sudo su - foxway -c "wget http://www.haproxy.org/download/1.6/src/haproxy-$HAPROXY_VERSION.tar.gz"
sudo su - foxway -c "tar xzf haproxy-$HAPROXY_VERSION.tar.gz -C $HOME/haproxy"
sudo su - foxway -c "cd $HOME/haproxy && make TARGET=generic USE_OPENSSL=1"

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
chown foxway:foxway /home/foxway/haproxy.cfg

# Start haproxy in daemon mode
sudo su - foxway -c "cd $HOME/haproxy/haproxy -D -f haproxy.cfg"
