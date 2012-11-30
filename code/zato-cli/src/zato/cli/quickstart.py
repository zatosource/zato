# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, random, stat, sys
from copy import deepcopy
from itertools import count
from uuid import uuid4

# Bunch
from bunch import Bunch

# Zato
from zato.cli import common_odb_opts, kvdb_opts, ca_create_ca, ca_create_lb_agent, ca_create_server, \
     ca_create_zato_admin, create_cluster, create_lb, create_odb, create_server, create_zato_admin, ZatoCommand
from zato.common.defaults import http_plain_server_port
from zato.common.markov_passwords import generate_password
from zato.common.util import get_zato_command, make_repr

random.seed()

zato_qs_start_template = """#!/usr/bin/env sh

export ZATO_CLI_DONT_SHOW_OUTPUT=1

BASE_DIR=`pwd`
ZATO_BIN={zato_bin}

echo Starting the Zato quickstart environment

# Start the load balancer first ..
cd $BASE_DIR/load-balancer
$ZATO_BIN start .
echo [1/4] Load-balancer started

# .. servers ..
cd $BASE_DIR/server1
$ZATO_BIN start .
echo [2/4] server1 started

cd $BASE_DIR/server2
$ZATO_BIN start .
echo [3/4] server2 started

# .. web admin comes as the last one because it may ask Django-related questions.
cd $BASE_DIR/zato-admin
$ZATO_BIN start .
echo [4/4] Zato admin started

cd $BASE_DIR
echo Zato quickstart environment started
echo Visit https://TODO for more information and support options
exit 0
""" 

zato_qs_stop_template = """#!/usr/bin/env sh

export ZATO_CLI_DONT_SHOW_OUTPUT=1

BASE_DIR=`pwd`
ZATO_BIN={zato_bin}

echo Stopping the Zato quickstart environment

# Start the load balancer first ..
cd $BASE_DIR/load-balancer
$ZATO_BIN stop .

# .. the broker ..
cd $BASE_DIR/broker
$ZATO_BIN stop .

# .. servers ..
cd $BASE_DIR/server1
$ZATO_BIN stop .

cd $BASE_DIR/server2
$ZATO_BIN stop .

# .. web admin comes as the last one because it may ask Django-related questions.
cd $BASE_DIR/zato-admin
$ZATO_BIN stop .

cd $BASE_DIR
echo Zato quickstart environment stopped
"""

zato_qs_restart = """#!/usr/bin/env sh

./zato-qs-stop.sh
./zato-qs-start.sh
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
    #needs_empty_dir = True
    allow_empty_secrets = True
    opts = deepcopy(common_odb_opts) + deepcopy(kvdb_opts)
    
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
        bunch.postgresql_schema = args.postgresql_schema
        bunch.odb_password = args.odb_password
        bunch.kvdb_password = args.kvdb_password
        bunch.cluster_name = cluster_name
        
        return bunch
    
    def execute(self, args):
        """ Quickly creates Zato components
        1) CA and crypto material
        2) ODB
        3) ODB initial data 
        4) server1 
        5) server2 
        6) load-balancer
        7) Zato admin
        8) Scripts
        """
        next_step = count(1)
        next_port = count(http_plain_server_port)
        total_steps = 8
        cluster_name = 'quickstart-{}'.format(random.getrandbits(20)).zfill(7)
        server_names = {'1':'server1', '2':'server2'}
        tech_account_name = 'techacct-{}'.format(random.getrandbits(20)).zfill(7)
        tech_account_password = uuid4().hex
        broker_host = 'localhost'
        broker_port = 6379
        lb_host = 'localhost'
        lb_port = 11223
        lb_agent_port = 20151
        
        #
        # 1) CA
        #
        ca_path = os.path.join(args.path, 'ca')
        os.mkdir(ca_path)
        
        ca_args = self._bunch_from_args(args, cluster_name)
        ca_args.path = ca_path
        
        ca_args_server1 = deepcopy(ca_args)
        ca_args_server1.server_name = server_names['1']
        
        ca_args_server2 = deepcopy(ca_args)
        ca_args_server2.server_name = server_names['2']
        
        ca_create_ca.Create(ca_args).execute(ca_args, False)
        ca_create_lb_agent.Create(ca_args).execute(ca_args, False)
        
        ca_create_server.Create(ca_args_server1).execute(ca_args_server1, False)
        ca_create_server.Create(ca_args_server2).execute(ca_args_server2, False)
        
        ca_create_zato_admin.Create(ca_args).execute(ca_args, False)

        server_crypto_loc = {}
        for key in server_names:
            server_crypto_loc[key] = CryptoMaterialLocation(ca_path, '{}-{}'.format(cluster_name, server_names[key]))
        
        lb_agent_crypto_loc = CryptoMaterialLocation(ca_path, 'lb-agent')
        zato_admin_crypto_loc = CryptoMaterialLocation(ca_path, 'zato-admin')
        
        self.logger.info('[{}/{}] Certificate authority created'.format(next_step.next(), total_steps))
        
        #
        # 2) ODB
        #
        if create_odb.Create(args).execute(args, False) == self.SYS_ERROR.ODB_EXISTS:
            self.logger.info('[{}/{}] ODB schema already exists, not creating it'.format(next_step.next(), total_steps))
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
        create_cluster_args.tech_account_name = tech_account_name
        create_cluster_args.tech_account_password = tech_account_password
        create_cluster.Create(create_cluster_args).execute(create_cluster_args, False)
        
        self.logger.info('[{}/{}] ODB initial data created'.format(next_step.next(), total_steps))
        
        #
        # 4) server1 
        # 5) server2
        #
        for key in server_names:
            server_path = os.path.join(args.path, server_names[key])
            os.mkdir(server_path)
            
            create_server_args = self._bunch_from_args(args, cluster_name)
            create_server_args.server_name = server_names[key]
            create_server_args.path = server_path
            create_server_args.cert_path = server_crypto_loc[key].cert_path
            create_server_args.pub_key_path = server_crypto_loc[key].pub_path
            create_server_args.priv_key_path = server_crypto_loc[key].priv_path
            
            create_server.Create(create_server_args).execute(create_server_args, next_port.next(), False)
            
            self.logger.info('[{}/{}] server{} created'.format(next_step.next(), total_steps, key))
            
        #
        # 6) load-balancer
        #
        lb_path = os.path.join(args.path, 'load-balancer')
        os.mkdir(lb_path)
        
        create_lb_args = self._bunch_from_args(args, cluster_name)
        create_lb_args.path = lb_path
        create_lb_args.cert_path = lb_agent_crypto_loc.cert_path
        create_lb_args.pub_key_path = lb_agent_crypto_loc.pub_path
        create_lb_args.priv_key_path = lb_agent_crypto_loc.priv_path
        create_lb_args.ca_certs_path = lb_agent_crypto_loc.ca_certs_path
        
        # Need to substract 1 because we've already called .next() twice
        # when creating servers above.
        server2_port = next_port.next()-1 
        
        create_lb.Create(create_lb_args).execute(create_lb_args, True, server2_port, False)
        self.logger.info('[{}/{}] Load-balancer created'.format(next_step.next(), total_steps))
        
        #
        # 7) Zato admin
        #
        zato_admin_path = os.path.join(args.path, 'zato-admin')
        os.mkdir(zato_admin_path)
        
        create_zato_admin_args = self._bunch_from_args(args, cluster_name)
        create_zato_admin_args.path = zato_admin_path
        create_zato_admin_args.cert_path = zato_admin_crypto_loc.cert_path
        create_zato_admin_args.pub_key_path = zato_admin_crypto_loc.pub_path
        create_zato_admin_args.priv_key_path = zato_admin_crypto_loc.priv_path
        create_zato_admin_args.ca_certs_path = zato_admin_crypto_loc.ca_certs_path
        create_zato_admin_args.tech_account_name = tech_account_name
        create_zato_admin_args.tech_account_password = tech_account_password
        
        password = generate_password()
        admin_created = create_zato_admin.Create(create_zato_admin_args).execute(create_zato_admin_args, False, password)
        
        # Need to reset the logger here because executing the create_zato_admin command
        # loads the Zato admin's logger which doesn't like that of ours.
        self.reset_logger(args, True)
        self.logger.info('[{}/{}] Zato admin created'.format(next_step.next(), total_steps))
        
        #
        # 8) Scripts
        #
        zato_bin = os.path.join(os.path.dirname(sys.executable), 'zato')
        zato_qs_start_path = os.path.join(args.path, 'zato-qs-start.sh')
        zato_qs_stop_path = os.path.join(args.path, 'zato-qs-stop.sh')
        zato_qs_restart_path = os.path.join(args.path, 'zato-qs-restart.sh')

        open(zato_qs_start_path, 'w').write(zato_qs_start_template.format(zato_bin=zato_bin))
        open(zato_qs_stop_path, 'w').write(zato_qs_stop_template.format(zato_bin=zato_bin))
        open(zato_qs_restart_path, 'w').write(zato_qs_restart)

        file_mod = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP
        
        os.chmod(zato_qs_start_path, file_mod)
        os.chmod(zato_qs_stop_path, file_mod)
        os.chmod(zato_qs_restart_path, file_mod)
        
        self.logger.info('[{}/{}] Management scripts created'.format(next_step.next(), total_steps))
        self.logger.info('Quickstart cluster {} created'.format(cluster_name))
        
        if admin_created:
            self.logger.info('Zato admin user:[admin], password:[{}]'.format(password))
        else:
            self.logger.info('User [admin] already exists in the ODB')
            
        self.logger.info('Start the cluster by issuing the {}/zato-qs-start.sh command'.format(args.path))
        self.logger.info('Visit https://TODO for more information and support options')
