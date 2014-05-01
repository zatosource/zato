# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, random, stat
from copy import deepcopy
from itertools import count
from uuid import uuid4

# Bunch
from bunch import Bunch

# Zato
from zato.cli import common_odb_opts, kvdb_opts, ca_create_ca, ca_create_lb_agent, ca_create_server, \
     ca_create_web_admin, create_cluster, create_lb, create_odb, create_server, create_web_admin, ZatoCommand
from zato.common.defaults import http_plain_server_port
from zato.common.markov_passwords import generate_password
from zato.common.util import make_repr

random.seed()

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
$ZATO_BIN start .
echo [{step_number}/$STEPS] {server_name} started
"""

zato_qs_start_head_template = """#!/bin/bash

set -e
export ZATO_CLI_DONT_SHOW_OUTPUT=1

{script_dir}
ZATO_BIN={zato_bin}
STEPS={start_steps}
CLUSTER={cluster_name}

echo Starting the Zato cluster $CLUSTER
echo Running sanity checks
"""

zato_qs_start_body_template = """
{sanity_checks}

echo [1/$STEPS] Redis connection OK
echo [2/$STEPS] SQL ODB connection OK

# Start the load balancer first ..
cd $BASE_DIR/load-balancer
$ZATO_BIN start .
echo [3/$STEPS] Load-balancer started

# .. servers ..
{start_servers}
"""

zato_qs_start_tail = """
# .. web admin comes as the last one because it may ask Django-related questions.
cd $BASE_DIR/web-admin
$ZATO_BIN start .
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
ZATO_BIN={zato_bin}
STEPS={stop_steps}
CLUSTER={cluster_name}

echo Stopping the Zato cluster $CLUSTER

# Start the load balancer first ..
cd $BASE_DIR/load-balancer
$ZATO_BIN stop .
echo [1/$STEPS] Load-balancer stopped

# .. servers ..
{stop_servers}

cd $BASE_DIR/web-admin
$ZATO_BIN stop .
echo [$STEPS/$STEPS] Web admin stopped

cd $BASE_DIR
echo Zato cluster $CLUSTER stopped
"""

zato_qs_restart = """#!/bin/bash

{script_dir}
cd $BASE_DIR

$BASE_DIR/zato-qs-stop.sh
$BASE_DIR/zato-qs-start.sh
"""


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

################################################################################

class Create(ZatoCommand):
    """ Quickly creates a working cluster
    """
    needs_empty_dir = True
    allow_empty_secrets = True
    opts = deepcopy(common_odb_opts) + deepcopy(kvdb_opts)
    opts.append({'name':'--cluster_name', 'help':"Name to be given to the new cluster"})
    opts.append({'name':'--servers', 'help':"Number of servers to be created"})

    def _bunch_from_args(self, args, cluster_name):
        bunch = Bunch()
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
        bunch.postgresql_schema = getattr(args, 'postgresql_schema', None)
        bunch.odb_password = args.odb_password
        bunch.kvdb_password = args.kvdb_password
        bunch.cluster_name = cluster_name
        
        return bunch
    
    def execute(self, args):
        """ Quickly creates Zato components
        1) CA and crypto material
        2) ODB
        3) ODB initial data
        4) servers
        5) load-balancer
        6) Web admin
        7) Scripts
        """
        next_step = count(1)
        next_port = count(http_plain_server_port)
        cluster_name = getattr(args, 'cluster_name', 'quickstart-{}'.format(random.getrandbits(20)).zfill(7))
        servers = int(getattr(args, 'servers', '2'))
        server_names = {'{}'.format(i):'server{}'.format(i) for i in range(1,servers+1)}
        total_steps = 6 + servers
        admin_invoke_password = uuid4().hex
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
        
        server_crypto_loc = {}
        for key in server_names:
            ca_args_server = deepcopy(ca_args)
            ca_args_server.server_name = server_names[key]
            ca_create_server.Create(ca_args_server).execute(ca_args_server, False)
            server_crypto_loc[key] = CryptoMaterialLocation(ca_path, '{}-{}'.format(cluster_name, server_names[key]))
        
        lb_agent_crypto_loc = CryptoMaterialLocation(ca_path, 'lb-agent')
        web_admin_crypto_loc = CryptoMaterialLocation(ca_path, 'web-admin')
        
        self.logger.info('[{}/{}] Certificate authority created'.format(next_step.next(), total_steps))
        
        #
        # 2) ODB
        #
        if create_odb.Create(args).execute(args, False) == self.SYS_ERROR.ODB_EXISTS:
            self.logger.info('[{}/{}] ODB schema already exists'.format(next_step.next(), total_steps))
        else:
            self.logger.info('[{}/{}] ODB schema created'.format(next_step.next(), total_steps))
            
        #
        # 3) ODB initial data
        #
        create_cluster_args = self._bunch_from_args(args, cluster_name)
        create_cluster_args.broker_host = broker_host
        create_cluster_args.broker_port = broker_port
        create_cluster_args.lb_host = lb_host
        create_cluster_args.lb_port = lb_port
        create_cluster_args.lb_agent_port = lb_agent_port
        create_cluster_args.admin_invoke_password = admin_invoke_password
        create_cluster.Create(create_cluster_args).execute(create_cluster_args, False)
        
        self.logger.info('[{}/{}] ODB initial data created'.format(next_step.next(), total_steps))
        
        #
        # 4) servers
        #
        for key in server_names:
            server_path = os.path.join(args_path, server_names[key])
            os.mkdir(server_path)
            
            create_server_args = self._bunch_from_args(args, cluster_name)
            create_server_args.server_name = server_names[key]
            create_server_args.path = server_path
            create_server_args.cert_path = server_crypto_loc[key].cert_path
            create_server_args.pub_key_path = server_crypto_loc[key].pub_path
            create_server_args.priv_key_path = server_crypto_loc[key].priv_path
            create_server_args.ca_certs_path = server_crypto_loc[key].ca_certs_path
            
            create_server.Create(create_server_args).execute(create_server_args, next_port.next(), False)
            
            self.logger.info('[{}/{}] server{} created'.format(next_step.next(), total_steps, key))
            
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
        servers_port = next_port.next() - 1
        
        create_lb.Create(create_lb_args).execute(create_lb_args, True, servers_port, False)
        self.logger.info('[{}/{}] Load-balancer created'.format(next_step.next(), total_steps))
        
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
        
        password = generate_password()
        admin_created = create_web_admin.Create(create_web_admin_args).execute(
            create_web_admin_args, False, password, True)
        
        # Need to reset the logger here because executing the create_web_admin command
        # loads the web admin's logger which doesn't like that of ours.
        self.reset_logger(args, True)
        self.logger.info('[{}/{}] Web admin created'.format(next_step.next(), total_steps))
        
        #
        # 7) Scripts
        #
        zato_bin = 'zato'
        zato_qs_start_path = os.path.join(args_path, 'zato-qs-start.sh')
        zato_qs_stop_path = os.path.join(args_path, 'zato-qs-stop.sh')
        zato_qs_restart_path = os.path.join(args_path, 'zato-qs-restart.sh')

        sanity_checks_array = []
        start_servers_array = []
        stop_servers_array = []
        for key in server_names:
            sanity_checks_array.append(sanity_checks_template.format(server_name=server_names[key]))
            start_servers_array.append(start_servers_template.format(server_name=server_names[key], step_number=int(key)+3))
            stop_servers_array.append(stop_servers_template.format(server_name=server_names[key], step_number=int(key)+1))

        sanity_checks = '\n'.join(sanity_checks_array)
        start_servers = '\n'.join(start_servers_array)
        stop_servers = '\n'.join(stop_servers_array)
        start_steps = 4 + servers
        stop_steps = 2 + servers

        zato_qs_start_head = zato_qs_start_head_template.format(zato_bin=zato_bin, script_dir=script_dir, cluster_name=cluster_name, start_steps=start_steps)
        zato_qs_start_body = zato_qs_start_body_template.format(sanity_checks=sanity_checks, start_servers=start_servers)
        zato_qs_start = zato_qs_start_head + zato_qs_start_body + zato_qs_start_tail

        zato_qs_stop = zato_qs_stop_template.format(zato_bin=zato_bin, script_dir=script_dir, cluster_name=cluster_name, stop_steps=stop_steps, stop_servers=stop_servers)

        open(zato_qs_start_path, 'w').write(zato_qs_start)
        open(zato_qs_stop_path, 'w').write(zato_qs_stop)
        open(zato_qs_restart_path, 'w').write(zato_qs_restart.format(script_dir=script_dir, cluster_name=cluster_name))

        file_mod = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP
        
        os.chmod(zato_qs_start_path, file_mod)
        os.chmod(zato_qs_stop_path, file_mod)
        os.chmod(zato_qs_restart_path, file_mod)
        
        self.logger.info('[{}/{}] Management scripts created'.format(next_step.next(), total_steps))
        self.logger.info('Quickstart cluster {} created'.format(cluster_name))
        
        if admin_created:
            self.logger.info('Web admin user:[admin], password:[{}]'.format(password))
        else:
            self.logger.info('User [admin] already exists in the ODB')
            
        start_command = os.path.join(args_path, 'zato-qs-start.sh')
        self.logger.info('Start the cluster by issuing the {} command'.format(start_command))
        self.logger.info('Visit https://zato.io/support for more information and support options')
