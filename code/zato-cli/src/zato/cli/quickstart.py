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
import argparse, os, shutil, sys, textwrap, traceback
from copy import deepcopy
from datetime import datetime
from getpass import getpass
from hashlib import sha256
from string import Template
from uuid import uuid4

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# M2Crypto
from M2Crypto import RSA

# Zato
from zato.cli import ZatoCommand, common_odb_opts, broker_opts, create_odb, \
     create_lb, ca_create_ca, ca_create_lb_agent, ca_create_server, \
     ca_create_zato_admin, create_server, create_zato_admin
from zato.common import ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.odb import engine_def, ping_queries
from zato.common.odb.model import *
from zato.common.util import current_host, security_def_type, tech_account_password
from zato.server import main
from zato.server.crypto import CryptoManager
from zato.server.repo import RepoManager

################################################################################

class Quickstart(ZatoCommand):
    command_name = "quickstart"
    needs_empty_dir = True

    def __init__(self, target_dir="."):
        super(Quickstart, self).__init__()
        self.target_dir = target_dir

    opts = deepcopy(common_odb_opts) + deepcopy(broker_opts)
    description = "Quickly sets up a working Zato environment."
    
    def get_next_id(self, session, class_, like_attr, like_value, order_by, split_by):
        
        next_id = 1
        
        top_id = session.query(class_).filter(
            Cluster.name.like(like_value)).order_by(order_by)
        try:
            top_id = top_id[0]
        except Exception, e:
            # It's OK, we simply don't have any such IDs yet.
            return next_id
        else:
            _, id = top_id.name.split(split_by)
            next_id = int(id) + 1
            
        return next_id

    def execute(self, args):
        try:

            # Make sure the ODB tables exists.
            # Note: Also make sure that's always at the very top of the method
            # as otherwise the 'quickstart' command will fail on a pristine
            # database, one that hasn't been used with Zato yet.
            create_odb.CreateODB().execute(args)

            args.cluster_name = "ZatoQuickstart"
            args.server_name = "ZatoServer"
            
            engine = self._get_engine(args)

            print("\nPinging database..")
            engine.execute(ping_queries[args.odb_type])
            print("Ping OK\n")
            
            session = self._get_session(engine)

            next_id = self.get_next_id(session, Cluster, Cluster.name, 
                                       'ZatoQuickstartCluster-%', Cluster.id.desc(),
                                       '#')
            cluster_name = 'ZatoQuickstartCluster-#{next_id}'.format(next_id=next_id)

            ca_dir = os.path.abspath(os.path.join(self.target_dir, "./ca"))
            lb_dir = os.path.abspath(os.path.join(self.target_dir, "./load-balancer"))
            server_dir = os.path.abspath(os.path.join(self.target_dir, "./server"))
            zato_admin_dir = os.path.abspath(os.path.join(self.target_dir, "./zato-admin"))

            # Create the CA.
            os.mkdir(ca_dir)
            ca_create_ca.CreateCA(ca_dir).execute(args)

            # Create crypto stuff for each component
            lb_format_args = ca_create_lb_agent.CreateLBAgent(ca_dir).execute(args)
            server_format_args = ca_create_server.CreateServer(ca_dir).execute(args)
            zato_admin_format_args = ca_create_zato_admin.CreateZatoAdmin(ca_dir).execute(args)

            # Create the LB agent.
            os.mkdir(lb_dir)
            create_lb.CreateLoadBalancer(lb_dir).execute(args)

            # .. copy the LB agent's crypto material over to its directory
            shutil.copy2(lb_format_args["priv_key_name"], os.path.join(lb_dir, 'config', "lba-priv-key.pem"))
            shutil.copy2(lb_format_args["cert_name"], os.path.join(lb_dir, 'config', "lba-cert.pem"))
            shutil.copy2(os.path.join(ca_dir, "ca-material/ca-cert.pem"), os.path.join(lb_dir, 'config', "ca-chain.pem"))
            
            
            # Create the server
            os.mkdir(server_dir)
            cs = create_server.CreateServer(server_dir, cluster_name)
            
            # Copy crypto stuff to the newly created directories. We're doing
            # it here because CreateServer's execute expects the pub_key to be
            # already at its place.
            cs.prepare_directories()

            shutil.copy2(server_format_args["priv_key_name"], os.path.join(server_dir, "config/repo/zs-priv-key.pem"))
            shutil.copy2(server_format_args["pub_key_name"], os.path.join(server_dir, "config/repo/zs-pub-key.pem"))
            shutil.copy2(server_format_args["cert_name"], os.path.join(server_dir, "config/repo/zs-cert.pem"))
            shutil.copy2(os.path.join(ca_dir, "ca-material/ca-cert.pem"), os.path.join(server_dir, "config/repo/ca-chain.pem"))

            cs.execute(args)

            # Create the web admin now.
            
            tech_account_name = 'techadmin-{random}'.format(random=uuid4().hex[:12])
            tech_account_password_clear = uuid4().hex
            
            os.mkdir(zato_admin_dir)
            create_zato_admin.CreateZatoAdmin(zato_admin_dir,
                tech_account_name, tech_account_password_clear).execute(args)

            # .. copy the web admin's material over to its directory
            
            # Will be used later on.
            priv_key_path = os.path.join(zato_admin_dir, "zato-admin-priv-key.pem")
            
            shutil.copy2(zato_admin_format_args["priv_key_name"], priv_key_path)
            shutil.copy2(zato_admin_format_args["cert_name"], os.path.join(zato_admin_dir, "zato-admin-cert.pem"))
            shutil.copy2(os.path.join(ca_dir, "ca-material/ca-cert.pem"), os.path.join(zato_admin_dir, "ca-chain.pem"))


            print("Setting up ODB objects..")


            #
            # Cluster
            #
            cluster = Cluster(None, cluster_name,
                              'An automatically generated quickstart cluster',
                              args.odb_type, args.odb_host, args.odb_port, args.odb_user,
                              args.odb_dbname, args.odb_schema, args.broker_host,
                              args.broker_start_port, '01234567890123456789012345678901',
                              'localhost', 20151,  11223)
            
            #
            # Server
            #
            server = Server(None, 
                            'ZatoQuickstartServer-(cluster-#{next_id})'.format(next_id=next_id), 
                            cluster,
                            cs.odb_token,
                            'ACCEPTED',
                            datetime.now(),
                            'zato-quickstart/' + current_host())
            session.add(server)
            

            #
            # ChannelURLDefinition
            #
            zato_soap = ChannelURLDefinition(None, '/zato/soap', 'soap', True, cluster)
            session.add(zato_soap)

            #
            # SecurityDef
            #
            sec_def = SecurityDefinition(None, security_def_type.tech_account)
            session.add(sec_def)
            
            #
            # ChannelURLSecurity
            #
            chan_url_sec = ChannelURLSecurity(zato_soap, sec_def)
            session.add(chan_url_sec)
            
            #
            # TechnicalAccount
            #
            salt = uuid4().hex
            password = tech_account_password(tech_account_password_clear, salt)
            tech_account = TechnicalAccount(None, tech_account_name, 
                                password, salt, True, sec_def, cluster=cluster)
            session.add(tech_account)
            
            #
            # ChannelURLSecurity
            #
            #channel_url_sec = ChannelURLSecurity(zato_soap, sec_def)
            #session.add(channel_url_sec)

            

            session.commit()

            print('ODB objects created')
            print('')

            print("Quickstart OK. You can now start the newly created Zato components.\n")
            print("""To start the server, type 'zato start {server_dir}'.
To start the load-balancer's agent, type 'zato start {lb_dir}'.
To start the ZatoAdmin web console, type 'zato start {zato_admin_dir}'.
            """.format(server_dir=server_dir, lb_dir=lb_dir, zato_admin_dir=zato_admin_dir))
            


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
