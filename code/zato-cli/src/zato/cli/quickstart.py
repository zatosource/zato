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
import os, shutil, sys, stat, traceback
from copy import deepcopy
from datetime import datetime
from uuid import uuid4

# Zato
from zato.cli import ZatoCommand, common_odb_opts, broker_opts, create_odb, \
     create_lb, ca_create_ca, ca_create_lb_agent, ca_create_server, \
     ca_create_zato_admin, create_broker, create_server, create_zato_admin, kvdb_opts
from zato.common import SERVER_JOIN_STATUS, SIMPLE_IO
from zato.common.defaults import http_plain_server_port
from zato.common.odb import ping_queries
from zato.common.odb.model import *
from zato.common.util import current_host, service_name_from_impl, tech_account_password
from zato.server import main

zato_qs_start_template = """#!/usr/bin/env sh

BASE_DIR=`pwd`
ZATO_BIN={zato_bin}

echo Starting the Zato quickstart environment

# Start the load balancer first ..
cd $BASE_DIR/load-balancer
$ZATO_BIN start .

# .. the broker ..
cd $BASE_DIR/broker
$ZATO_BIN start .

# .. servers ..
cd $BASE_DIR/server1
$ZATO_BIN start .

cd $BASE_DIR/server2
$ZATO_BIN start .

# .. web admin comes as the last one because it may ask Django-related questions.
cd $BASE_DIR/zato-admin
$ZATO_BIN start .

cd $BASE_DIR
echo Zato quickstart environment started
exit 0
""" 

zato_qs_stop_template = """#!/usr/bin/env sh

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
exit 0
"""

zato_qs_restart = """#!/usr/bin/env sh

./zato-qs-stop.sh
./zato-qs-start.sh
""" 

################################################################################

class Quickstart(ZatoCommand):
    command_name = "quickstart"
    needs_empty_dir = True

    def __init__(self, target_dir="."):
        super(Quickstart, self).__init__()
        self.target_dir = target_dir

    opts = deepcopy(common_odb_opts) + deepcopy(broker_opts) + deepcopy(kvdb_opts)
    description = "Quickly sets up a working Zato environment."
    
    def create_scripts(self):
        """ Creates start/stop/restart scripts for the newly created quickstart
        environment.
        """
        # This surely will need to be improved when distributions begin
        # to ship Zato, for now it will do the trick just fine.
        zato_bin = os.path.join(os.path.dirname(sys.executable), 'zato')

        zato_qs_start_path = os.path.join(self.target_dir, 'zato-qs-start.sh')
        zato_qs_stop_path = os.path.join(self.target_dir, 'zato-qs-stop.sh')
        zato_qs_restart_path = os.path.join(self.target_dir, 'zato-qs-restart.sh')
        
        open(zato_qs_start_path, 'w').write(zato_qs_start_template.format(zato_bin=zato_bin))
        open(zato_qs_stop_path, 'w').write(zato_qs_stop_template.format(zato_bin=zato_bin))
        open(zato_qs_restart_path, 'w').write(zato_qs_restart)

        file_mod = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP
        
        os.chmod(zato_qs_start_path, file_mod)
        os.chmod(zato_qs_stop_path, file_mod)
        os.chmod(zato_qs_restart_path, file_mod)
    
    def get_next_id(self, session, class_, like_attr, like_value, order_by, split_by):
        """ Gets the next ID for a given class, such as Cluster or Server.
        """
        next_id = '01'
        top_id = session.query(class_).filter(Cluster.name.like(like_value)).order_by(order_by)
        
        try:
            top_id = top_id[0]
        except Exception, e:
            # It's OK, we simply don't have any such IDs yet.
            return next_id
        else:
            _,_,_, id = top_id.name.split(split_by)
            next_id = int(id) + 1
            next_id = str(next_id).zfill(2)
            
        return next_id
    
    def execute(self, args):
        
        try:

            server02_port_diff = 20
            
            # Make sure the ODB tables exists.
            # Note: Also make sure that's always at the very top of the method
            # as otherwise the 'quickstart' command will fail on a pristine
            # database, one that hasn't been used with Zato yet.
            create_odb.CreateODB().execute(args)

            args.cluster_name = 'zato-quickstart-cluster'
            args.server_name = 'zato-server'
            
            engine = self._get_engine(args)

            print('\nPinging database..')
            engine.execute(ping_queries[args.odb_type])
            print('Ping OK\n')
            
            session = self._get_session(engine)

            next_id = self.get_next_id(session, Cluster, Cluster.name, 
                                       'zato-quickstart-cluster-%', Cluster.id.desc(),
                                       '-')
            cluster_name = 'zato-quickstart-cluster-{next_id}'.format(next_id=next_id)

            ca_dir = os.path.abspath(os.path.join(self.target_dir, './ca'))
            lb_dir = os.path.abspath(os.path.join(self.target_dir, './load-balancer'))
            server_dir1 = os.path.abspath(os.path.join(self.target_dir, './server1'))
            server_dir2 = os.path.abspath(os.path.join(self.target_dir, './server2'))
            zato_admin_dir = os.path.abspath(os.path.join(self.target_dir, './zato-admin'))
            broker_dir = os.path.abspath(os.path.join(self.target_dir, './broker'))

            # Create the CA.
            os.mkdir(ca_dir)
            ca_create_ca.CreateCA(ca_dir).execute(args)
            
            # Create the broker
            cb = create_broker.CreateBroker(broker_dir)
            cb.execute(args)

            # Create crypto stuff for each component (but not for the broker)
            lb_format_args = ca_create_lb_agent.CreateLBAgent(ca_dir).execute(args)
            server_format_args = ca_create_server.CreateServer(ca_dir).execute(args)
            zato_admin_format_args = ca_create_zato_admin.CreateZatoAdmin(ca_dir).execute(args)

            # Create the LB agent
            os.mkdir(lb_dir)
            create_lb.CreateLoadBalancer(lb_dir).execute(args, use_default_backend=True,
                        server02_port=http_plain_server_port+server02_port_diff)

            # .. copy the LB agent's crypto material over to its directory
            shutil.copy2(lb_format_args['priv_key_name'], os.path.join(lb_dir, 'config', 'lba-priv-key.pem'))
            shutil.copy2(lb_format_args['cert_name'], os.path.join(lb_dir, 'config', 'lba-cert.pem'))
            shutil.copy2(os.path.join(ca_dir, 'ca-material/ca-cert.pem'), os.path.join(lb_dir, 'config', 'ca-chain.pem'))
            
            # Create the servers
            os.mkdir(server_dir1)
            os.mkdir(server_dir2)
            cs1 = create_server.CreateServer(server_dir1, cluster_name)
            cs2 = create_server.CreateServer(server_dir2, cluster_name)
            
            # Copy crypto stuff to the newly created directories. We're doing
            # it here because CreateServer's execute expects the pub_key to be
            # already at its place.
            cs1.prepare_directories()
            cs2.prepare_directories()
            
            for server_dir in(server_dir1, server_dir2):
                shutil.copy2(server_format_args['priv_key_name'], os.path.join(server_dir, 'config/repo/zs-priv-key.pem'))
                shutil.copy2(server_format_args['pub_key_name'], os.path.join(server_dir, 'config/repo/zs-pub-key.pem'))
                shutil.copy2(server_format_args['cert_name'], os.path.join(server_dir, 'config/repo/zs-cert.pem'))
                shutil.copy2(os.path.join(ca_dir, 'ca-material/ca-cert.pem'), os.path.join(server_dir, 'config/repo/ca-chain.pem'))

            cs1.execute(args, parallel_count=1)
            cs2.execute(args, starting_port=http_plain_server_port+server02_port_diff, parallel_count=1)

            # Create the web admin now.
            
            tech_account_name = 'zato-{random}'.format(random=uuid4().hex[:10])
            tech_account_password_clear = uuid4().hex
            
            os.mkdir(zato_admin_dir)
            create_zato_admin.CreateZatoAdmin(zato_admin_dir, tech_account_name, tech_account_password_clear).execute(args)

            # .. copy the web admin's material over to its directory
            
            # Will be used later on.
            priv_key_path = os.path.join(zato_admin_dir, 'zato-admin-priv-key.pem')
            
            shutil.copy2(zato_admin_format_args['priv_key_name'], priv_key_path)
            shutil.copy2(zato_admin_format_args['cert_name'], os.path.join(zato_admin_dir, 'zato-admin-cert.pem'))
            shutil.copy2(os.path.join(ca_dir, 'ca-material/ca-cert.pem'), os.path.join(zato_admin_dir, 'ca-chain.pem'))

            print('Setting up ODB objects..')

            #
            # Cluster
            #
            cluster = Cluster(None, cluster_name, 'An automatically generated quickstart cluster',
                args.odb_type, args.odb_host, args.odb_port, args.odb_user, args.odb_db_name, 
                args.odb_schema, args.broker_host, args.broker_port, cb.token, 'localhost', 11223, 20151)

            #
            # Servers
            #
            server1 = Server(None, 'zato-quickstart-server-01', cluster, cs1.odb_token, SERVER_JOIN_STATUS.ACCEPTED, 
                             datetime.now(), 'zato-quickstart/' + current_host())
            session.add(server1)
            
            server2 = Server(None, 'zato-quickstart-server-02', cluster, cs2.odb_token, SERVER_JOIN_STATUS.ACCEPTED, 
                             datetime.now(), 'zato-quickstart/' + current_host())
            session.add(server2)
            
            # Commit all the stuff.
            session.commit()

            print('ODB objects created')
            print('')
            
            self.create_scripts()

            print('Quickstart OK. You can now start the newly created Zato components by issuing the ./zato-qs-start.sh command\n')
            
        except Exception, e:
            print("\nAn exception has been caught, quitting now!\n")
            traceback.print_exc()
            print("")
        except KeyboardInterrupt:
            print("\nQuitting.")
            sys.exit(1)
            

def main(target_dir):
    Quickstart(target_dir).run()

if __name__ == "__main__":
    main(".")
