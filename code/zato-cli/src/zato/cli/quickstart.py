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
     ca_create_zato_admin, create_broker, create_server, create_zato_admin
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
    
    def add_ping(self, session, cluster):
        
            #
            # Ping service and channels, with and without security checks ..
            #
        
            passwords = {
                'ping.plain_http.basic_auth': None,
                'ping.plain_http.wss.clear_text': None,
                'ping.plain_http.wss.digest': None,
                'ping.soap.basic_auth': None,
                'ping.soap.wss.clear_text': None,
                'ping.soap.wss.digest': None
            }
            
            for password in passwords:
                passwords[password] = uuid4().hex

            ping_service_name = 'zato.server.service.internal.Ping'
            ping_service = Service(None, ping_service_name, True, ping_service_name, True, cluster)
            session.add(ping_service)
            
            #
            # .. no security ..
            #
            ping_no_sec_channel = HTTPSOAP(None, 'zato:ping', True, True, 'channel', 
                                           'plain_http', '/zato/ping', None, None, None, service=ping_service, cluster=cluster)
            session.add(ping_no_sec_channel)


            #
            # All the possible options
            # 
            # Plain HTTP / Basic auth
            # Plain HTTP / WSS / Clear text
            # Plain HTTP / WSS / Digest
            # SOAP / Basic auth
            # SOAP / WSS / Clear text
            # SOAP / WSS / Digest
            #

            transports = ['plain_http', 'soap']
            wss_types = ['clear_text', 'digest']
            
            for transport in transports:

                base_name = 'ping.{0}.basic_auth'.format(transport)
                zato_name = 'zato:{0}'.format(base_name)
                url = '/zato/{0}'.format(base_name)
                soap_action, soap_version = (zato_name, '1.1') if transport == 'soap' else (None, None)
                
                sec_def = SecurityDefinition(None, security_def_type.basic_auth)
                session.add(sec_def)
                
                sec = HTTPBasicAuth(None, zato_name, True, zato_name, 'Zato', passwords[password], sec_def, cluster)
                session.add(sec)
                
                channel = HTTPSOAP(None, zato_name, True, True, 'channel', transport, url, None, soap_action, soap_version, service=ping_service, cluster=cluster)
                session.add(channel)
                
                channel_sec = HTTPSOAPSecurity(channel, sec_def)
                session.add(channel_sec)
                
                for wss_type in wss_types:
                    base_name = 'ping.{0}.wss.{1}'.format(transport, wss_type)
                    zato_name = 'zato:{0}'.format(base_name)
                    url = '/zato/{0}'.format(base_name)
                    
                    sec_def = SecurityDefinition(None, security_def_type.wss_username_password)
                    session.add(sec_def)
                    
                    sec = WSSDefinition(None, zato_name, True, zato_name, passwords[password], wss_type, True, True, 3600, 3600, sec_def, cluster)
                    session.add(sec)
                    
                    channel = HTTPSOAP(None, zato_name, True, True, 'channel', transport, url, None, soap_action, soap_version, service=ping_service, cluster=cluster)
                    session.add(channel)
                    
                    channel_sec = HTTPSOAPSecurity(channel, sec_def)
                    session.add(channel_sec)
                    
    def execute(self, args):
        try:

            
            # Make sure the ODB tables exists.
            # Note: Also make sure that's always at the very top of the method
            # as otherwise the 'quickstart' command will fail on a pristine
            # database, one that hasn't been used with Zato yet.
            create_odb.CreateODB().execute(args)

            args.cluster_name = 'ZatoQuickstart'
            args.server_name = 'ZatoServer'
            
            engine = self._get_engine(args)

            print('\nPinging database..')
            engine.execute(ping_queries[args.odb_type])
            print('Ping OK\n')
            
            session = self._get_session(engine)

            next_id = self.get_next_id(session, Cluster, Cluster.name, 
                                       'ZatoQuickstartCluster-%', Cluster.id.desc(),
                                       '#')
            cluster_name = 'ZatoQuickstartCluster-#{next_id}'.format(next_id=next_id)


            
            ca_dir = os.path.abspath(os.path.join(self.target_dir, './ca'))
            lb_dir = os.path.abspath(os.path.join(self.target_dir, './load-balancer'))
            server_dir = os.path.abspath(os.path.join(self.target_dir, './server'))
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
            create_lb.CreateLoadBalancer(lb_dir).execute(args)

            # .. copy the LB agent's crypto material over to its directory
            shutil.copy2(lb_format_args['priv_key_name'], os.path.join(lb_dir, 'config', 'lba-priv-key.pem'))
            shutil.copy2(lb_format_args['cert_name'], os.path.join(lb_dir, 'config', 'lba-cert.pem'))
            shutil.copy2(os.path.join(ca_dir, 'ca-material/ca-cert.pem'), os.path.join(lb_dir, 'config', 'ca-chain.pem'))
            
            # Create the server
            os.mkdir(server_dir)
            cs = create_server.CreateServer(server_dir, cluster_name)
            
            # Copy crypto stuff to the newly created directories. We're doing
            # it here because CreateServer's execute expects the pub_key to be
            # already at its place.
            cs.prepare_directories()

            shutil.copy2(server_format_args['priv_key_name'], os.path.join(server_dir, 'config/repo/zs-priv-key.pem'))
            shutil.copy2(server_format_args['pub_key_name'], os.path.join(server_dir, 'config/repo/zs-pub-key.pem'))
            shutil.copy2(server_format_args['cert_name'], os.path.join(server_dir, 'config/repo/zs-cert.pem'))
            shutil.copy2(os.path.join(ca_dir, 'ca-material/ca-cert.pem'), os.path.join(server_dir, 'config/repo/ca-chain.pem'))

            cs.execute(args)

            # Create the web admin now.
            
            tech_account_name = 'zato-{random}'.format(random=uuid4().hex[:10])
            tech_account_password_clear = uuid4().hex
            
            os.mkdir(zato_admin_dir)
            create_zato_admin.CreateZatoAdmin(zato_admin_dir,
                tech_account_name, tech_account_password_clear).execute(args)

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
            cluster = Cluster(None, cluster_name,
                              'An automatically generated quickstart cluster',
                              args.odb_type, args.odb_host, args.odb_port, args.odb_user,
                              args.odb_dbname, args.odb_schema, args.broker_host,
                              args.broker_start_port, cb.token,
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
            # SOAP Services
            #
            soap_services = {
    
                # SQL connection pools
                'zato:pool.sql.get-list':'zato.server.service.internal.sql.GetSQLConnectionPoolList',
                'zato:pool.sql.create':'zato.server.service.internal.sql.CreateSQLConnectionPool',
                'zato:pool.sql.edit':'zato.server.service.internal.sql.EditSQLConnectionPool',
                'zato:pool.sql.delete':'zato.server.service.internal.sql.DeleteSQLConnectionPool',
                'zato:pool.sql.change-password':'zato.server.service.internal.sql.ChangePasswordSQLConnectionPool',
                'zato:pool.sql.ping':'zato.server.service.internal.sql.PingSQLConnectionPool',
    
                # Scheduler
                'zato:scheduler.job.get-list':'zato.server.service.internal.scheduler.GetList',
                'zato:scheduler.job.create':'zato.server.service.internal.scheduler.Create',
                'zato:scheduler.job.edit':'zato.server.service.internal.scheduler.Edit',
                'zato:scheduler.job.execute':'zato.server.service.internal.scheduler.Execute',
                'zato:scheduler.job.delete':'zato.server.service.internal.scheduler.Delete',
    
                # Services
                'zato:service.get-list':'zato.server.service.internal.service.GetList',
                'zato:service.get-by-id':'zato.server.service.internal.service.GetByID',
                'zato:service.create':'zato.server.service.internal.service.Create',
                'zato:service.edit':'zato.server.service.internal.service.Edit',
                'zato:service.delete':'zato.server.service.internal.service.Delete',
    
                # SOAP channels
                'zato:channel.soap.get-list':'zato.server.service.internal.channel.soap.GetList',
    
                # Security
                'zato:security.get-list':'zato.server.service.internal.security.GetList',
    
                # Technical accounts
                'zato:security.tech-account.get-list':'zato.server.service.internal.security.tech_account.GetList',
                'zato:security.tech-account.get-by-id':'zato.server.service.internal.security.tech_account.GetByID',
                'zato:security.tech-account.create':'zato.server.service.internal.security.tech_account.Create',
                'zato:security.tech-account.edit':'zato.server.service.internal.security.tech_account.Edit',
                'zato:security.tech-account.change-password':'zato.server.service.internal.security.tech_account.ChangePassword',
                'zato:security.tech-account.delete':'zato.server.service.internal.security.tech_account.Delete',
    
                # WS-Security
                'zato:security.wss.get-list':'zato.server.service.internal.security.wss.GetList',
                'zato:security.wss.create':'zato.server.service.internal.security.wss.Create',
                'zato:security.wss.edit':'zato.server.service.internal.security.wss.Edit',
                'zato:security.wss.change-password':'zato.server.service.internal.security.wss.ChangePassword',
                'zato:security.wss.delete':'zato.server.service.internal.security.wss.Delete',
    
                # HTTP Basic Auth
                'zato:security.basic-auth.get-list':'zato.server.service.internal.security.basic_auth.GetList',
                'zato:security.basic-auth.create':'zato.server.service.internal.security.basic_auth.Create',
                'zato:security.basic-auth.edit':'zato.server.service.internal.security.basic_auth.Edit',
                'zato:security.basic-auth.change-password':'zato.server.service.internal.security.basic_auth.ChangePassword',
                'zato:security.basic-auth.delete':'zato.server.service.internal.security.basic_auth.Delete',
    
                # Definitions - AMQP
                'zato:definition.amqp.get-list':'zato.server.service.internal.definition.amqp.GetList',
                'zato:definition.amqp.get-by-id':'zato.server.service.internal.definition.amqp.GetByID',
                'zato:definition.amqp.create':'zato.server.service.internal.definition.amqp.Create',
                'zato:definition.amqp.change-password':'zato.server.service.internal.definition.amqp.ChangePassword',
                'zato:definition.amqp.edit':'zato.server.service.internal.definition.amqp.Edit',
                'zato:definition.amqp.delete':'zato.server.service.internal.definition.amqp.Delete',
    
                # Definitions - JMS WebSphere MQ
                'zato:definition.jms_wmq.get-list':'zato.server.service.internal.definition.jms_wmq.GetList',
                'zato:definition.jms_wmq.get-by-id':'zato.server.service.internal.definition.jms_wmq.GetByID',
                'zato:definition.jms_wmq.create':'zato.server.service.internal.definition.jms_wmq.Create',
                'zato:definition.jms_wmq.edit':'zato.server.service.internal.definition.jms_wmq.Edit',
                'zato:definition.jms_wmq.delete':'zato.server.service.internal.definition.jms_wmq.Delete',
    
                # Channels - AMQP
                'zato:channel.amqp.get-list':'zato.server.service.internal.channel.amqp.GetList',
                'zato:channel.amqp.create':'zato.server.service.internal.channel.amqp.Create',
                'zato:channel.amqp.edit':'zato.server.service.internal.channel.amqp.Edit',
                'zato:channel.amqp.delete':'zato.server.service.internal.channel.amqp.Delete',
    
                # Channels - JMS WebSphere MQ
                'zato:channel.jms_wmq.get-list':'zato.server.service.internal.channel.jms_wmq.GetList',
                'zato:channel.jms_wmq.create':'zato.server.service.internal.channel.jms_wmq.Create',
                'zato:channel.jms_wmq.edit':'zato.server.service.internal.channel.jms_wmq.Edit',
                'zato:channel.jms_wmq.delete':'zato.server.service.internal.channel.jms_wmq.Delete',
    
                # Channels - ZeroMQ
                'zato:channel.zmq.get-list':'zato.server.service.internal.channel.zmq.GetList',
                'zato:channel.zmq.create':'zato.server.service.internal.channel.zmq.Create',
                'zato:channel.zmq.edit':'zato.server.service.internal.channel.zmq.Edit',
                'zato:channel.zmq.delete':'zato.server.service.internal.channel.zmq.Delete',
    
                # Outgoing connections - AMQP
                'zato:outgoing.amqp.get-list':'zato.server.service.internal.outgoing.amqp.GetList',
                'zato:outgoing.amqp.create':'zato.server.service.internal.outgoing.amqp.Create',
                'zato:outgoing.amqp.edit':'zato.server.service.internal.outgoing.amqp.Edit',
                'zato:outgoing.amqp.delete':'zato.server.service.internal.outgoing.amqp.Delete',
    
                # Outgoing connections - JMS WebSphere MQ
                'zato:outgoing.jms_wmq.get-list':'zato.server.service.internal.outgoing.jms_wmq.GetList',
                'zato:outgoing.jms_wmq.create':'zato.server.service.internal.outgoing.jms_wmq.Create',
                'zato:outgoing.jms_wmq.edit':'zato.server.service.internal.outgoing.jms_wmq.Edit',
                'zato:outgoing.jms_wmq.delete':'zato.server.service.internal.outgoing.jms_wmq.Delete',
    
                # Outgoing connections - S3
                'zato:outgoing.s3.get-list':'zato.server.service.internal.outgoing.s3.GetList',
                'zato:outgoing.s3.create':'zato.server.service.internal.outgoing.s3.Create',
                'zato:outgoing.s3.edit':'zato.server.service.internal.outgoing.s3.Edit',
                'zato:outgoing.s3.delete':'zato.server.service.internal.outgoing.s3.Delete',
                
                # Outgoing connections - FTP
                'zato:outgoing.ftp.get-list':'zato.server.service.internal.outgoing.ftp.GetList',
                'zato:outgoing.ftp.create':'zato.server.service.internal.outgoing.ftp.Create',
                'zato:outgoing.ftp.edit':'zato.server.service.internal.outgoing.ftp.Edit',
                'zato:outgoing.ftp.delete':'zato.server.service.internal.outgoing.ftp.Delete',
                'zato:outgoing.ftp.change-password':'zato.server.service.internal.outgoing.ftp.ChangePassword',
    
                # Outgoing connections - ZeroMQ
                'zato:outgoing.zmq.get-list':'zato.server.service.internal.outgoing.zmq.GetList',
                'zato:outgoing.zmq.create':'zato.server.service.internal.outgoing.zmq.Create',
                'zato:outgoing.zmq.edit':'zato.server.service.internal.outgoing.zmq.Edit',
                'zato:outgoing.zmq.delete':'zato.server.service.internal.outgoing.zmq.Delete',
    
                # HTTP SOAP
                'zato:http_soap.get-list':'zato.server.service.internal.http_soap.GetList',
                'zato:http_soap.create':'zato.server.service.internal.http_soap.Create',
                'zato:http_soap.edit':'zato.server.service.internal.http_soap.Edit',
                'zato:http_soap.delete':'zato.server.service.internal.http_soap.Delete',
            }

            #
            # HTTPSOAP + services
            #

            zato_soap_channels = []
            
            for soap_action, service_name in soap_services.iteritems():
                
                service = Service(None, service_name, True, service_name, True, cluster)
                session.add(service)
                
                zato_soap = HTTPSOAP(None, soap_action, True, True, 'channel', 
                    'soap', '/zato/soap', None, soap_action, '1.1', service=service, cluster=cluster)
                session.add(zato_soap)
                
                zato_soap_channels.append(zato_soap)
                
            # Ping services
            self.add_ping(session, cluster)
                
            #
            # Security definition for all the other admin services uses a technical account.
            #
            sec_def = SecurityDefinition(None, security_def_type.tech_account)
            session.add(sec_def)
            
            #
            # HTTPSOAPSecurity
            #
            for soap_channel in zato_soap_channels:
                chan_url_sec = HTTPSOAPSecurity(soap_channel, sec_def)
                session.add(chan_url_sec)
            
            #
            # TechnicalAccount
            #
            salt = uuid4().hex
            password = tech_account_password(tech_account_password_clear, salt)
            tech_account = TechnicalAccount(None, tech_account_name, password, salt, True, sec_def, cluster=cluster)
            session.add(tech_account)
            
            # Commit all the stuff.
            session.commit()

            print('ODB objects created')
            print('')

            print('Quickstart OK. You can now start the newly created Zato components.\n')
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
