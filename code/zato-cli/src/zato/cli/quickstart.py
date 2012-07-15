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
    
    def add_ping_services(self, session, cluster):
        """ Add a ping service and channels, with and without security checks.
        """
        passwords = {
            'ping.plain_http.basic_auth': None,
            'ping.soap.basic_auth': None,
            'ping.soap.wss.clear_text': None,
        }
        
        for password in passwords:
            passwords[password] = uuid4().hex

        ping_impl_name = 'zato.server.service.internal.Ping'
        ping_service_name = 'zato.Ping'
        ping_service = Service(None, ping_service_name, True, ping_impl_name, True, cluster)
        session.add(ping_service)
        
        #
        # .. no security ..
        #
        ping_no_sec_channel = HTTPSOAP(None, 'zato.ping', True, True, 'channel', 
            'plain_http', None, '/zato/ping', None, '', None, SIMPLE_IO.FORMAT.JSON, service=ping_service, cluster=cluster)
        session.add(ping_no_sec_channel)


        #
        # All the possible options
        # 
        # Plain HTTP / Basic auth
        # SOAP / Basic auth
        # SOAP / WSS / Clear text
        #

        transports = ['plain_http', 'soap']
        wss_types = ['clear_text']
        
        for transport in transports:
            
            if transport == 'plain_http':
                data_format = SIMPLE_IO.FORMAT.JSON
            else:
                data_format = SIMPLE_IO.FORMAT.XML

            base_name = 'ping.{0}.basic_auth'.format(transport)
            zato_name = 'zato.{0}'.format(base_name)
            url = '/zato/{0}'.format(base_name)
            soap_action, soap_version = (zato_name, '1.1') if transport == 'soap' else ('', None)
            password = passwords[base_name]
            
            sec = HTTPBasicAuth(None, zato_name, True, zato_name, 'Zato', password, cluster)
            session.add(sec)
            
            channel = HTTPSOAP(None, zato_name, True, True, 'channel', transport, None, url, None, soap_action, 
                               soap_version, data_format, service=ping_service, security=sec, cluster=cluster)
            session.add(channel)
            
            if transport == 'soap':
                for wss_type in wss_types:
                    base_name = 'ping.{0}.wss.{1}'.format(transport, wss_type)
                    zato_name = 'zato.{0}'.format(base_name)
                    url = '/zato/{0}'.format(base_name)
                    password = passwords[base_name]
                    
                    sec = WSSDefinition(None, zato_name, True, zato_name, password, wss_type, False, True, 3600, 3600, cluster)
                    session.add(sec)
                    
                    channel = HTTPSOAP(None, zato_name, True, True, 'channel', transport, None, url, None, soap_action, 
                                       soap_version, data_format, service=ping_service, security=sec, cluster=cluster)
                    session.add(channel)
                
    def add_soap_services(self, session, cluster, tech_account):
        """ Adds these Zato internal services that can be accessed through SOAP requests.
        """
        soap_services = {

            # Cluster - servers
            'zato:cluster.server.delete':'zato.server.service.internal.server.Delete',
            'zato:cluster.server.edit':'zato.server.service.internal.server.Edit',
            'zato:cluster.server.get-by-id':'zato.server.service.internal.server.GetByID',

            # Scheduler
            'zato:scheduler.job.create':'zato.server.service.internal.scheduler.Create',
            'zato:scheduler.job.delete':'zato.server.service.internal.scheduler.Delete',
            'zato:scheduler.job.edit':'zato.server.service.internal.scheduler.Edit',
            'zato:scheduler.job.execute':'zato.server.service.internal.scheduler.Execute',
            'zato:scheduler.job.get-by-name':'zato.server.service.internal.scheduler.GetByName',
            'zato:scheduler.job.get-list':'zato.server.service.internal.scheduler.GetList',

            # Services
            'zato:service.configure-request-response':'zato.server.service.internal.service.ConfigureRequestResponse',
            'zato:service.create':'zato.server.service.internal.service.Create',
            'zato:service.delete':'zato.server.service.internal.service.Delete',
            'zato:service.edit':'zato.server.service.internal.service.Edit',
            'zato:service.get-by-name':'zato.server.service.internal.service.GetByName',
            'zato:service.get-deployment-info-list':'zato.server.service.internal.service.GetDeploymentInfoList',
            'zato:service.get-list':'zato.server.service.internal.service.GetList',
            'zato:service.get-request-response':'zato.server.service.internal.service.GetRequestResponse',
            'zato:service.get-source-info':'zato.server.service.internal.service.GetSourceInfo',
            'zato:service.get-wsdl':'zato.server.service.internal.service.GetWSDL',
            'zato:service.get-channel-list':'zato.server.service.internal.service.GetChannelList',
            'zato:service.has-wsdl':'zato.server.service.internal.service.HasWSDL',
            'zato:service.invoke':'zato.server.service.internal.service.Invoke',
            'zato:service.set-wsdl':'zato.server.service.internal.service.SetWSDL',
            'zato:service.set-request-response':'zato.server.service.internal.service.SetRequestResponse',
            'zato:service.upload-package':'zato.server.service.internal.service.UploadPackage',

            # SOAP channels
            'zato:channel.soap.get-list':'zato.server.service.internal.channel.soap.GetList',

            # Security
            'zato:security.get-list':'zato.server.service.internal.security.GetList',

            # Technical accounts
            'zato:security.tech-account.change-password':'zato.server.service.internal.security.tech_account.ChangePassword',
            'zato:security.tech-account.create':'zato.server.service.internal.security.tech_account.Create',
            'zato:security.tech-account.delete':'zato.server.service.internal.security.tech_account.Delete',
            'zato:security.tech-account.edit':'zato.server.service.internal.security.tech_account.Edit',
            'zato:security.tech-account.get-by-id':'zato.server.service.internal.security.tech_account.GetByID',
            'zato:security.tech-account.get-list':'zato.server.service.internal.security.tech_account.GetList',

            # WS-Security
            'zato:security.wss.change-password':'zato.server.service.internal.security.wss.ChangePassword',
            'zato:security.wss.create':'zato.server.service.internal.security.wss.Create',
            'zato:security.wss.delete':'zato.server.service.internal.security.wss.Delete',
            'zato:security.wss.edit':'zato.server.service.internal.security.wss.Edit',
            'zato:security.wss.get-list':'zato.server.service.internal.security.wss.GetList',

            # HTTP Basic Auth
            'zato:security.basic-auth.change-password':'zato.server.service.internal.security.basic_auth.ChangePassword',
            'zato:security.basic-auth.create':'zato.server.service.internal.security.basic_auth.Create',
            'zato:security.basic-auth.delete':'zato.server.service.internal.security.basic_auth.Delete',
            'zato:security.basic-auth.edit':'zato.server.service.internal.security.basic_auth.Edit',
            'zato:security.basic-auth.get-list':'zato.server.service.internal.security.basic_auth.GetList',

            # Definitions - AMQP
            'zato:definition.amqp.change-password':'zato.server.service.internal.definition.amqp.ChangePassword',
            'zato:definition.amqp.create':'zato.server.service.internal.definition.amqp.Create',
            'zato:definition.amqp.delete':'zato.server.service.internal.definition.amqp.Delete',
            'zato:definition.amqp.edit':'zato.server.service.internal.definition.amqp.Edit',
            'zato:definition.amqp.get-by-id':'zato.server.service.internal.definition.amqp.GetByID',
            'zato:definition.amqp.get-list':'zato.server.service.internal.definition.amqp.GetList',

            # Definitions - JMS WebSphere MQ
            'zato:definition.jms_wmq.create':'zato.server.service.internal.definition.jms_wmq.Create',
            'zato:definition.jms_wmq.delete':'zato.server.service.internal.definition.jms_wmq.Delete',
            'zato:definition.jms_wmq.edit':'zato.server.service.internal.definition.jms_wmq.Edit',
            'zato:definition.jms_wmq.get-by-id':'zato.server.service.internal.definition.jms_wmq.GetByID',
            'zato:definition.jms_wmq.get-list':'zato.server.service.internal.definition.jms_wmq.GetList',

            # Channels - AMQP
            'zato:channel.amqp.create':'zato.server.service.internal.channel.amqp.Create',
            'zato:channel.amqp.delete':'zato.server.service.internal.channel.amqp.Delete',
            'zato:channel.amqp.edit':'zato.server.service.internal.channel.amqp.Edit',
            'zato:channel.amqp.get-list':'zato.server.service.internal.channel.amqp.GetList',

            # Channels - JMS WebSphere MQ
            'zato:channel.jms_wmq.create':'zato.server.service.internal.channel.jms_wmq.Create',
            'zato:channel.jms_wmq.delete':'zato.server.service.internal.channel.jms_wmq.Delete',
            'zato:channel.jms_wmq.edit':'zato.server.service.internal.channel.jms_wmq.Edit',
            'zato:channel.jms_wmq.get-list':'zato.server.service.internal.channel.jms_wmq.GetList',

            # Channels - ZeroMQ
            'zato:channel.zmq.create':'zato.server.service.internal.channel.zmq.Create',
            'zato:channel.zmq.delete':'zato.server.service.internal.channel.zmq.Delete',
            'zato:channel.zmq.edit':'zato.server.service.internal.channel.zmq.Edit',
            'zato:channel.zmq.get-list':'zato.server.service.internal.channel.zmq.GetList',

            # Outgoing connections - AMQP
            'zato:outgoing.amqp.create':'zato.server.service.internal.outgoing.amqp.Create',
            'zato:outgoing.amqp.delete':'zato.server.service.internal.outgoing.amqp.Delete',
            'zato:outgoing.amqp.edit':'zato.server.service.internal.outgoing.amqp.Edit',
            'zato:outgoing.amqp.get-list':'zato.server.service.internal.outgoing.amqp.GetList',
            
            # Outgoing connections - FTP
            'zato:outgoing.ftp.change-password':'zato.server.service.internal.outgoing.ftp.ChangePassword',
            'zato:outgoing.ftp.create':'zato.server.service.internal.outgoing.ftp.Create',
            'zato:outgoing.ftp.delete':'zato.server.service.internal.outgoing.ftp.Delete',
            'zato:outgoing.ftp.edit':'zato.server.service.internal.outgoing.ftp.Edit',
            'zato:outgoing.ftp.get-list':'zato.server.service.internal.outgoing.ftp.GetList',

            # Outgoing connections - JMS WebSphere MQ
            'zato:outgoing.jms_wmq.create':'zato.server.service.internal.outgoing.jms_wmq.Create',
            'zato:outgoing.jms_wmq.delete':'zato.server.service.internal.outgoing.jms_wmq.Delete',
            'zato:outgoing.jms_wmq.edit':'zato.server.service.internal.outgoing.jms_wmq.Edit',
            'zato:outgoing.jms_wmq.get-list':'zato.server.service.internal.outgoing.jms_wmq.GetList',
            
            # Outgoing connections - SQL
            'zato:outgoing.sql.change-password':'zato.server.service.internal.outgoing.sql.ChangePassword',
            'zato:outgoing.sql.create':'zato.server.service.internal.outgoing.sql.Create',
            'zato:outgoing.sql.delete':'zato.server.service.internal.outgoing.sql.Delete',
            'zato:outgoing.sql.edit':'zato.server.service.internal.outgoing.sql.Edit',
            'zato:outgoing.sql.get-list':'zato.server.service.internal.outgoing.sql.GetList',
            'zato:outgoing.sql.ping':'zato.server.service.internal.outgoing.sql.Ping',
            
            # Outgoing connections - ZeroMQ
            'zato:outgoing.zmq.create':'zato.server.service.internal.outgoing.zmq.Create',
            'zato:outgoing.zmq.delete':'zato.server.service.internal.outgoing.zmq.Delete',
            'zato:outgoing.zmq.edit':'zato.server.service.internal.outgoing.zmq.Edit',
            'zato:outgoing.zmq.get-list':'zato.server.service.internal.outgoing.zmq.GetList',

            # HTTP SOAP
            'zato:http_soap.create':'zato.server.service.internal.http_soap.Create',
            'zato:http_soap.delete':'zato.server.service.internal.http_soap.Delete',
            'zato:http_soap.edit':'zato.server.service.internal.http_soap.Edit',
            'zato:http_soap.get-list':'zato.server.service.internal.http_soap.GetList',
            'zato:http_soap.ping':'zato.server.service.internal.http_soap.Ping',
            
            # Key/value DB
            'zato:kvdb.data-dict.dictionary.create':'zato.server.service.internal.kvdb.data_dict.dictionary.Create',
            'zato:kvdb.data-dict.dictionary.delete':'zato.server.service.internal.kvdb.data_dict.dictionary.Delete',
            'zato:kvdb.data-dict.dictionary.edit':'zato.server.service.internal.kvdb.data_dict.dictionary.Edit',
            'zato:kvdb.data-dict.dictionary.get-list':'zato.server.service.internal.kvdb.data_dict.dictionary.GetList',
            'zato:kvdb.data-dict.dictionary.get-key-list':'zato.server.service.internal.kvdb.data_dict.dictionary.GetKeyList',
            'zato:kvdb.data-dict.dictionary.get-last-id':'zato.server.service.internal.kvdb.data_dict.dictionary.GetLastID',
            'zato:kvdb.data-dict.dictionary.get-system-list':'zato.server.service.internal.kvdb.data_dict.dictionary.GetSystemList',
            'zato:kvdb.data-dict.dictionary.get-value-list':'zato.server.service.internal.kvdb.data_dict.dictionary.GetValueList',
            'zato:kvdb.data-dict.translation.create':'zato.server.service.internal.kvdb.data_dict.translation.Create',
            'zato:kvdb.data-dict.translation.delete':'zato.server.service.internal.kvdb.data_dict.translation.Delete',
            'zato:kvdb.data-dict.translation.edit':'zato.server.service.internal.kvdb.data_dict.translation.Edit',
            'zato:kvdb.data-dict.translation.get-list':'zato.server.service.internal.kvdb.data_dict.translation.GetList',
            'zato:kvdb.data-dict.translation.get-last-id':'zato.server.service.internal.kvdb.data_dict.translation.GetLastID',
            'zato:kvdb.data-dict.translation.translate':'zato.server.service.internal.kvdb.data_dict.translation.Translate',
            'zato:kvdb.data-dict.impexp.import':'zato.server.service.internal.kvdb.data_dict.impexp.Import',
            'zato:kvdb.remote-command.execute':'zato.server.service.internal.kvdb.ExecuteCommand',
            
            # Statistics
            'zato:stats.get-top-n':'zato.server.service.internal.stats.GetTopN',
            'zato:stats.get-by-service':'zato.server.service.internal.stats.GetByService',
            'zato:stats.delete':'zato.server.service.internal.stats.Delete',
        }
        
        #
        # HTTPSOAP + services
        #

        zato_soap_channels = []
        
        for soap_action, impl_name in soap_services.iteritems():

            # Make the actual name shorter so it better fits the screen's real estate
            service_name = service_name_from_impl(impl_name)
            
            service = Service(None, service_name, True, impl_name, True, cluster)
            session.add(service)
            
            # Add the HTTP channel for WSDLs
            if impl_name == 'zato.server.service.internal.service.GetWSDL':
                http_soap = HTTPSOAP(None, service_name, True, True, 'channel', 'plain_http', 
                    None, '/zato/wsdl', None, '', None, None, service=service, cluster=cluster)
                session.add(http_soap)
            
            zato_soap = HTTPSOAP(None, soap_action, True, True, 'channel', 
                'soap', None, '/zato/soap', None, soap_action, '1.1', 
                SIMPLE_IO.FORMAT.XML, service=service, cluster=cluster, security=tech_account)
            session.add(zato_soap)
            
            zato_soap_channels.append(zato_soap)
            
    def add_json_services(self, session, cluster, tech_account):
        """ Adds these Zato internal services that can be accessed through JSON
        over plain HTTP.
        """
        json_services = (
            # URL Security
            ('/zato/json/http-soap/url-security', 'zato.server.service.internal.http_soap.GetURLSecurity'),
        )
        
        for url_path, impl_name in json_services:
        
            # Make the actual name shorter so it better fits the screen's real estate
            service_name = service_name_from_impl(impl_name)
            
            service = Service(None, service_name , True, impl_name, True, cluster)
            session.add(service)
        
            http_soap = HTTPSOAP(None, service_name, True, True, 'channel', 'plain_http', 
                None, url_path, None, '', None, SIMPLE_IO.FORMAT.JSON, service=service, cluster=cluster, security=tech_account)
            session.add(http_soap)
            
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
                args.odb_type, args.odb_host, args.odb_port, args.odb_user, args.odb_dbname, 
                args.odb_schema, args.broker_host, args.broker_start_port, cb.token, 'localhost', 20151,  11223)

            #
            # Servers
            #
            server1 = Server(None, 'zato-quickstart-server-01', cluster, cs1.odb_token, SERVER_JOIN_STATUS.ACCEPTED, 
                             datetime.now(), 'zato-quickstart/' + current_host())
            session.add(server1)
            
            server2 = Server(None, 'zato-quickstart-server-02', cluster, cs2.odb_token, SERVER_JOIN_STATUS.ACCEPTED, 
                             datetime.now(), 'zato-quickstart/' + current_host())
            session.add(server2)
            
            #
            # TechnicalAccount for the web admin
            #
            salt = uuid4().hex
            password = tech_account_password(tech_account_password_clear, salt)
            
            tech_account = TechnicalAccount(None, tech_account_name, True, password, salt, cluster)
            session.add(tech_account)
                
            # Ping services
            self.add_ping_services(session, cluster)
            
            # SOAP services
            self.add_soap_services(session, cluster, tech_account)
            
            # JSON services
            self.add_json_services(session, cluster, tech_account)
            
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
