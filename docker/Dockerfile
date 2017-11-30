#!./bin/py
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Dariusz Suchojad <dsuch at zato.io>
#
# Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
#
#########################################

# docker build -q -t zato -f docker/Dockerfile .
#
# docker-machine start default 2 > /dev/null
# eval `docker-machine env default`
# docker-machine ip default
#
# docker create -p 22 -p 139:139 -p 445:445 -p 6379:6379 -p 8183:8183 -p 17010:17010 -p 17011:17011 -p 11223:11223 -it zato
# docker exec -it <CONTAINER ID> bash

# Access environment (slow search, over network)
#
#   Docker (add after required tools)
#     COPY docker/Dockerfile.d/etc/ /etc/
#     RUN apt-get install -y samba
#     RUN (echo toor; echo toor) | smbpasswd -s -a
#     EXPOSE 139 445
#   
#   Insert to entry.sh
#     service samba start
#
#   Expose ports
#     -p 139:139 -p 445:445
#
#   Mount image
#     smb://root:toor@XXX/zato-smb
#
#   Editor
#     Sublime Text with thousands of plugins (if missing, make one)
#       * open folder zato-smb/zato
#

#########################################

FROM ubuntu:16.04

RUN apt-get update --fix-missing
RUN apt-get upgrade -y

# ENV would persist to the final image
ENV DEBIAN_FRONTEND=noninteractive
ENV ZATO=/zato

RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Set .bashrc shell startup
RUN echo 'cd $ZATO' >> /root/.bashrc

# Install basic tools
RUN apt-get install -y \
    apt-utils apt-transport-https \
    python-software-properties software-properties-common \
    curl ssh unzip redis-server supervisor \
    nano htop wget git sudo sqlite

# Install required tools
RUN apt-get install -y \
    bzr gfortran haproxy \
    libatlas-dev libatlas3-base libblas3 \
    libbz2-dev libev4 libev-dev \
    libevent-dev libgfortran3 liblapack-dev liblapack3 libldap2-dev \
    libpq-dev libsasl2-dev libyaml-dev libxml2-dev libxslt1-dev \
    libumfpack* openssl python2.7-dev python-numpy python-pip \
    python-scipy python-zdaemon swig uuid-dev uuid-runtime libffi-dev \
    libssl-dev freetds-dev
RUN ln -sf /usr/sbin/haproxy /usr/bin/haproxy

# Zato 3.0 - Install
COPY . $ZATO
WORKDIR $ZATO/code
RUN mkdir zato_extra_paths
RUN ln -s `python -c 'import numpy, os.path, sys; sys.stdout.write(os.path.dirname(numpy.__file__))'` zato_extra_paths
RUN ln -s `python -c 'import scipy, os.path, sys; sys.stdout.write(os.path.dirname(scipy.__file__))'` zato_extra_paths
ENV CYTHON="$ZATO/code/bin/cython"
RUN pip install --upgrade pip distribute==0.7.3 virtualenv==15.1.0 zato-apitest
RUN virtualenv .
RUN bin/pip install --upgrade pip
RUN bin/python bootstrap.py
RUN bin/pip install cython==0.27.1
RUN git log -n 1 --pretty=format:'%H' > release-info/revision.txt
RUN bin/buildout
ENV PATH=$PATH:$ZATO/code/bin

RUN mkdir -p $ZATO/env/qs-1
WORKDIR $ZATO/env/qs-1
RUN zato quickstart create . sqlite localhost 6379 --verbose --kvdb_password '' --cluster_name 'zato-quickstart'
RUN sed -i 's/127.0.0.1:11223/0.0.0.0:11223/g' load-balancer/config/repo/zato.config
RUN sed -i 's/gunicorn_workers=2/gunicorn_workers=1/g' server1/config/repo/server.conf
RUN sed -i 's/gunicorn_workers=2/gunicorn_workers=1/g' server2/config/repo/server.conf

# Redis Warning 'fix' (breaks code)
#RUN sysctl vm.overcommit_memory=1
#RUN echo 'sysctl -w net.core.somaxconn=137' >> /etc/rc.local
#RUN echo 'echo never > /sys/kernel/mm/transparent_hugepage/enabled' >> /etc/rc.local

# Create zato user
RUN useradd -s /bin/bash zato

# Grant ssh privileges
RUN mkdir -p /var/run/sshd && chmod 755 /var/run/sshd

# Copy config files and starter scripts
WORKDIR $ZATO
COPY docker/Dockerfile.d/zato .
RUN chmod 755 zato_start_load_balancer \
              zato_start_server1 \
              zato_start_server2 \
              zato_start_scheduler \
              zato_start_web_admin

# Set a password for web admin and append it to a config file
RUN touch web_admin_password
RUN uuidgen > web_admin_password
RUN echo "path=$ZATO/env/qs-1/web-admin" >> update_password.config
RUN echo 'password'=$(cat web_admin_password) >> update_password.config
RUN zato from-config update_password.config

EXPOSE 22 6379 8183 17010 17011 11223

# Set Zato user as owner
RUN chown -R zato:zato $ZATO

# Copy entry.sh to root directory
COPY docker/Dockerfile.d/root/ /root/
RUN chmod +x /root/entry.sh

# Set start command
ENTRYPOINT ["/root/entry.sh"]
