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
import asyncore, logging, os, time
from datetime import datetime
from httplib import INTERNAL_SERVER_ERROR, responses
from threading import Thread
from time import sleep
from traceback import format_exc

# Bunch
from bunch import Bunch, SimpleBunch

# Paste
from paste.util.multidict import MultiDict

# Zato
from zato.broker.client import BrokerClient
from zato.common import SERVER_JOIN_STATUS, SERVER_UP_STATUS, ZATO_ODB_POOL_NAME
from zato.common.broker_message import AMQP_CONNECTOR, code_to_name, HOT_DEPLOY, JMS_WMQ_CONNECTOR, MESSAGE_TYPE, TOPICS, ZMQ_CONNECTOR
from zato.common.util import new_cid
from zato.server.base import BrokerMessageReceiver
from zato.server.base.worker import WorkerStore
from zato.server.config import ConfigDict, ConfigStore
from zato.server.connection.amqp.channel import start_connector as amqp_channel_start_connector
from zato.server.connection.amqp.outgoing import start_connector as amqp_out_start_connector
from zato.server.connection.jms_wmq.channel import start_connector as jms_wmq_channel_start_connector
from zato.server.connection.jms_wmq.outgoing import start_connector as jms_wmq_out_start_connector
from zato.server.connection.zmq_.channel import start_connector as zmq_channel_start_connector
from zato.server.connection.zmq_.outgoing import start_connector as zmq_outgoing_start_connector
from zato.server.stats import add_stats_jobs

logger = logging.getLogger(__name__)

class ParallelServer(BrokerMessageReceiver):
    def __init__(self, host=None, port=None, crypto_manager=None,
                 odb=None, odb_data=None, singleton_server=None, worker_config=None, 
                 repo_location=None, sql_pool_store=None, int_parameters=None, 
                 int_parameter_suffixes=None, bool_parameter_prefixes=None,
                 soap11_content_type=None, soap12_content_type=None, 
                 plain_xml_content_type=None, json_content_type=None,
                 internal_service_modules=None, service_modules=None, base_dir=None,
                 hot_deploy_config=None, pickup=None, fs_server_config=None, connector_server_grace_time=None,
                 id=None, name=None, cluster_id=None, kvdb=None, stats_jobs=None, worker_store=None):
        self.host = host
        self.port = port
        self.crypto_manager = crypto_manager
        self.odb = odb
        self.odb_data = odb_data
        self.singleton_server = singleton_server
        self.config = worker_config
        self.repo_location = repo_location
        self.sql_pool_store = sql_pool_store
        self.int_parameters = int_parameters
        self.int_parameter_suffixes = int_parameter_suffixes
        self.bool_parameter_prefixes = bool_parameter_prefixes
        self.soap11_content_type = soap11_content_type
        self.soap12_content_type = soap12_content_type
        self.plain_xml_content_type = plain_xml_content_type
        self.json_content_type = json_content_type
        self.internal_service_modules = internal_service_modules
        self.service_modules = service_modules
        self.base_dir = base_dir
        self.hot_deploy_config = hot_deploy_config
        self.pickup = pickup
        self.fs_server_config = fs_server_config
        self.connector_server_grace_time = connector_server_grace_time
        self.id = id
        self.name = name
        self.cluster_id = cluster_id
        self.kvdb = kvdb
        self.stats_jobs = stats_jobs
        self.worker_store = worker_store
        
        # The main config store
        self.config = ConfigStore()
        
    def __call__(self, wsgi_environ, start_response):
        """ Handles incoming HTTP requests. Each request is being handled by one
        of the threads created in ParallelServer.run_forever method.
        """
        cid = new_cid()
        
        try:
            payload = self.worker_store.request_dispatcher.dispatch(cid, datetime.utcnow(), wsgi_environ)
        # Any exception at this point must be our fault
        except Exception, e:
            tb = format_exc(e)
            status = b'{} {}'.format(INTERNAL_SERVER_ERROR, responses[INTERNAL_SERVER_ERROR])
            error_msg = b'[{0}] Exception caught [{1}]'.format(cid, tb)
            logger.error(error_msg)
            payload = error_msg
            
        print(wsgi_environ)
            
        #headers = ((k.encode('utf-8'), v.encode('utf-8')) for k, v in wsgi_environ['zato.http.response.headers'].items())
        #start_response(wsgi_environ['zato.http.response.status'], headers)
        
        start_response('200 OK', {})
        
        return [payload]
        
    def _after_init_common(self, server):
        """ Initializes parts of the server that don't depend on whether the
        server's been allowed to join the cluster or not.
        """
        # .. Remove all the deployed services from the DB ..
        self.odb.drop_deployed_services(server.id)
        
        # .. and re-deploy the back from a clear state.
        self.service_store.import_services_from_anywhere(
            self.internal_service_modules + self.service_modules, self.base_dir)
        
        # Add the statistics-related scheduler jobs to the ODB
        add_stats_jobs(self.cluster_id, self.odb, self.stats_jobs)
        
        # Key-value DB
        self.kvdb.config = self.fs_server_config.kvdb
        self.kvdb.server = self
        self.kvdb.init()

        callbacks = {
            MESSAGE_TYPE.TO_SINGLETON: self.on_broker_msg_singleton,
            }
        
        
        self.broker_client = BrokerClient(self.kvdb, 'parallel') # TODO: Actually use the broker host from config
        self.broker_client.start()
        
        if self.singleton_server:
        
            #self.broker_client.subscribe(TOPICS[MESSAGE_TYPE.TO_SINGLETON])
            
            # Normalize hot-deploy configuration
            if not self.hot_deploy_config:
                self.hot_deploy_config = Bunch()
                self.hot_deploy_config.work_dir = os.path.normpath(os.path.join(
                    self.repo_location, self.fs_server_config.hot_deploy.work_dir))
                self.hot_deploy_config.backup_history = int(self.fs_server_config.hot_deploy.backup_history)
                self.hot_deploy_config.backup_format = self.fs_server_config.hot_deploy.backup_format
                self.hot_deploy_config.current_work_dir = os.path.normpath(os.path.join(
                    self.hot_deploy_config.work_dir, self.fs_server_config.hot_deploy.current_work_dir))
                self.hot_deploy_config.backup_work_dir = os.path.normpath(os.path.join(
                    self.hot_deploy_config.work_dir, self.fs_server_config.hot_deploy.backup_work_dir))
                self.hot_deploy_config.last_backup_work_dir = os.path.normpath(
                    os.path.join(
                        self.hot_deploy_config.work_dir, self.fs_server_config.hot_deploy.last_backup_work_dir))
                
            kwargs = {'broker_client':self.broker_client}
            Thread(target=self.singleton_server.run, kwargs=kwargs).start()
            
            # Let the scheduler fully initialize
            self.singleton_server.scheduler.wait_for_init()
            self.singleton_server.server_id = server.id
    
    def _after_init_accepted(self, server):
        
        if self.singleton_server:
            for(_, name, is_active, job_type, start_date, extra, service_name, service_impl_name,
                _, weeks, days, hours, minutes, seconds, repeats, cron_definition)\
                    in self.odb.get_job_list(server.cluster.id):
                if is_active:
                    job_data = SimpleBunch({'name':name, 'is_active':is_active, 
                        'job_type':job_type, 'start_date':start_date, 
                        'extra':extra, 'service':service_impl_name, 'weeks':weeks, 
                        'days':days, 'hours':hours, 'minutes':minutes, 
                        'seconds':seconds,  'repeats':repeats, 
                        'cron_definition':cron_definition})
                    self.singleton_server.scheduler.create_edit('create', job_data)
                    

            # Let's see if we can become a connector server, the one to start all
            # the connectors, and start the connectors only once throughout the whole cluster.
            self.connector_server_keep_alive_job_time = int(
                self.fs_server_config.singleton.connector_server_keep_alive_job_time)
            self.connector_server_grace_time = int(
                self.fs_server_config.singleton.grace_time_multiplier) * self.connector_server_keep_alive_job_time
            
            if self.singleton_server.become_cluster_wide(
                self.connector_server_keep_alive_job_time, self.connector_server_grace_time, 
                server.id, server.cluster_id, True):
                self.init_connectors()
                
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
        #self.config.url_sec = self.odb.get_url_security(server.cluster.id)
        
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
        
        self.worker_store = WorkerStore(self.config, self)
        self.worker_store._init()
        
        for x in range(2):
            time.sleep(1)
            print('sleep', x)
        
        for x in range(2000):
            self.broker_client.publish({'payload':'aaa', 'action':'10203'})
            print(x)
        
    def init_connectors(self):
        """ Starts all the connector subprocesses.
        """
        logger.info('Initializing connectors')

        # AMQP - channels    
        channel_amqp_list = self.odb.get_channel_amqp_list(self.cluster_id)
        if channel_amqp_list:
            for item in channel_amqp_list:
                amqp_channel_start_connector(self.repo_location, item.id, item.def_id)
        else:
            logger.info('No AMQP channels to start')
        
        # AMQP - outgoing
        out_amqp_list = self.odb.get_out_amqp_list(self.cluster_id)
        if out_amqp_list:
            for item in out_amqp_list:
                amqp_out_start_connector(self.repo_location, item.id, item.def_id)
        else:
            logger.info('No AMQP outgoing connections to start')
            
        # JMS WMQ - channels
        channel_jms_wmq_list = self.odb.get_channel_jms_wmq_list(self.cluster_id)
        if channel_jms_wmq_list:
            for item in channel_jms_wmq_list:
                jms_wmq_channel_start_connector(self.repo_location, item.id, item.def_id)
        else:
            logger.info('No JMS WebSphere MQ channels to start')
    
        # JMS WMQ - outgoing
        out_jms_wmq_list = self.odb.get_out_jms_wmq_list(self.cluster_id)
        if out_jms_wmq_list:
            for item in out_jms_wmq_list:
                jms_wmq_out_start_connector(self.repo_location, item.id, item.def_id)
        else:
            logger.info('No JMS WebSphere MQ outgoing connections to start')
            
        # ZMQ - channels
        channel_zmq_list = self.odb.get_channel_zmq_list(self.cluster_id)
        if channel_zmq_list:
            for item in channel_zmq_list:
                zmq_channel_start_connector(self.repo_location, item.id)
        else:
            logger.info('No Zero MQ channels to start')
            
        # ZMQ - outgoimg
        out_zmq_list = self.odb.get_out_zmq_list(self.cluster_id)
        if out_zmq_list:
            for item in out_zmq_list:
                zmq_outgoing_start_connector(self.repo_location, item.id)
        else:
            logger.info('No Zero MQ outgoing connections to start')
            
    def _after_init_non_accepted(self, server):
        raise NotImplementedError("This Zato version doesn't support join states other than ACCEPTED")
        
    @staticmethod
    def post_fork(arbiter, worker):
        """ A Gunicorn hook.
        """
        print(333, arbiter, worker, worker.app.zato_wsgi_app)
        
        parallel_server = worker.app.zato_wsgi_app
        
        # Store the ODB configuration, create an ODB connection pool and have self.odb use it
        parallel_server.config.odb_data = Bunch()
        parallel_server.config.odb_data.db_name = parallel_server.odb_data['db_name']
        parallel_server.config.odb_data.engine = parallel_server.odb_data['engine']
        parallel_server.config.odb_data.extra = parallel_server.odb_data['extra']
        parallel_server.config.odb_data.host = parallel_server.odb_data['host']
        parallel_server.config.odb_data.password = parallel_server.crypto_manager.decrypt(parallel_server.odb_data['password'])
        parallel_server.config.odb_data.pool_size = parallel_server.odb_data['pool_size']
        parallel_server.config.odb_data.username = parallel_server.odb_data['username']
        parallel_server.config.odb_data.token = parallel_server.odb_data['token']
        parallel_server.config.odb_data.is_odb = True
        
        # This is the call that creates an SQLAlchemy connection
        parallel_server.sql_pool_store[ZATO_ODB_POOL_NAME] = parallel_server.config.odb_data
        
        parallel_server.odb.pool = parallel_server.sql_pool_store[ZATO_ODB_POOL_NAME]
        parallel_server.odb.token = parallel_server.config.odb_data.token
        
        # Now try grabbing the basic server's data from the ODB. No point
        # in doing anything else if we can't get past this point.
        server = parallel_server.odb.fetch_server()
        
        if not server:
            raise Exception('Server does not exist in the ODB')
        
        parallel_server.id = server.id
        parallel_server.name = server.name
        parallel_server.cluster_id = server.cluster_id

        parallel_server._after_init_common(server)
        
        # For now, all the servers are always ACCEPTED but future versions
        # might introduce more join states
        if server.last_join_status in(SERVER_JOIN_STATUS.ACCEPTED):
            parallel_server._after_init_accepted(server)
        else:
            msg = 'Server has not been accepted, last_join_status:[{0}]'
            logger.warn(msg.format(server.last_join_status))
            
            parallel_server._after_init_non_accepted(server)
            
        parallel_server.odb.server_up_down(server.id, SERVER_UP_STATUS.RUNNING, True)

    def shutdown(self):
            
        # Close all the connector subprocesses this server has started
        pairs = ((AMQP_CONNECTOR.CLOSE, MESSAGE_TYPE.TO_AMQP_CONNECTOR_ALL),
                (JMS_WMQ_CONNECTOR.CLOSE, MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_ALL),
                (ZMQ_CONNECTOR.CLOSE, MESSAGE_TYPE.TO_ZMQ_CONNECTOR_ALL),
                )
        
        for action, msg_type in pairs:
            msg = {}
            msg['action'] = action
            msg['odb_token'] = self.odb.token
            self.broker_client.publish(msg, msg_type=msg_type)
            time.sleep(0.2)
        
        self.broker_client.stop()
        
        if self.singleton_server:
            self.singleton_server.pickup.stop()
            
            if self.singleton_server.is_cluster_wide:
                self.odb.clear_cluster_wide()
            
        self.odb.server_up_down(self.id, SERVER_UP_STATUS.CLEAN_DOWN)
        self.odb.close()
            
# ##############################################################################

    def on_broker_msg_singleton(self, msg):
        getattr(self.singleton_server, 'on_broker_msg_{}'.format(code_to_name[msg.action]))(msg)
    
# ##############################################################################

    def notify_new_package(self, package_id):
        """ Publishes a message on the broker so all the servers (this one including
        can deploy a new package).
        """
        msg = {'action': HOT_DEPLOY.CREATE, 'package_id': package_id}
        self.broker_client.publish(msg)
