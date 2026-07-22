#!/bin/bash
# Rebuilds echo-server.jar from EchoServer.java - needs a JDK on the path.
set -e
cd "$(dirname "$0")"
javac EchoServer.java
jar --create --file echo-server.jar --main-class EchoServer EchoServer.class
rm -f EchoServer.class 'EchoServer$1.class'
echo "Built echo-server.jar"
