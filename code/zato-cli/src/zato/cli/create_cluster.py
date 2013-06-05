# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from datetime import datetime
from traceback import format_exc
from uuid import uuid4

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.cli import common_odb_opts, get_tech_account_opts, ZatoCommand
from zato.common import SIMPLE_IO
from zato.common.odb.model import Cluster, HTTPBasicAuth, HTTPSOAP, Service, WSSDefinition

zato_services = {

    # Channels - AMQP
    'zato.channel.amqp.create':'zato.server.service.internal.channel.amqp.Create',
    'zato.channel.amqp.delete':'zato.server.service.internal.channel.amqp.Delete',
    'zato.channel.amqp.edit':'zato.server.service.internal.channel.amqp.Edit',
    'zato.channel.amqp.get-list':'zato.server.service.internal.channel.amqp.GetList',

    # Channels - JMS WebSphere MQ
    'zato.channel.jms-wmq.create':'zato.server.service.internal.channel.jms_wmq.Create',
    'zato.channel.jms-wmq.delete':'zato.server.service.internal.channel.jms_wmq.Delete',
    'zato.channel.jms-wmq.edit':'zato.server.service.internal.channel.jms_wmq.Edit',
    'zato.channel.jms-wmq.get-list':'zato.server.service.internal.channel.jms_wmq.GetList',

    # Channels - ZeroMQ
    'zato.channel.zmq.create':'zato.server.service.internal.channel.zmq.Create',
    'zato.channel.zmq.delete':'zato.server.service.internal.channel.zmq.Delete',
    'zato.channel.zmq.edit':'zato.server.service.internal.channel.zmq.Edit',
    'zato.channel.zmq.get-list':'zato.server.service.internal.channel.zmq.GetList',
    
    # Definitions - AMQP
    'zato.definition.amqp.change-password':'zato.server.service.internal.definition.amqp.ChangePassword',
    'zato.definition.amqp.create':'zato.server.service.internal.definition.amqp.Create',
    'zato.definition.amqp.delete':'zato.server.service.internal.definition.amqp.Delete',
    'zato.definition.amqp.edit':'zato.server.service.internal.definition.amqp.Edit',
    'zato.definition.amqp.get-by-id':'zato.server.service.internal.definition.amqp.GetByID',
    'zato.definition.amqp.get-list':'zato.server.service.internal.definition.amqp.GetList',

    # Definitions - JMS WebSphere MQ
    'zato.definition.jms-wmq.create':'zato.server.service.internal.definition.jms_wmq.Create',
    'zato.definition.jms-wmq.delete':'zato.server.service.internal.definition.jms_wmq.Delete',
    'zato.definition.jms-wmq.edit':'zato.server.service.internal.definition.jms_wmq.Edit',
    'zato.definition.jms-wmq.get-by-id':'zato.server.service.internal.definition.jms_wmq.GetByID',
    'zato.definition.jms-wmq.get-list':'zato.server.service.internal.definition.jms_wmq.GetList',
    
    # HTTP/SOAP
    'zato.http-soap.create':'zato.server.service.internal.http_soap.Create',
    'zato.http-soap.delete':'zato.server.service.internal.http_soap.Delete',
    'zato.http-soap.edit':'zato.server.service.internal.http_soap.Edit',
    'zato.http-soap.get-list':'zato.server.service.internal.http_soap.GetList',
    'zato.http-soap.ping':'zato.server.service.internal.http_soap.Ping',
    
    # Key/value DB
    'zato.kvdb.data-dict.dictionary.create':'zato.server.service.internal.kvdb.data_dict.dictionary.Create',
    'zato.kvdb.data-dict.dictionary.delete':'zato.server.service.internal.kvdb.data_dict.dictionary.Delete',
    'zato.kvdb.data-dict.dictionary.edit':'zato.server.service.internal.kvdb.data_dict.dictionary.Edit',
    'zato.kvdb.data-dict.dictionary.get-key-list':'zato.server.service.internal.kvdb.data_dict.dictionary.GetKeyList',
    'zato.kvdb.data-dict.dictionary.get-last-id':'zato.server.service.internal.kvdb.data_dict.dictionary.GetLastID',
    'zato.kvdb.data-dict.dictionary.get-list':'zato.server.service.internal.kvdb.data_dict.dictionary.GetList',
    'zato.kvdb.data-dict.dictionary.get-system-list':'zato.server.service.internal.kvdb.data_dict.dictionary.GetSystemList',
    'zato.kvdb.data-dict.dictionary.get-value-list':'zato.server.service.internal.kvdb.data_dict.dictionary.GetValueList',
    'zato.kvdb.data-dict.impexp.import':'zato.server.service.internal.kvdb.data_dict.impexp.Import',
    'zato.kvdb.data-dict.translation.create':'zato.server.service.internal.kvdb.data_dict.translation.Create',
    'zato.kvdb.data-dict.translation.delete':'zato.server.service.internal.kvdb.data_dict.translation.Delete',
    'zato.kvdb.data-dict.translation.edit':'zato.server.service.internal.kvdb.data_dict.translation.Edit',
    'zato.kvdb.data-dict.translation.get-last-id':'zato.server.service.internal.kvdb.data_dict.translation.GetLastID',
    'zato.kvdb.data-dict.translation.get-list':'zato.server.service.internal.kvdb.data_dict.translation.GetList',
    'zato.kvdb.data-dict.translation.translate':'zato.server.service.internal.kvdb.data_dict.translation.Translate',
    'zato.kvdb.remote-command.execute':'zato.server.service.internal.kvdb.ExecuteCommand',
    
    # Outgoing connections - AMQP
    'zato.outgoing.amqp.create':'zato.server.service.internal.outgoing.amqp.Create',
    'zato.outgoing.amqp.delete':'zato.server.service.internal.outgoing.amqp.Delete',
    'zato.outgoing.amqp.edit':'zato.server.service.internal.outgoing.amqp.Edit',
    'zato.outgoing.amqp.get-list':'zato.server.service.internal.outgoing.amqp.GetList',
    
    # Outgoing connections - FTP
    'zato.outgoing.ftp.change-password':'zato.server.service.internal.outgoing.ftp.ChangePassword',
    'zato.outgoing.ftp.create':'zato.server.service.internal.outgoing.ftp.Create',
    'zato.outgoing.ftp.delete':'zato.server.service.internal.outgoing.ftp.Delete',
    'zato.outgoing.ftp.edit':'zato.server.service.internal.outgoing.ftp.Edit',
    'zato.outgoing.ftp.get-list':'zato.server.service.internal.outgoing.ftp.GetList',

    # Outgoing connections - JMS WebSphere MQ
    'zato.outgoing.jms-wmq.create':'zato.server.service.internal.outgoing.jms_wmq.Create',
    'zato.outgoing.jms-wmq.delete':'zato.server.service.internal.outgoing.jms_wmq.Delete',
    'zato.outgoing.jms-wmq.edit':'zato.server.service.internal.outgoing.jms_wmq.Edit',
    'zato.outgoing.jms-wmq.get-list':'zato.server.service.internal.outgoing.jms_wmq.GetList',
    
    # Outgoing connections - SQL
    'zato.outgoing.sql.change-password':'zato.server.service.internal.outgoing.sql.ChangePassword',
    'zato.outgoing.sql.create':'zato.server.service.internal.outgoing.sql.Create',
    'zato.outgoing.sql.delete':'zato.server.service.internal.outgoing.sql.Delete',
    'zato.outgoing.sql.edit':'zato.server.service.internal.outgoing.sql.Edit',
    'zato.outgoing.sql.get-list':'zato.server.service.internal.outgoing.sql.GetList',
    'zato.outgoing.sql.ping':'zato.server.service.internal.outgoing.sql.Ping',
    
    # Outgoing connections - ZeroMQ
    'zato.outgoing.zmq.create':'zato.server.service.internal.outgoing.zmq.Create',
    'zato.outgoing.zmq.delete':'zato.server.service.internal.outgoing.zmq.Delete',
    'zato.outgoing.zmq.edit':'zato.server.service.internal.outgoing.zmq.Edit',
    'zato.outgoing.zmq.get-list':'zato.server.service.internal.outgoing.zmq.GetList',
    
    # Patterns - delivery
    'zato.pattern.delivery.definition.create':'zato.server.service.internal.pattern.delivery.definition.Create',
    'zato.pattern.delivery.definition.delete':'zato.server.service.internal.pattern.delivery.definition.Delete',
    'zato.pattern.delivery.definition.edit':'zato.server.service.internal.pattern.delivery.definition.Edit',
    'zato.pattern.delivery.definition.get-list':'zato.server.service.internal.pattern.delivery.definition.GetList',
    
    # Ping services are added in Create.add_ping_services

    # Scheduler
    'zato.scheduler.job.create':'zato.server.service.internal.scheduler.Create',
    'zato.scheduler.job.delete':'zato.server.service.internal.scheduler.Delete',
    'zato.scheduler.job.edit':'zato.server.service.internal.scheduler.Edit',
    'zato.scheduler.job.execute':'zato.server.service.internal.scheduler.Execute',
    'zato.scheduler.job.get-by-name':'zato.server.service.internal.scheduler.GetByName',
    'zato.scheduler.job.get-list':'zato.server.service.internal.scheduler.GetList',

    # Security
    'zato.security.get-list':'zato.server.service.internal.security.GetList',

    # Security - HTTP Basic Auth
    'zato.security.basic-auth.change-password':'zato.server.service.internal.security.basic_auth.ChangePassword',
    'zato.security.basic-auth.create':'zato.server.service.internal.security.basic_auth.Create',
    'zato.security.basic-auth.delete':'zato.server.service.internal.security.basic_auth.Delete',
    'zato.security.basic-auth.edit':'zato.server.service.internal.security.basic_auth.Edit',
    'zato.security.basic-auth.get-list':'zato.server.service.internal.security.basic_auth.GetList',

    # Security - Technical accounts
    'zato.security.tech-account.change-password':'zato.server.service.internal.security.tech_account.ChangePassword',
    'zato.security.tech-account.create':'zato.server.service.internal.security.tech_account.Create',
    'zato.security.tech-account.delete':'zato.server.service.internal.security.tech_account.Delete',
    'zato.security.tech-account.edit':'zato.server.service.internal.security.tech_account.Edit',
    'zato.security.tech-account.get-by-id':'zato.server.service.internal.security.tech_account.GetByID',
    'zato.security.tech-account.get-list':'zato.server.service.internal.security.tech_account.GetList',

    # Security - WS-Security
    'zato.security.wss.change-password':'zato.server.service.internal.security.wss.ChangePassword',
    'zato.security.wss.create':'zato.server.service.internal.security.wss.Create',
    'zato.security.wss.delete':'zato.server.service.internal.security.wss.Delete',
    'zato.security.wss.edit':'zato.server.service.internal.security.wss.Edit',
    'zato.security.wss.get-list':'zato.server.service.internal.security.wss.GetList',
    
    # Servers
    'zato.server.delete':'zato.server.service.internal.server.Delete',
    'zato.server.edit':'zato.server.service.internal.server.Edit',
    'zato.server.get-by-id':'zato.server.service.internal.server.GetByID',
    
    # Services
    'zato.service.configure-request-response':'zato.server.service.internal.service.ConfigureRequestResponse',
    'zato.service.delete':'zato.server.service.internal.service.Delete',
    'zato.service.edit':'zato.server.service.internal.service.Edit',
    'zato.service.get-by-name':'zato.server.service.internal.service.GetByName',
    'zato.service.get-channel-list':'zato.server.service.internal.service.GetChannelList',
    'zato.service.get-deployment-info-list':'zato.server.service.internal.service.GetDeploymentInfoList',
    'zato.service.get-list':'zato.server.service.internal.service.GetList',
    'zato.service.get-request-response':'zato.server.service.internal.service.GetRequestResponse',
    'zato.service.get-source-info':'zato.server.service.internal.service.GetSourceInfo',
    'zato.service.get-wsdl':'zato.server.service.internal.service.GetWSDL',
    'zato.service.has-wsdl':'zato.server.service.internal.service.HasWSDL',
    'zato.service.invoke':'zato.server.service.internal.service.Invoke',
    'zato.service.set-wsdl':'zato.server.service.internal.service.SetWSDL',
    'zato.service.slow-response.get':'zato.server.service.internal.service.GetSlowResponse',
    'zato.service.slow-response.get-list':'zato.server.service.internal.service.GetSlowResponseList',
    'zato.service.upload-package':'zato.server.service.internal.service.UploadPackage',

    # Statistics
    'zato.stats.delete':'zato.server.service.internal.stats.Delete',
    'zato.stats.get-by-service':'zato.server.service.internal.stats.GetByService',
    'zato.stats.summary.get-summary-by-day':'zato.server.service.internal.stats.summary.GetSummaryByDay',
    'zato.stats.summary.get-summary-by-month':'zato.server.service.internal.stats.summary.GetSummaryByMonth',
    'zato.stats.summary.get-summary-by-range':'zato.server.service.internal.stats.summary.GetSummaryByRange',
    'zato.stats.summary.get-summary-by-week':'zato.server.service.internal.stats.summary.GetSummaryByWeek',
    'zato.stats.summary.get-summary-by-year':'zato.server.service.internal.stats.summary.GetSummaryByYear',
    'zato.stats.trends.get-trends':'zato.server.service.internal.stats.trends.GetTrends',
}

class Create(ZatoCommand):
    """ Creates a new Zato cluster in the ODB
    """
    opts = deepcopy(common_odb_opts)
    
    opts.append({'name':'lb_host', 'help':"Load-balancer host"})
    opts.append({'name':'lb_port', 'help':'Load-balancer port'})
    opts.append({'name':'lb_agent_port', 'help':'Load-balancer agent host'})
    opts.append({'name':'broker_host', 'help':"Redis host"})
    opts.append({'name':'broker_port', 'help':'Redis port'})
    opts.append({'name':'cluster_name', 'help':'Name of the cluster to create'})
    
    opts += get_tech_account_opts('for web admin instances to use')
    
    def execute(self, args, show_output=True):
        
        engine = self._get_engine(args)
        session = self._get_session(engine)
        
        cluster = Cluster()
        cluster.name = args.cluster_name
        cluster.description = 'Created by {} on {} (UTC)'.format(self._get_user_host(), datetime.utcnow().isoformat())
        
        for name in(
              'odb_type', 'odb_host', 'odb_port', 'odb_user', 'odb_db_name',
              'broker_host', 'broker_port', 'lb_host', 'lb_port', 'lb_agent_port'):
            setattr(cluster, name, getattr(args, name))
        session.add(cluster)
        
        # TODO: getattrs below should be squared away - one of the attrs should win
        #       and the other one should be get ridden of.
        admin_invoke_sec = HTTPBasicAuth(None, 'admin.invoke', True, 'admin.invoke', 'Zato admin invoke', getattr(args, 'admin_invoke_password', None) or getattr(args, 'tech_account_password'), cluster)
        session.add(admin_invoke_sec)
        
        pubapi_sec = HTTPBasicAuth(None, 'pubapi', True, 'pubapi', 'Zato public API', uuid4().hex, cluster)
        session.add(pubapi_sec)
        
        self.add_soap_services(session, cluster, admin_invoke_sec, pubapi_sec)
        self.add_ping_services(session, cluster)
        
        try:
            session.commit()
        except IntegrityError, e:
            msg = 'Cluster name [{}] already exists'.format(cluster.name)
            if self.verbose:
                msg += '. Caught an exception:[{}]'.format(format_exc(e))
                self.logger.error(msg)
            self.logger.error(msg)
            session.rollback()
            
            return self.SYS_ERROR.CLUSTER_NAME_ALREADY_EXISTS

        if show_output:
            if self.verbose:
                msg = 'Successfully created a new cluster [{}]'.format(args.cluster_name)
                self.logger.debug(msg)
            else:
                self.logger.info('OK')
            
    def add_soap_services(self, session, cluster, admin_invoke_sec, pubapi_sec):
        """ Adds these Zato internal services that can be accessed through SOAP requests.
        """
        
        #
        # HTTPSOAP + services
        #
        
        for name, impl_name in zato_services.iteritems():
            
            service = Service(None, name, True, impl_name, True, cluster)
            session.add(service)
            
            # Add the HTTP channel for WSDLs
            if name == 'zato.service.get-wsdl':
                http_soap = HTTPSOAP(
                    None, '{}.soap'.format(name), True, True, 'channel', 'plain_http',
                    None, '/zato/wsdl', None, '', None, None, service=service, cluster=cluster)
                session.add(http_soap)
                
            elif name == 'zato.service.invoke':
                self.add_admin_invoke(session, cluster, service, admin_invoke_sec)

            zato_soap = HTTPSOAP(
                None, name, True, True, 'channel',
                'soap', None, '/zato/soap', None, name, '1.1',
                SIMPLE_IO.FORMAT.XML, service=service, cluster=cluster, security=pubapi_sec)
            session.add(zato_soap)

            json_url_path = '/zato/json/{}'.format(name)
            json_http = HTTPSOAP(
                None, '{}.json'.format(name), True, True, 'channel', 'plain_http',
                None, json_url_path, None, '', None, SIMPLE_IO.FORMAT.JSON, service=service, cluster=cluster, security=pubapi_sec)
            session.add(json_http)

    def add_ping_services(self, session, cluster):
        """ Adds a ping service and channels, with and without security checks.
        """
        passwords = {
            'ping.plain_http.basic_auth': None,
            'ping.soap.basic_auth': None,
            'ping.soap.wss.clear_text': None,
        }
        
        for password in passwords:
            passwords[password] = uuid4().hex

        ping_impl_name = 'zato.server.service.internal.Ping'
        ping_service_name = 'zato.ping'
        ping_service = Service(None, ping_service_name, True, ping_impl_name, True, cluster)
        session.add(ping_service)
        
        #
        # .. no security ..
        #
        # TODO
        # Change it to /zato/json/ping
        # and add an actual /zato/ping with no data format specified.
        ping_no_sec_channel = HTTPSOAP(
            None, 'zato.ping', True, True, 'channel',
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
            
            channel = HTTPSOAP(
                None, zato_name, True, True, 'channel', transport, None, url, None, soap_action,
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
                    
                    channel = HTTPSOAP(
                        None, zato_name, True, True, 'channel', transport, None, url, None, soap_action,
                        soap_version, data_format, service=ping_service, security=sec, cluster=cluster)
                    session.add(channel)

    def add_admin_invoke(self, session, cluster, service, admin_invoke_sec):
        """ Adds an admin channel for invoking services from web admin and CLI.
        """
        channel = HTTPSOAP(
            None, 'admin.invoke.json', True, True, 'channel', 'plain_http',
            None, '/zato/admin/invoke', None, '', None, SIMPLE_IO.FORMAT.JSON, service=service, cluster=cluster,
            security=admin_invoke_sec)
        session.add(channel)
