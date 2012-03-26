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
import asyncore, logging, time
from httplib import INTERNAL_SERVER_ERROR, responses
from threading import Thread
from time import sleep
from traceback import format_exc

# zope.server
from zope.server.http.httpserver import HTTPServer

# ZeroMQ
import zmq

# Paste
from paste.util.multidict import MultiDict

# Bunch
from bunch import Bunch, SimpleBunch

# Zato
from zato.broker.zato_client import BrokerClient
from zato.common import PORTS, ZATO_JOIN_REQUEST_ACCEPTED, ZATO_ODB_POOL_NAME
from zato.common.broker_message import AMQP_CONNECTOR, JMS_WMQ_CONNECTOR, ZMQ_CONNECTOR, MESSAGE_TYPE
from zato.common.util import new_cid
from zato.server.base import BrokerMessageReceiver
from zato.server.base.worker import _HTTPServerChannel, _TaskDispatcher
from zato.server.config import ConfigDict, ConfigStore
from zato.server.connection.amqp.channel import start_connector as amqp_channel_start_connector
from zato.server.connection.amqp.outgoing import start_connector as amqp_out_start_connector
from zato.server.connection.jms_wmq.channel import start_connector as jms_wmq_channel_start_connector
from zato.server.connection.jms_wmq.outgoing import start_connector as jms_wmq_out_start_connector
from zato.server.connection.zmq_.channel import start_connector as zmq_channel_start_connector
from zato.server.connection.zmq_.outgoing import start_connector as zmq_outgoing_start_connector

logger = logging.getLogger(__name__)

class ZatoHTTPListener(HTTPServer):
    
    SERVER_IDENT = 'Zato'
    channel_class = _HTTPServerChannel
    
    def __init__(self, server, task_dispatcher, broker_client=None):
        self.server = server
        self.broker_client = broker_client
        super(ZatoHTTPListener, self).__init__(self.server.host, self.server.port, 
                                               task_dispatcher)

    def executeRequest(self, task, thread_local_ctx):
        """ Handles incoming HTTP requests. Each request is being handled by one
        of the threads created in ParallelServer.run_forever method.
        """
        cid = new_cid()
        
        try:
            # SOAP or plain HTTP.
            payload = thread_local_ctx.store.request_handler.handle(cid, task, thread_local_ctx)

        # Any exception at this point must be our fault.
        except Exception, e:
            tb = format_exc(e)
            task.setResponseStatus(INTERNAL_SERVER_ERROR, responses[INTERNAL_SERVER_ERROR])
            error_msg = '[{0}] Exception caught [{1}]'.format(cid, tb)
            logger.error(error_msg)
            
            payload = error_msg
            task.response_headers['Content-Type'] = 'text/plain'
            
        task.response_headers['X-Zato-CID'] = cid
            
        # Can't set it any earlier, this is the only place we're sure the payload
        # won't be modified anymore.
        task.response_headers['Content-Length'] = str(len(payload))
        task.write(payload)


class ParallelServer(BrokerMessageReceiver):
    def __init__(self, host=None, port=None, zmq_context=None, crypto_manager=None,
                 odb=None, odb_data=None, singleton_server=None, worker_config=None, 
                 repo_location=None, ftp=None, sql_pool_store=None, int_parameters=None, 
                 int_parameter_suffixes=None, bool_parameter_prefixes=None,
                 soap11_content_type=None, soap12_content_type=None, 
                 plain_xml_content_type=None, json_content_type=None):
        self.host = host
        self.port = port
        self.zmq_context = zmq_context or zmq.Context()
        self.crypto_manager = crypto_manager
        self.odb = odb
        self.odb_data = odb_data
        self.singleton_server = singleton_server
        self.config = worker_config
        self.repo_location = repo_location
        self.ftp = ftp
        self.sql_pool_store = sql_pool_store
        self.int_parameters = int_parameters
        self.int_parameter_suffixes = int_parameter_suffixes
        self.bool_parameter_prefixes = bool_parameter_prefixes
        self.soap11_content_type = soap11_content_type
        self.soap12_content_type = soap12_content_type
        self.plain_xml_content_type = plain_xml_content_type
        self.json_content_type = json_content_type
        
        # The main config store
        self.config = ConfigStore()
        
    def _after_init_common(self, server):
        """ Initializes parts of the server that don't depend on whether the
        server's been allowed to join the cluster or not.
        """
        
        self.broker_token = server.cluster.broker_token
        self.broker_push_worker_pull = 'tcp://{0}:{1}'.format(server.cluster.broker_host, 
                server.cluster.broker_start_port + PORTS.BROKER_PUSH_WORKER_THREAD_PULL)
        self.worker_push_broker_pull = self.parallel_push_broker_pull = 'tcp://{0}:{1}'.format(server.cluster.broker_host, 
                server.cluster.broker_start_port + PORTS.WORKER_THREAD_PUSH_BROKER_PULL)
        self.broker_pub_worker_sub = 'tcp://{0}:{1}'.format(server.cluster.broker_host, 
                server.cluster.broker_start_port + PORTS.BROKER_PUB_WORKER_THREAD_SUB)
        
        if self.singleton_server:
            
            self.service_store.read_internal_services()
            
            kwargs = {'zmq_context':self.zmq_context,
            'broker_host': server.cluster.broker_host,
            'broker_push_singleton_pull_port': server.cluster.broker_start_port + PORTS.BROKER_PUSH_SINGLETON_PULL,
            'singleton_push_broker_pull_port': server.cluster.broker_start_port + PORTS.SINGLETON_PUSH_BROKER_PULL,
            'broker_token':self.broker_token,
                    }
            Thread(target=self.singleton_server.run, kwargs=kwargs).start()
            
            # Let the scheduler fully initialize
            self.singleton_server.scheduler.wait_for_init()
    
    def _after_init_accepted(self, server):
        if self.singleton_server:
            for(_, name, is_active, job_type, start_date, extra, service,\
                _, weeks, days, hours, minutes, seconds, repeats, cron_definition)\
                    in self.odb.get_job_list(server.cluster.id):
                if is_active:
                    job_data = SimpleBunch({'name':name, 'is_active':is_active, 
                        'job_type':job_type, 'start_date':start_date, 
                        'extra':extra, 'service':service,  'weeks':weeks, 
                        'days':days, 'hours':hours, 'minutes':minutes, 
                        'seconds':seconds,  'repeats':repeats, 
                        'cron_definition':cron_definition})
                    self.singleton_server.scheduler.create_edit('create', job_data)

            # Start the connectors only once throughout the whole cluster
            self._init_connectors(server)
            
            
        # Repo location so that AMQP subprocesses know where to read
        # the server's configuration from.
        self.config.repo_location = self.repo_location
        
        #
        # Outgoing connections - start
        # 
            
        # FTP
        query = self.odb.get_out_ftp_list(server.cluster.id, True)
        self.config.out_ftp = ConfigDict.from_query('out_ftp', query)
        
        # Plain HTTP
        query = self.odb.get_http_soap_list(server.cluster.id, 'outgoing', 'plain_http', True)
        self.config.out_plain_http = ConfigDict.from_query('out_plain_http', query)
        
        # SOAP
        query = self.odb.get_http_soap_list(server.cluster.id, 'outgoing', 'soap', True)
        self.config.out_soap = ConfigDict.from_query('out_soap', query)

        # SQL
        query = self.odb.get_out_sql_list(server.cluster.id, True)
        self.config.out_sql = ConfigDict.from_query('out_sql', query)
        
        # AMQP
        query = self.odb.get_out_amqp_list(server.cluster.id, True)
        self.config.out_amqp = ConfigDict.from_query('out_amqp', query)
        
        # JMS WMQ
        query = self.odb.get_out_jms_wmq_list(server.cluster.id, True)
        self.config.out_jms_wmq = ConfigDict.from_query('out_jms_wmq', query)
        
        # ZMQ
        query = self.odb.get_out_zmq_list(server.cluster.id, True)
        self.config.out_zmq = ConfigDict.from_query('out_zmq', query)
        
        #
        # Outgoing connections - end
        # 

        # HTTP Basic Auth
        query = self.odb.get_basic_auth_list(server.cluster.id, True)
        self.config.basic_auth = ConfigDict.from_query('basic_auth', query)
        
        # Technical accounts
        query = self.odb.get_tech_acc_list(server.cluster.id, True)
        self.config.tech_acc = ConfigDict.from_query('tech_acc', query)
        
        # WS-Security
        query = self.odb.get_wss_list(server.cluster.id, True)
        self.config.wss = ConfigDict.from_query('wss', query)
        
        # Security configuration of HTTP URLs
        self.config.url_sec = self.odb.get_url_security(server)
        
        # The broker client for each of the worker threads.
        self.config.broker_config = Bunch()
        self.config.broker_config.name = 'worker-thread'
        self.config.broker_config.broker_token = self.broker_token
        self.config.broker_config.zmq_context = self.zmq_context
        self.config.broker_config.broker_push_client_pull = self.broker_push_worker_pull
        self.config.broker_config.client_push_broker_pull = self.worker_push_broker_pull
        self.config.broker_config.broker_pub_client_sub = self.broker_pub_worker_sub
        
        # All the HTTP/SOAP channels.
        http_soap = MultiDict()
        for item in self.odb.get_http_soap_list(server.cluster.id, 'channel'):
            _info = SimpleBunch()
            _info[item.soap_action] = SimpleBunch()
            _info[item.soap_action].id = item.id
            _info[item.soap_action].name = item.name
            _info[item.soap_action].is_internal = item.is_internal
            _info[item.soap_action].url_path = item.url_path
            _info[item.soap_action].method = item.method
            _info[item.soap_action].soap_version = item.soap_version
            _info[item.soap_action].service_id = item.service_id
            _info[item.soap_action].service_name = item.service_name
            _info[item.soap_action].impl_name = item.impl_name
            _info[item.soap_action].transport = item.transport
            _info[item.soap_action].connection = item.connection
            http_soap.add(item.url_path, _info)
            
        self.config.http_soap = http_soap
        
        # SimpleIO
        self.config.simple_io = ConfigDict('simple_io', Bunch())
        self.config.simple_io['int_parameters'] = self.int_parameters
        self.config.simple_io['int_parameter_suffixes'] = self.int_parameter_suffixes
        self.config.simple_io['bool_parameter_prefixes'] = self.bool_parameter_prefixes

        # The parallel server's broker client. The client's used to notify
        # all the server's AMQP subprocesses that they need to shut down.

        self.broker_client = BrokerClient()
        self.broker_client.name = 'parallel'
        self.broker_client.token = server.cluster.broker_token
        self.broker_client.zmq_context = self.zmq_context
        self.broker_client.client_push_broker_pull = self.parallel_push_broker_pull
        
        self.broker_client.init()
        self.broker_client.start()
        
    def _init_connectors(self, server):
        """ Starts all the connector subprocesses.
        """

        # AMQP - channels    
        for item in self.odb.get_channel_amqp_list(server.cluster.id):
            amqp_channel_start_connector(self.repo_location, item.id, item.def_id)
        
        # AMQP - outgoing
        for item in self.odb.get_out_amqp_list(server.cluster.id):
            amqp_out_start_connector(self.repo_location, item.id, item.def_id)
            
        # JMS WMQ - channels
        for item in self.odb.get_channel_jms_wmq_list(server.cluster.id):
            jms_wmq_channel_start_connector(self.repo_location, item.id, item.def_id)
    
        # JMS WMQ - outgoing
        for item in self.odb.get_out_jms_wmq_list(server.cluster.id):
            jms_wmq_out_start_connector(self.repo_location, item.id, item.def_id)
            
        # ZMQ - channels
        for item in self.odb.get_channel_zmq_list(server.cluster.id):
            zmq_channel_start_connector(self.repo_location, item.id)
            
        # ZMQ - outgoimg
        for item in self.odb.get_out_zmq_list(server.cluster.id):
            zmq_outgoing_start_connector(self.repo_location, item.id)
            
    def _after_init_non_accepted(self, server):
        pass    
        
    def after_init(self):
        
        # Store the ODB configuration, create an ODB connection pool and have self.odb use it
        self.config.odb_data = Bunch()
        self.config.odb_data.db_name = self.odb_data['db_name']
        self.config.odb_data.engine = self.odb_data['engine']
        self.config.odb_data.extra = self.odb_data['extra']
        self.config.odb_data.host = self.odb_data['host']
        self.config.odb_data.password = self.crypto_manager.decrypt(self.odb_data['password'])
        self.config.odb_data.pool_size = self.odb_data['pool_size']
        self.config.odb_data.username = self.odb_data['username']
        self.config.odb_data.is_odb = True
        
        # This is the call that creates an SQLAlchemy connection
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.config.odb_data
        
        self.odb.server = self
        self.odb.odb_token = self.odb_data['token']
        
        # Now try grabbing the basic server's data from the ODB. No point
        # in doing anything else if we can't get past this point.
        server = self.odb.fetch_server()
        
        if not server:
            raise Exception('Server does not exist in the ODB')
        
        self._after_init_common(server)
        
        # A server which hasn't been approved in the cluster still needs to fetch
        # all the config data but it won't start any MQ/AMQP/ZMQ/etc. listeners
        # except for a ZMQ config subscriber that will listen for an incoming approval.
        
        if server.last_join_status == ZATO_JOIN_REQUEST_ACCEPTED:
            self._after_init_accepted(server)
        else:
            msg = 'Server has not been accepted, last_join_status=[{0}]'
            logger.warn(msg.format(server.last_join_status))
            
            self._after_init_non_accepted(server)

    def run_forever(self):
        
        task_dispatcher = _TaskDispatcher(self, self.config, self.on_broker_msg, self.zmq_context)
        task_dispatcher.setThreadCount(1) # TODO: Make it configurable

        logger.debug('host=[{0}], port=[{1}]'.format(self.host, self.port))

        ZatoHTTPListener(self, task_dispatcher)

        try:
            while True:
                asyncore.poll(5)

        except KeyboardInterrupt:
            logger.info('Shutting down')

            # Close all the connector subprocesses this server has started
            pairs = ((AMQP_CONNECTOR.CLOSE, MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB),
                    (JMS_WMQ_CONNECTOR.CLOSE, MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_SUB),
                    (ZMQ_CONNECTOR.CLOSE, MESSAGE_TYPE.TO_ZMQ_CONNECTOR_SUB),
                    )
            
            for action, msg_type in pairs:
                msg = {}
                msg['action'] = action
                msg['odb_token'] = self.odb.odb_token
                self.broker_client.send_json(msg, msg_type=msg_type)
                time.sleep(0.2)
            
            self.broker_client.close()
            
            if self.singleton_server:
                if getattr(self.singleton_server, 'broker_client', None):
                    self.singleton_server.broker_client.close()
                
            self.zmq_context.term()
            self.odb.close()
            task_dispatcher.shutdown()

# ##############################################################################
