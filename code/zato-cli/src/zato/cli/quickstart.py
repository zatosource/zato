# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, random, stat
from collections import OrderedDict
from contextlib import closing
from copy import deepcopy
from itertools import count
from uuid import uuid4

# Bunch
from bunch import Bunch

# Cryptography
from cryptography.fernet import Fernet

# Zato
from zato.cli import common_odb_opts, kvdb_opts, ca_create_ca, ca_create_lb_agent, ca_create_scheduler, ca_create_server, \
     ca_create_web_admin, create_cluster, create_lb, create_odb, create_scheduler, create_server, create_web_admin, \
     ZatoCommand
from zato.common.crypto import CryptoManager
from zato.common.defaults import http_plain_server_port
from zato.common.odb.model import Cluster, PubSubSubscription, PubSubTopic
from zato.common.util import get_engine, get_session, make_repr

random.seed()

DEFAULT_NO_SERVERS=2

# Taken from http://stackoverflow.com/a/246128
script_dir = """SOURCE="${BASH_SOURCE[0]}"
BASE_DIR="$( dirname "$SOURCE" )"
while [ -h "$SOURCE" ]
do
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$BASE_DIR/$SOURCE"
  BASE_DIR="$( cd -P "$( dirname "$SOURCE"  )" && pwd )"
done
BASE_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
"""

sanity_checks_template = """$ZATO_BIN check-config $BASE_DIR/{server_name}"""

start_servers_template = """
cd $BASE_DIR/{server_name}
$ZATO_BIN start . --verbose
echo [{step_number}/$STEPS] {server_name} started
"""

zato_qs_start_head_template = """#!/bin/bash

set -e
export ZATO_CLI_DONT_SHOW_OUTPUT=1

{script_dir}
ZATO_BIN={zato_bin}
STEPS={start_steps}
CLUSTER={cluster_name}

echo Starting Zato cluster $CLUSTER
echo Checking configuration
"""

zato_qs_start_body_template = """
{sanity_checks}

echo [1/$STEPS] Redis connection OK
echo [2/$STEPS] SQL ODB connection OK

# Make sure TCP ports are available
echo [3/$STEPS] Checking TCP ports availability

ZATO_BIN_PATH=`which zato`
ZATO_BIN_DIR=`python -c "import os; print(os.path.dirname('$ZATO_BIN_PATH'))"`
UTIL_DIR=`python -c "import os; print(os.path.join('$ZATO_BIN_DIR', '..', 'util'))"`

$ZATO_BIN_DIR/py $UTIL_DIR/check_tcp_ports.py

# Start the load balancer first ..
cd $BASE_DIR/load-balancer
$ZATO_BIN start . --verbose
echo [4/$STEPS] Load-balancer started

# .. servers ..
{start_servers}

# .. scheduler ..
cd $BASE_DIR/scheduler
$ZATO_BIN start . --verbose
echo [7/$STEPS] Scheduler started
"""

zato_qs_start_tail = """
# .. web admin comes as the last one because it may ask Django-related questions.
cd $BASE_DIR/web-admin
$ZATO_BIN start . --verbose
echo [$STEPS/$STEPS] Web admin started

cd $BASE_DIR
echo Zato cluster $CLUSTER started
echo Visit https://zato.io/support for more information and support options
exit 0
"""

stop_servers_template = """
cd $BASE_DIR/{server_name}
$ZATO_BIN stop .
echo [{step_number}/$STEPS] {server_name} stopped
"""

zato_qs_stop_template = """#!/bin/bash

export ZATO_CLI_DONT_SHOW_OUTPUT=1

{script_dir}

if [[ "$1" = "--delete-pidfiles" ]]
then
  echo Deleting PID files

  rm -f $BASE_DIR/load-balancer/pidfile
  rm -f $BASE_DIR/load-balancer/zato-lb-agent.pid
  rm -f $BASE_DIR/server1/pidfile
  rm -f $BASE_DIR/server2/pidfile
  rm -f $BASE_DIR/web-admin/pidfile
  rm -f $BASE_DIR/scheduler/pidfile

  echo PID files deleted
fi

ZATO_BIN={zato_bin}
STEPS={stop_steps}
CLUSTER={cluster_name}

echo Stopping Zato cluster $CLUSTER

# Start the load balancer first ..
cd $BASE_DIR/load-balancer
$ZATO_BIN stop .
echo [1/$STEPS] Load-balancer stopped

# .. servers ..
{stop_servers}

cd $BASE_DIR/web-admin
$ZATO_BIN stop .
echo [4/$STEPS] Web admin stopped

cd $BASE_DIR/scheduler
$ZATO_BIN stop .
echo [$STEPS/$STEPS] Scheduler stopped

cd $BASE_DIR
echo Zato cluster $CLUSTER stopped
"""

zato_qs_restart = """#!/bin/bash

{script_dir}
cd $BASE_DIR

$BASE_DIR/zato-qs-stop.sh
$BASE_DIR/zato-qs-start.sh
"""

# ################################################################################################################################

class CryptoMaterialLocation(object):
    """ Locates and remembers location of various crypto material for Zato components.
    """
    def __init__(self, ca_dir, component_pattern):
        self.ca_dir = ca_dir
        self.component_pattern = component_pattern
        self.ca_certs_path = os.path.join(self.ca_dir, 'ca-material', 'ca-cert.pem')
        self.cert_path = None
        self.pub_path = None
        self.priv_path = None
        self.locate()

    def __repr__(self):
        return make_repr(self)

    def locate(self):
        for crypto_name in('cert', 'priv', 'pub'):
            path = os.path.join(self.ca_dir, 'out-{}'.format(crypto_name))
            for name in os.listdir(path):
                full_path = os.path.join(path, name)
                if '{}-{}'.format(self.component_pattern, crypto_name) in full_path:
                    setattr(self, '{}_path'.format(crypto_name), full_path)

# ################################################################################################################################

class Create(ZatoCommand):
    """ Quickly creates a working cluster
    """
    needs_empty_dir = True
    allow_empty_secrets = True
    opts = deepcopy(common_odb_opts) + deepcopy(kvdb_opts)
    opts.append({'name':'--cluster_name', 'help':'Name to be given to the new cluster'})
    opts.append({'name':'--servers', 'help':'How many servers to create'})

    def _bunch_from_args(self, args, cluster_name):
        bunch = Bunch()
        bunch.path = args.path
        bunch.verbose = args.verbose
        bunch.store_log = args.store_log
        bunch.store_config = args.store_config
        bunch.odb_type = args.odb_type
        bunch.odb_host = args.odb_host
        bunch.odb_port = args.odb_port
        bunch.odb_user = args.odb_user
        bunch.odb_db_name = args.odb_db_name
        bunch.kvdb_host = args.kvdb_host
        bunch.kvdb_port = args.kvdb_port
        bunch.sqlite_path = getattr(args, 'sqlite_path', None)
        bunch.postgresql_schema = getattr(args, 'postgresql_schema', None)
        bunch.odb_password = args.odb_password
        bunch.kvdb_password = args.kvdb_password
        bunch.cluster_name = cluster_name
        bunch.scheduler_name = 'scheduler1'

        return bunch

# ################################################################################################################################

    def _set_pubsub_server(self, args, server_id, cluster_name, topic_name):
        engine = self._get_engine(args)
        session = self._get_session(engine)
        sub = session.query(PubSubSubscription).\
            filter(PubSubTopic.id==PubSubSubscription.topic_id).\
            filter(PubSubTopic.name==topic_name).\
            filter(PubSubTopic.cluster_id==Cluster.id).\
            filter(Cluster.name==cluster_name).\
            one()

        # Set publishing server for that subscription
        sub.server_id = server_id

        session.add(sub)
        session.commit()

# ################################################################################################################################

    def execute(self, args):
        """ Quickly creates Zato components
        1) CA and crypto material
        2) ODB
        3) ODB initial data
        4) Servers
        5) Load-balancer
        6) Web admin
        7) Scheduler
        8) Scripts
        """

        if args.odb_type == 'sqlite':
            args.sqlite_path = os.path.abspath(os.path.join(args.path, 'zato.db'))

        next_step = count(1)
        next_port = count(http_plain_server_port)
        cluster_name = getattr(args, 'cluster_name', None) or 'quickstart-{}'.format(random.getrandbits(20)).zfill(7)
        servers = int(getattr(args, 'servers', 0) or DEFAULT_NO_SERVERS)

        server_names = OrderedDict()
        for idx in range(1, servers+1):
            server_names['{}'.format(idx)] = 'server{}'.format(idx)

        total_steps = 7 + servers
        admin_invoke_password = 'admin.invoke.' + uuid4().hex
        broker_host = 'localhost'
        broker_port = 6379
        lb_host = 'localhost'
        lb_port = 11223
        lb_agent_port = 20151

        args_path = os.path.abspath(args.path)

        # This could've been set to True by user in the command-line so we'd want
        # to unset it so that individual commands quickstart invokes don't attempt
        # to store their own configs.
        args.store_config = False

# ################################################################################################################################

        #
        # 1) CA
        #
        ca_path = os.path.join(args_path, 'ca')
        os.mkdir(ca_path)

        ca_args = self._bunch_from_args(args, cluster_name)
        ca_args.path = ca_path

        ca_create_ca.Create(ca_args).execute(ca_args, False)
        ca_create_lb_agent.Create(ca_args).execute(ca_args, False)
        ca_create_web_admin.Create(ca_args).execute(ca_args, False)
        ca_create_scheduler.Create(ca_args).execute(ca_args, False)

        server_crypto_loc = {}

        for name in server_names:
            ca_args_server = deepcopy(ca_args)
            ca_args_server.server_name = server_names[name]
            ca_create_server.Create(ca_args_server).execute(ca_args_server, False)
            server_crypto_loc[name] = CryptoMaterialLocation(ca_path, '{}-{}'.format(cluster_name, server_names[name]))

        lb_agent_crypto_loc = CryptoMaterialLocation(ca_path, 'lb-agent')
        web_admin_crypto_loc = CryptoMaterialLocation(ca_path, 'web-admin')
        scheduler_crypto_loc = CryptoMaterialLocation(ca_path, 'scheduler1')

        self.logger.info('[{}/{}] Certificate authority created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 2) ODB
        #
        if create_odb.Create(args).execute(args, False) == self.SYS_ERROR.ODB_EXISTS:
            self.logger.info('[{}/{}] ODB schema already exists'.format(next(next_step), total_steps))
        else:
            self.logger.info('[{}/{}] ODB schema created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 3) ODB initial data
        #
        create_cluster_args = self._bunch_from_args(args, cluster_name)
        create_cluster_args.broker_host = broker_host
        create_cluster_args.broker_port = broker_port
        create_cluster_args.lb_host = lb_host
        create_cluster_args.lb_port = lb_port
        create_cluster_args.lb_agent_port = lb_agent_port
        create_cluster_args['admin-invoke-password'] = admin_invoke_password
        create_cluster.Create(create_cluster_args).execute(create_cluster_args, False)

        self.logger.info('[{}/{}] ODB initial data created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 4) servers
        #

        # Must be shared by all servers
        jwt_secret = Fernet.generate_key()
        secret_key = Fernet.generate_key()

        for idx, name in enumerate(server_names):
            server_path = os.path.join(args_path, server_names[name])
            os.mkdir(server_path)

            create_server_args = self._bunch_from_args(args, cluster_name)
            create_server_args.server_name = server_names[name]
            create_server_args.path = server_path
            create_server_args.cert_path = server_crypto_loc[name].cert_path
            create_server_args.pub_key_path = server_crypto_loc[name].pub_path
            create_server_args.priv_key_path = server_crypto_loc[name].priv_path
            create_server_args.ca_certs_path = server_crypto_loc[name].ca_certs_path
            create_server_args.jwt_secret = jwt_secret
            create_server_args.secret_key = secret_key

            server_id = create_server.Create(create_server_args).execute(create_server_args, next(next_port), False, True)

            # We make the first server a delivery server for sample pub/sub topics.
            if idx == 0:
                self._set_pubsub_server(args, server_id, cluster_name, '/zato/demo/sample')

            self.logger.info('[{}/{}] server{} created'.format(next(next_step), total_steps, name))

# ################################################################################################################################

        #
        # 5) load-balancer
        #
        lb_path = os.path.join(args_path, 'load-balancer')
        os.mkdir(lb_path)

        create_lb_args = self._bunch_from_args(args, cluster_name)
        create_lb_args.path = lb_path
        create_lb_args.cert_path = lb_agent_crypto_loc.cert_path
        create_lb_args.pub_key_path = lb_agent_crypto_loc.pub_path
        create_lb_args.priv_key_path = lb_agent_crypto_loc.priv_path
        create_lb_args.ca_certs_path = lb_agent_crypto_loc.ca_certs_path

        # Need to substract 1 because we've already called .next() twice
        # when creating servers above.
        servers_port = next(next_port) - 1

        create_lb.Create(create_lb_args).execute(create_lb_args, True, servers_port, False)
        self.logger.info('[{}/{}] Load-balancer created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 6) Web admin
        #
        web_admin_path = os.path.join(args_path, 'web-admin')
        os.mkdir(web_admin_path)

        create_web_admin_args = self._bunch_from_args(args, cluster_name)
        create_web_admin_args.path = web_admin_path
        create_web_admin_args.cert_path = web_admin_crypto_loc.cert_path
        create_web_admin_args.pub_key_path = web_admin_crypto_loc.pub_path
        create_web_admin_args.priv_key_path = web_admin_crypto_loc.priv_path
        create_web_admin_args.ca_certs_path = web_admin_crypto_loc.ca_certs_path
        create_web_admin_args.admin_invoke_password = admin_invoke_password

        web_admin_password = CryptoManager.generate_password()
        admin_created = create_web_admin.Create(create_web_admin_args).execute(
            create_web_admin_args, False, web_admin_password, True)

        # Need to reset the logger here because executing the create_web_admin command
        # loads the web admin's logger which doesn't like that of ours.
        self.reset_logger(args, True)
        self.logger.info('[{}/{}] Web admin created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 7) Scheduler
        #
        scheduler_path = os.path.join(args_path, 'scheduler')
        os.mkdir(scheduler_path)

        session = get_session(get_engine(args))

        with closing(session):
            cluster_id = session.query(Cluster.id).\
                filter(Cluster.name==cluster_name).\
                one()[0]

        create_scheduler_args = self._bunch_from_args(args, cluster_name)
        create_scheduler_args.path = scheduler_path
        create_scheduler_args.cert_path = scheduler_crypto_loc.cert_path
        create_scheduler_args.pub_key_path = scheduler_crypto_loc.pub_path
        create_scheduler_args.priv_key_path = scheduler_crypto_loc.priv_path
        create_scheduler_args.ca_certs_path = scheduler_crypto_loc.ca_certs_path
        create_scheduler_args.cluster_id = cluster_id

        create_scheduler.Create(create_scheduler_args).execute(create_scheduler_args, False, True)
        self.logger.info('[{}/{}] Scheduler created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 8) Scripts
        #
        zato_bin = 'zato'
        zato_qs_start_path = os.path.join(args_path, 'zato-qs-start.sh')
        zato_qs_stop_path = os.path.join(args_path, 'zato-qs-stop.sh')
        zato_qs_restart_path = os.path.join(args_path, 'zato-qs-restart.sh')

        sanity_checks = []
        start_servers = []
        stop_servers = []

        for name in server_names:
            sanity_checks.append(sanity_checks_template.format(server_name=server_names[name]))
            start_servers.append(start_servers_template.format(server_name=server_names[name], step_number=int(name)+4))
            stop_servers.append(stop_servers_template.format(server_name=server_names[name], step_number=int(name)+1))

        sanity_checks = '\n'.join(sanity_checks)
        start_servers = '\n'.join(start_servers)
        stop_servers = '\n'.join(stop_servers)
        start_steps = 6 + servers
        stop_steps = 3 + servers

        zato_qs_start_head = zato_qs_start_head_template.format(
            zato_bin=zato_bin, script_dir=script_dir, cluster_name=cluster_name, start_steps=start_steps)
        zato_qs_start_body = zato_qs_start_body_template.format(sanity_checks=sanity_checks, start_servers=start_servers)
        zato_qs_start = zato_qs_start_head + zato_qs_start_body + zato_qs_start_tail

        zato_qs_stop = zato_qs_stop_template.format(
            zato_bin=zato_bin, script_dir=script_dir, cluster_name=cluster_name, stop_steps=stop_steps, stop_servers=stop_servers)

        open(zato_qs_start_path, 'w').write(zato_qs_start)
        open(zato_qs_stop_path, 'w').write(zato_qs_stop)
        open(zato_qs_restart_path, 'w').write(zato_qs_restart.format(script_dir=script_dir, cluster_name=cluster_name))

        file_mod = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP

        os.chmod(zato_qs_start_path, file_mod)
        os.chmod(zato_qs_stop_path, file_mod)
        os.chmod(zato_qs_restart_path, file_mod)

        self.logger.info('[{}/{}] Management scripts created'.format(next(next_step), total_steps))
        self.logger.info('Quickstart cluster {} created'.format(cluster_name))

        if admin_created:
            self.logger.info('Web admin user:[admin], password:[%s]', web_admin_password.decode('utf8'))
        else:
            self.logger.info('User [admin] already exists in the ODB')

        start_command = os.path.join(args_path, 'zato-qs-start.sh')
        self.logger.info('Start the cluster by issuing the {} command'.format(start_command))
        self.logger.info('Visit https://zato.io/support for more information and support options')

# ################################################################################################################################
