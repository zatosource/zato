# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, os, time, signal
from datetime import datetime
from httplib import INTERNAL_SERVER_ERROR, responses
from logging import INFO
from tempfile import mkstemp
from threading import Thread
from traceback import format_exc
from uuid import uuid4

# anyjson
from anyjson import dumps

# arrow
from arrow import utcnow

# Bunch
from bunch import Bunch

# gevent
import gevent
import gevent.monkey # Needed for Cassandra

# Paste
from paste.util.converters import asbool

# pytz
from pytz import UTC

# Spring Python
from springpython.context import DisposableObject

# retools
from retools.lock import Lock

# tzlocal
from tzlocal import get_localzone

# Zato
from zato.broker.client import BrokerClient
from zato.common import ACCESS_LOG_DT_FORMAT, KVDB, MISC, SERVER_JOIN_STATUS, SERVER_UP_STATUS, ZATO_ODB_POOL_NAME
from zato.common.broker_message import AMQP_CONNECTOR, code_to_name, HOT_DEPLOY, JMS_WMQ_CONNECTOR, MESSAGE_TYPE, TOPICS, \
     ZMQ_CONNECTOR
from zato.common.pubsub import PubSubAPI, RedisPubSub
from zato.common.util import add_startup_jobs, get_kvdb_config_for_log, hot_deploy, \
     invoke_startup_services as _invoke_startup_services, new_cid, StaticConfig, register_diag_handlers
from zato.server.base import BrokerMessageReceiver
from zato.server.base.worker import WorkerStore
from zato.server.config import ConfigDict, ConfigStore
from zato.server.connection.amqp.channel import start_connector as amqp_channel_start_connector
from zato.server.connection.amqp.outgoing import start_connector as amqp_out_start_connector
from zato.server.connection.http_soap.url_data import Matcher
from zato.server.connection.jms_wmq.channel import start_connector as jms_wmq_channel_start_connector
from zato.server.connection.jms_wmq.outgoing import start_connector as jms_wmq_out_start_connector
from zato.server.connection.zmq_.channel import start_connector as zmq_channel_start_connector
from zato.server.pickup import get_pickup

logger = logging.getLogger(__name__)
kvdb_logger = logging.getLogger('zato_kvdb')

class ParallelServer(DisposableObject, BrokerMessageReceiver):
    def __init__(self):
        self.host = None
        self.port = None
        self.crypto_manager = None
        self.odb = None
        self.odb_data = None
        self.singleton_server = None
        self.config = None
        self.repo_location = None
        self.sql_pool_store = None
        self.int_parameters = None
        self.int_parameter_suffixes = None
        self.bool_parameter_prefixes = None
        self.soap11_content_type = None
        self.soap12_content_type = None
        self.plain_xml_content_type = None
        self.json_content_type = None
        self.internal_service_modules = None # Zato's own internal services
        self.service_modules = None # Set programmatically in Spring
        self.service_sources = None # Set in a config file
        self.base_dir = None
        self.tls_dir = None
        self.hot_deploy_config = None
        self.pickup = None
        self.fs_server_config = None
        self.connector_server_grace_time = None
        self.id = None
        self.name = None
        self.cluster_id = None
        self.kvdb = None
        self.startup_jobs = None
        self.worker_store = None
        self.deployment_lock_expires = None
        self.deployment_lock_timeout = None
        self.app_context = None
        self.has_gevent = None
        self.delivery_store = None
        self.static_config = None
        self.component_enabled = Bunch()
        self.client_address_headers = ['HTTP_X_ZATO_FORWARDED_FOR', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']
        self.broker_client = None

        # Allows users store arbitrary data across service invocations
        self.user_ctx = Bunch()
        self.user_ctx_lock = gevent.lock.RLock()

        self.access_logger = logging.getLogger('zato_access_log')

        # The main config store
        self.config = ConfigStore()

        gevent.signal(signal.SIGINT, self.destroy)

    def on_wsgi_request(self, wsgi_environ, start_response, **kwargs):
        """ Handles incoming HTTP requests.
        """
        cid = kwargs.get('cid', new_cid())

        wsgi_environ['zato.local_tz'] = get_localzone()
        wsgi_environ['zato.request_timestamp_utc'] = utcnow()

        local_dt = wsgi_environ['zato.request_timestamp_utc'].replace(tzinfo=UTC).astimezone(wsgi_environ['zato.local_tz'])
        wsgi_environ['zato.request_timestamp'] = wsgi_environ['zato.local_tz'].normalize(local_dt)

        wsgi_environ['zato.http.response.headers'] = {'X-Zato-CID': cid}

        remote_addr = '(None)'
        for name in self.client_address_headers:
            remote_addr = wsgi_environ.get(name)
            if remote_addr:
                break

        wsgi_environ['zato.http.remote_addr'] = remote_addr

        try:

            payload = self.worker_store.request_dispatcher.dispatch(
                cid, datetime.utcnow(), wsgi_environ, self.worker_store) or b''

        # Any exception at this point must be our fault
        except Exception, e:
            tb = format_exc(e)
            wsgi_environ['zato.http.response.status'] = b'{} {}'.format(INTERNAL_SERVER_ERROR, responses[INTERNAL_SERVER_ERROR])
            error_msg = b'[{0}] Exception caught [{1}]'.format(cid, tb)
            logger.error(error_msg)
            payload = error_msg
            raise

        # Note that this call is asynchronous and we do it the last possible moment.
        if wsgi_environ['zato.http.channel_item'] and wsgi_environ['zato.http.channel_item'].get('audit_enabled'):
            self.worker_store.request_dispatcher.url_data.audit_set_response(
                cid, payload, wsgi_environ)

        headers = [(k.encode('utf-8'), v.encode('utf-8')) for k, v in wsgi_environ['zato.http.response.headers'].items()]
        start_response(wsgi_environ['zato.http.response.status'], headers)

        if isinstance(payload, unicode):
            payload = payload.encode('utf-8')

        if self.access_logger.isEnabledFor(INFO):

            channel_item = wsgi_environ.get('zato.http.channel_item')
            if channel_item:
                channel_name = channel_item.get('name', '-')
            else:
                channel_name = '-'

            self.access_logger.info('', extra = {
                'remote_ip': wsgi_environ['zato.http.remote_addr'],
                'cid_resp_time': '{}/{}'.format(cid, (utcnow() - wsgi_environ['zato.request_timestamp_utc']).total_seconds()),
                'channel_name': channel_name,
                'req_timestamp_utc': wsgi_environ['zato.request_timestamp_utc'].strftime(ACCESS_LOG_DT_FORMAT),
                'req_timestamp': wsgi_environ['zato.request_timestamp'].strftime(ACCESS_LOG_DT_FORMAT),
                'method': wsgi_environ['REQUEST_METHOD'],
                'path': wsgi_environ['PATH_INFO'],
                'http_version': wsgi_environ['SERVER_PROTOCOL'],
                'status_code': wsgi_environ['zato.http.response.status'].split()[0],
                'response_size': len(payload),
                'user_agent': wsgi_environ.get('HTTP_USER_AGENT', '(None)'),
                })

        return [payload]

    def deploy_missing_services(self, locally_deployed):
        """ Deploys services that exist on other servers but not on ours.
        """

        # The locally_deployed list are all the services that we could import based on our current
        # understanding of the contents of the cluster. However, it's possible that we have
        # been shut down for a long time and during that time other servers deployed services
        # we don't know anything about. They are not stored locally because we were down.
        # Hence we need to check out if there are any other servers in the cluster and if so,
        # grab their list of services, compare it with what we have deployed and deploy
        # any that are missing.

        # Continue only if there is more than one running server in the cluster.
        other_servers = self.odb.get_servers()

        if other_servers:
            other_server = other_servers[0] # Index 0 is as random as any other because the list is not sorted.
            missing = self.odb.get_missing_services(other_server, locally_deployed)

            if missing:
                logger.info('Found extra services to deploy: %s', ', '.join(sorted(item.name for item in missing)))

                for service_id, name, source_path, source in missing:
                    file_name = os.path.basename(source_path)
                    _, full_path = mkstemp(suffix='-'+ file_name)

                    f = open(full_path, 'wb')
                    f.write(source)
                    f.close()

                    # Create a deployment package in ODB out of which all the services will be picked up ..
                    msg = Bunch()
                    msg.action = HOT_DEPLOY.CREATE.value
                    msg.msg_type = MESSAGE_TYPE.TO_PARALLEL_ALL
                    msg.package_id = hot_deploy(self, file_name, full_path, notify=False)

                    # .. and tell the worker to actually deploy all the services the package contains.
                    gevent.spawn(self.worker_store.on_broker_msg_HOT_DEPLOY_CREATE, msg)

                    logger.info('Deployed an extra service found: %s (%s)', name, service_id)

    def maybe_on_first_worker(self, server, redis_conn, deployment_key):
        """ This method will execute code with a Redis lock held. We need a lock
        because we can have multiple worker processes fighting over the right to
        redeploy services. The first worker to grab the lock will actually perform
        the redeployment and set a flag meaning that for this particular deployment
        key (and remember that each server restart means a new deployment key)
        the services have been already deployed. Later workers will check that
        the flag exists and will skip the deployment altogether.

        The first worker to be started will also start a singleton thread later on,
        outside this method but basing on whether the method returns True or not.
        """

        def import_initial_services_jobs():
            # (re-)deploy the services from a clear state
            locally_deployed = self.service_store.import_services_from_anywhere(
                self.internal_service_modules + self.service_modules +
                self.service_sources, self.base_dir)

            # Add the statistics-related scheduler jobs to the ODB
            add_startup_jobs(self.cluster_id, self.odb, self.startup_jobs, asbool(self.fs_server_config.component_enabled.stats))

            # Migrations
            self.odb.add_channels_2_0()

            return set(locally_deployed)

        lock_name = '{}{}:{}'.format(KVDB.LOCK_SERVER_STARTING, self.fs_server_config.main.token, deployment_key)
        already_deployed_flag = '{}{}:{}'.format(KVDB.LOCK_SERVER_ALREADY_DEPLOYED,
            self.fs_server_config.main.token, deployment_key)

        logger.debug('Will use the lock_name: [{}]'.format(lock_name))

        with Lock(lock_name, self.deployment_lock_expires, self.deployment_lock_timeout, redis_conn):
            if redis_conn.get(already_deployed_flag):
                # There has been already the first worker who's done everything
                # there is to be done so we may just return.
                msg = 'Not attempting to grab the lock_name:[{}]'.format(lock_name)
                logger.debug(msg)

                # Simply deploy services, including any missing ones, the first worker has already cleared out the ODB
                locally_deployed = import_initial_services_jobs()

                return False, locally_deployed

            else:
                # We are this server's first worker so we need to re-populate
                # the database and create the flag indicating we're done.
                msg = 'Got Redis lock_name:[{}], expires:[{}], timeout:[{}]'.format(
                    lock_name, self.deployment_lock_expires, self.deployment_lock_timeout)
                logger.debug(msg)

                # .. Remove all the deployed services from the DB ..
                self.odb.drop_deployed_services(server.id)

                # .. deploy them back including any missing ones found on other servers.
                locally_deployed = import_initial_services_jobs()

                # Add the flag to Redis indicating that this server has already
                # deployed its services. Note that by default the expiration
                # time is more than a century in the future. It will be cleared out
                # next time the server will be started. This also means that when
                # a process dies and it's the one holding the singleton thread,
                # no other process will be able to start the singleton thread
                # until the server is fully restarted so that the locks are cleared.

                redis_conn.set(already_deployed_flag, dumps({'create_time_utc':datetime.utcnow().isoformat()}))
                redis_conn.expire(already_deployed_flag, self.deployment_lock_expires)

                return True, locally_deployed

    def get_lua_programs(self):
        for item in 'internal', 'user':
            dir_name = os.path.join(self.repo_location, 'lua', item)
            for file_name in os.listdir(dir_name):

                lua_idx = file_name.find('.lua')
                name = file_name[0:lua_idx] if lua_idx else file_name
                program = open(os.path.join(dir_name, file_name)).read()

                yield [name, program]

    def _after_init_common(self, server, deployment_key):
        """ Initializes parts of the server that don't depend on whether the
        server's been allowed to join the cluster or not.
        """
        self.worker_store = WorkerStore(self.config, self)
        self.worker_store.invoke_matcher.read_config(self.fs_server_config.invoke_patterns_allowed)
        self.worker_store.target_matcher.read_config(self.fs_server_config.invoke_target_patterns_allowed)

        # Patterns to match during deployment
        self.service_store.patterns_matcher.read_config(self.fs_server_config.deploy_patterns_allowed)

        # Static config files
        self.static_config = StaticConfig(os.path.join(self.repo_location, 'static'))

        # Key-value DB
        kvdb_config = get_kvdb_config_for_log(self.fs_server_config.kvdb)
        kvdb_logger.info('Worker config `%s`', kvdb_config)

        self.kvdb.config = self.fs_server_config.kvdb
        self.kvdb.server = self
        self.kvdb.decrypt_func = self.crypto_manager.decrypt
        self.kvdb.init()

        kvdb_logger.info('Worker config `%s`', kvdb_config)

        # Lua programs, both internal and user defined ones.
        for name, program in self.get_lua_programs():
            self.kvdb.lua_container.add_lua_program(name, program)

        # Service sources
        self.service_sources = []
        for name in open(os.path.join(self.repo_location, self.fs_server_config.main.service_sources)):
            name = name.strip()
            if name and not name.startswith('#'):
                self.service_sources.append(name)

        # Normalize hot-deploy configuration
        self.hot_deploy_config = Bunch()

        self.hot_deploy_config.work_dir = os.path.normpath(os.path.join(
            self.repo_location, self.fs_server_config.hot_deploy.work_dir))

        self.hot_deploy_config.backup_history = int(self.fs_server_config.hot_deploy.backup_history)
        self.hot_deploy_config.backup_format = self.fs_server_config.hot_deploy.backup_format

        for name in('current_work_dir', 'backup_work_dir', 'last_backup_work_dir', 'delete_after_pick_up'):

            # New in 2.0
            if name == 'delete_after_pick_up':
                value = asbool(self.fs_server_config.hot_deploy.get(name, True))
                self.hot_deploy_config[name] = value
            else:
                self.hot_deploy_config[name] = os.path.normpath(os.path.join(
                  self.hot_deploy_config.work_dir, self.fs_server_config.hot_deploy[name]))

        is_first, locally_deployed = self.maybe_on_first_worker(server, self.kvdb.conn, deployment_key)

        if is_first:

            self.singleton_server = self.app_context.get_object('singleton_server')
            self.singleton_server.initial_sleep_time = int(self.fs_server_config.singleton.initial_sleep_time) / 1000.0
            self.singleton_server.parallel_server = self

            pickup_dir = self.fs_server_config.hot_deploy.pickup_dir
            if not os.path.isabs(pickup_dir):
                pickup_dir = os.path.join(self.repo_location, pickup_dir)

            self.singleton_server.pickup = get_pickup(self.has_gevent)
            self.singleton_server.pickup.pickup_dir = pickup_dir
            self.singleton_server.pickup.pickup_event_processor.pickup_dir = pickup_dir
            self.singleton_server.pickup.pickup_event_processor.server = self.singleton_server

            self.singleton_server.server_id = server.id

        return is_first, locally_deployed

    def _after_init_accepted(self, server, deployment_key, locally_deployed):

        # Flag set to True if this worker is the cluster-wide singleton
        is_singleton = False

        # Which components are enabled
        self.component_enabled.stats = asbool(self.fs_server_config.component_enabled.stats)
        self.component_enabled.slow_response = asbool(self.fs_server_config.component_enabled.slow_response)

        # Pub/sub
        self.pubsub = PubSubAPI(RedisPubSub(self.kvdb.conn))

        # Repo location so that AMQP subprocesses know where to read
        # the server's configuration from.
        self.config.repo_location = self.repo_location

        #
        # Cassandra - start
        #

        query = self.odb.get_cassandra_conn_list(server.cluster.id, True)
        self.config.cassandra_conn = ConfigDict.from_query('cassandra_conn', query)

        query = self.odb.get_cassandra_query_list(server.cluster.id, True)
        self.config.cassandra_query = ConfigDict.from_query('cassandra_query', query)

        #
        # Cassandra - end
        #

        #
        # Search - start
        #

        query = self.odb.get_search_es_list(server.cluster.id, True)
        self.config.search_es = ConfigDict.from_query('search_es', query)

        query = self.odb.get_search_solr_list(server.cluster.id, True)
        self.config.search_solr = ConfigDict.from_query('search_solr', query)

        #
        # Search - end
        #

        #
        # Cloud - start
        #

        # OpenStack - Swift

        query = self.odb.get_cloud_openstack_swift_list(server.cluster.id, True)
        self.config.cloud_openstack_swift = ConfigDict.from_query('cloud_openstack_swift', query)

        query = self.odb.get_cloud_aws_s3_list(server.cluster.id, True)
        self.config.cloud_aws_s3 = ConfigDict.from_query('cloud_aws_s3', query)

        #
        # Cloud - end
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Services
        query = self.odb.get_service_list(server.cluster.id, True)
        self.config.service = ConfigDict.from_query('service_list', query)

        #
        # Outgoing connections - start
        #

        # AMQP
        query = self.odb.get_out_amqp_list(server.cluster.id, True)
        self.config.out_amqp = ConfigDict.from_query('out_amqp', query)

        # FTP
        query = self.odb.get_out_ftp_list(server.cluster.id, True)
        self.config.out_ftp = ConfigDict.from_query('out_ftp', query)

        # JMS WMQ
        query = self.odb.get_out_jms_wmq_list(server.cluster.id, True)
        self.config.out_jms_wmq = ConfigDict.from_query('out_jms_wmq', query)

        # Odoo
        query = self.odb.get_out_odoo_list(server.cluster.id, True)
        self.config.out_odoo = ConfigDict.from_query('out_odoo', query)

        # Plain HTTP
        query = self.odb.get_http_soap_list(server.cluster.id, 'outgoing', 'plain_http', True)
        self.config.out_plain_http = ConfigDict.from_query('out_plain_http', query)

        # SOAP
        query = self.odb.get_http_soap_list(server.cluster.id, 'outgoing', 'soap', True)
        self.config.out_soap = ConfigDict.from_query('out_soap', query)

        # SQL
        query = self.odb.get_out_sql_list(server.cluster.id, True)
        self.config.out_sql = ConfigDict.from_query('out_sql', query)

        # ZMQ
        query = self.odb.get_out_zmq_list(server.cluster.id, True)
        self.config.out_zmq = ConfigDict.from_query('out_zmq', query)

        #
        # Outgoing connections - end
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #
        # Notifications - start
        #

        # OpenStack Swift
        query = self.odb.get_notif_cloud_openstack_swift_list(server.cluster.id, True)
        self.config.notif_cloud_openstack_swift = ConfigDict.from_query('notif_cloud_openstack_swift', query)

        # SQL
        query = self.odb.get_notif_sql_list(server.cluster.id, True)
        self.config.notif_sql = ConfigDict.from_query('notif_sql', query)

        #
        # Notifications - end
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #
        # Security - start
        #

        # API keys
        query = self.odb.get_apikey_security_list(server.cluster.id, True)
        self.config.apikey = ConfigDict.from_query('apikey', query)

        # AWS
        query = self.odb.get_aws_security_list(server.cluster.id, True)
        self.config.aws = ConfigDict.from_query('aws', query)

        # HTTP Basic Auth
        query = self.odb.get_basic_auth_list(server.cluster.id, True)
        self.config.basic_auth = ConfigDict.from_query('basic_auth', query)

        # NTLM
        query = self.odb.get_ntlm_list(server.cluster.id, True)
        self.config.ntlm = ConfigDict.from_query('ntlm', query)

        # OAuth
        query = self.odb.get_oauth_list(server.cluster.id, True)
        self.config.oauth = ConfigDict.from_query('oauth', query)

        # OpenStack
        query = self.odb.get_openstack_security_list(server.cluster.id, True)
        self.config.openstack_security = ConfigDict.from_query('openstack_security', query)

        # RBAC - permissions
        query = self.odb.get_rbac_permission_list(server.cluster.id, True)
        self.config.rbac_permission = ConfigDict.from_query('rbac_permission', query)

        # RBAC - roles
        query = self.odb.get_rbac_role_list(server.cluster.id, True)
        self.config.rbac_role = ConfigDict.from_query('rbac_role', query)

        # RBAC - client roles
        query = self.odb.get_rbac_client_role_list(server.cluster.id, True)
        self.config.rbac_client_role = ConfigDict.from_query('rbac_client_role', query)

        # RBAC - role permission
        query = self.odb.get_rbac_role_permission_list(server.cluster.id, True)
        self.config.rbac_role_permission = ConfigDict.from_query('rbac_role_permission', query)

        # Technical accounts
        query = self.odb.get_tech_acc_list(server.cluster.id, True)
        self.config.tech_acc = ConfigDict.from_query('tech_acc', query)

        # TLS CA certs
        query = self.odb.get_tls_ca_cert_list(server.cluster.id, True)
        self.config.tls_ca_cert = ConfigDict.from_query('tls_ca_cert', query)

        # TLS channel security
        query = self.odb.get_tls_channel_sec_list(server.cluster.id, True)
        self.config.tls_channel_sec = ConfigDict.from_query('tls_channel_sec', query)

        # TLS key/cert pairs
        query = self.odb.get_tls_key_cert_list(server.cluster.id, True)
        self.config.tls_key_cert = ConfigDict.from_query('tls_key_cert', query)

        # WS-Security
        query = self.odb.get_wss_list(server.cluster.id, True)
        self.config.wss = ConfigDict.from_query('wss', query)

        # XPath
        query = self.odb.get_xpath_sec_list(server.cluster.id, True)
        self.config.xpath_sec = ConfigDict.from_query('xpath_sec', query)

        #
        # Security - end
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # All the HTTP/SOAP channels.
        http_soap = []
        for item in self.odb.get_http_soap_list(server.cluster.id, 'channel'):

            hs_item = Bunch()
            for key in item.keys():
                hs_item[key] = getattr(item, key)

            hs_item.replace_patterns_json_pointer = item.replace_patterns_json_pointer
            hs_item.replace_patterns_xpath = item.replace_patterns_xpath

            hs_item.match_target = '{}{}{}'.format(hs_item.soap_action, MISC.SEPARATOR, hs_item.url_path)
            hs_item.match_target_compiled = Matcher(hs_item.match_target)

            http_soap.append(hs_item)

        self.config.http_soap = http_soap

        # Namespaces
        query = self.odb.get_namespace_list(server.cluster.id, True)
        self.config.msg_ns = ConfigDict.from_query('msg_ns', query)

        # XPath
        query = self.odb.get_xpath_list(server.cluster.id, True)
        self.config.xpath = ConfigDict.from_query('msg_xpath', query)

        # JSON Pointer
        query = self.odb.get_json_pointer_list(server.cluster.id, True)
        self.config.json_pointer = ConfigDict.from_query('json_pointer', query)

        # SimpleIO
        self.config.simple_io = ConfigDict('simple_io', Bunch())
        self.config.simple_io['int_parameters'] = self.int_parameters
        self.config.simple_io['int_parameter_suffixes'] = self.int_parameter_suffixes
        self.config.simple_io['bool_parameter_prefixes'] = self.bool_parameter_prefixes

        # Pub/sub config
        self.config.pubsub = Bunch()
        self.config.pubsub.default_consumer = Bunch()
        self.config.pubsub.default_producer = Bunch()

        query = self.odb.get_pubsub_topic_list(server.cluster.id, True)
        self.config.pubsub.topics = ConfigDict.from_query('pubsub_topics', query)

        id, name = self.odb.get_pubsub_default_client(server.cluster.id, 'zato.pubsub.default-consumer')
        self.config.pubsub.default_consumer.id, self.config.pubsub.default_consumer.name = id, name

        id, name = self.odb.get_pubsub_default_client(server.cluster.id, 'zato.pubsub.default-producer')
        self.config.pubsub.default_producer.id, self.config.pubsub.default_producer.name = id, name

        query = self.odb.get_pubsub_producer_list(server.cluster.id, True)
        self.config.pubsub.producers = ConfigDict.from_query('pubsub_producers', query, list_config=True)

        query = self.odb.get_pubsub_consumer_list(server.cluster.id, True)
        self.config.pubsub.consumers = ConfigDict.from_query('pubsub_consumers', query, list_config=True)

        # E-mail - SMTP
        query = self.odb.get_email_smtp_list(server.cluster.id, True)
        self.config.email_smtp = ConfigDict.from_query('email_smtp', query)

        # E-mail - IMAP
        query = self.odb.get_email_imap_list(server.cluster.id, True)
        self.config.email_imap = ConfigDict.from_query('email_imap', query)

        # Assign config to worker
        self.worker_store.worker_config = self.config
        self.worker_store.pubsub = self.pubsub
        self.worker_store.init()

        if self.singleton_server:

            self.singleton_server.wait_for_worker()

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
                is_singleton = True

        # Deployed missing services found on other servers
        if locally_deployed:
            self.deploy_missing_services(locally_deployed)

        # Signal to ODB that we are done with deploying everything
        self.odb.on_deployment_finished()

        return is_singleton

    def init_connectors(self):
        """ Starts all the connector subprocesses.
        """
        logger.info('Initializing connectors')

        # AMQP - channels
        channel_amqp_list = self.odb.get_channel_amqp_list(self.cluster_id)
        if channel_amqp_list:
            for item in channel_amqp_list:
                if item.is_active:
                    amqp_channel_start_connector(self.repo_location, item.id, item.def_id)
                else:
                    logger.info('Not starting an inactive channel (AMQP {})'.format(item.name))

        else:
            logger.info('No AMQP channels to start')

        # AMQP - outgoing
        out_amqp_list = self.odb.get_out_amqp_list(self.cluster_id)
        if out_amqp_list:
            for item in out_amqp_list:
                if item.is_active:
                    amqp_out_start_connector(self.repo_location, item.id, item.def_id)
                else:
                    logger.info('Not starting an inactive outgoing connection (AMQP {})'.format(item.name))
        else:
            logger.info('No AMQP outgoing connections to start')

        # JMS WMQ - channels
        channel_jms_wmq_list = self.odb.get_channel_jms_wmq_list(self.cluster_id)
        if channel_jms_wmq_list:
            for item in channel_jms_wmq_list:
                if item.is_active:
                    jms_wmq_channel_start_connector(self.repo_location, item.id, item.def_id)
                else:
                    logger.info('Not starting an inactive channel (JMS WebSphere MQ {})'.format(item.name))
        else:
            logger.info('No JMS WebSphere MQ channels to start')

        # JMS WMQ - outgoing
        out_jms_wmq_list = self.odb.get_out_jms_wmq_list(self.cluster_id)
        if out_jms_wmq_list:
            for item in out_jms_wmq_list:
                if item.is_active:
                    jms_wmq_out_start_connector(self.repo_location, item.id, item.def_id)
                else:
                    logger.info('Not starting an inactive outgoing connection (JMS WebSphere MQ {})'.format(item.name))
        else:
            logger.info('No JMS WebSphere MQ outgoing connections to start')

        # ZMQ - channels
        channel_zmq_list = self.odb.get_channel_zmq_list(self.cluster_id)
        if channel_zmq_list:
            for item in channel_zmq_list:
                if item.is_active:
                    zmq_channel_start_connector(self.repo_location, item.id)
                else:
                    logger.info('Not starting an inactive channel (ZeroMQ {})'.format(item.name))
        else:
            logger.info('No Zero MQ channels to start')

    def _after_init_non_accepted(self, server):
        raise NotImplementedError("This Zato version doesn't support join states other than ACCEPTED")

    def get_config_odb_data(self, parallel_server):
        """ Returns configuration with regards to ODB data.
        """
        odb_data = Bunch()
        odb_data.db_name = parallel_server.odb_data['db_name']
        odb_data.extra = parallel_server.odb_data['extra']
        odb_data.engine = parallel_server.odb_data['engine']
        odb_data.token = parallel_server.fs_server_config.main.token
        odb_data.is_odb = True

        if odb_data.engine != 'sqlite':
            odb_data.password = parallel_server.crypto_manager.decrypt(parallel_server.odb_data['password'])
            odb_data.host = parallel_server.odb_data['host']
            odb_data.port = parallel_server.odb_data['port']
            odb_data.engine = parallel_server.odb_data['engine']
            odb_data.pool_size = parallel_server.odb_data['pool_size']
            odb_data.username = parallel_server.odb_data['username']

        # Note that we don't read is_active off of anywhere - ODB always must
        # be active and it's not a regular connection pool anyway.
        odb_data.is_active = True

        return odb_data

    def set_odb_pool(self):
        # This is the call that creates an SQLAlchemy connection
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.config.odb_data
        self.odb.pool = self.sql_pool_store[ZATO_ODB_POOL_NAME].pool
        self.odb.token = self.config.odb_data.token

    @staticmethod
    def start_server(parallel_server, zato_deployment_key=None):

        # Will be set to True if this process is a singleton
        is_singleton = False

        # Will be None if we are not running in background.
        if not zato_deployment_key:
            zato_deployment_key = uuid4().hex

        register_diag_handlers()

        # Store the ODB configuration, create an ODB connection pool and have self.odb use it
        parallel_server.config.odb_data = parallel_server.get_config_odb_data(parallel_server)
        parallel_server.set_odb_pool()

        # Now try grabbing the basic server's data from the ODB. No point
        # in doing anything else if we can't get past this point.
        server = parallel_server.odb.fetch_server(parallel_server.config.odb_data)

        if not server:
            raise Exception('Server does not exist in the ODB')

        parallel_server.id = server.id
        parallel_server.name = server.name
        parallel_server.cluster_id = server.cluster_id

        is_first, locally_deployed = parallel_server._after_init_common(server, zato_deployment_key)

        # For now, all the servers are always ACCEPTED but future versions
        # might introduce more join states
        if server.last_join_status in(SERVER_JOIN_STATUS.ACCEPTED):
            is_singleton = parallel_server._after_init_accepted(server, zato_deployment_key, locally_deployed)
        else:
            msg = 'Server has not been accepted, last_join_status:[{0}]'
            logger.warn(msg.format(server.last_join_status))

            parallel_server._after_init_non_accepted(server)

        broker_callbacks = {
            TOPICS[MESSAGE_TYPE.TO_PARALLEL_ANY]: parallel_server.worker_store.on_broker_msg,
            TOPICS[MESSAGE_TYPE.TO_PARALLEL_ALL]: parallel_server.worker_store.on_broker_msg,
            }

        if is_first:
            broker_callbacks[TOPICS[MESSAGE_TYPE.TO_SINGLETON]] = parallel_server.on_broker_msg_singleton

        parallel_server.broker_client = BrokerClient(
            parallel_server.kvdb, 'parallel', broker_callbacks, parallel_server.get_lua_programs())

        parallel_server.worker_store.set_broker_client(parallel_server.broker_client)

        if is_first:
            kwargs = {'broker_client':parallel_server.broker_client}
            Thread(target=parallel_server.singleton_server.run, kwargs=kwargs).start()

        parallel_server.odb.server_up_down(server.token, SERVER_UP_STATUS.RUNNING, True,
            parallel_server.host, parallel_server.port)

        if is_first:
            parallel_server.invoke_startup_services(is_first)

        # We cannot do it earlier because we need the broker client and everything be ready
        if is_singleton:

            # Let's wait for the broker client to connect before continuing with anything
            while not parallel_server.singleton_server.broker_client and parallel_server.singleton_server.broker_client.ready:
                time.sleep(0.01)

            parallel_server.singleton_server.init_scheduler()
            parallel_server.singleton_server.init_notifiers()

    def invoke_startup_services(self, is_first):
        _invoke_startup_services(
            'Parallel', 'startup_services_first_worker' if is_first else 'startup_services_any_worker',
            self.fs_server_config, self.repo_location, self.broker_client, 'zato.notif.init-notifiers')

    @staticmethod
    def post_fork(arbiter, worker):
        """ A Gunicorn hook which initializes the worker.
        """
        ParallelServer.start_server(worker.app.zato_wsgi_app, arbiter.zato_deployment_key)

    @staticmethod
    def on_starting(arbiter):
        """ A Gunicorn hook for setting the deployment key for this particular
        set of server processes. It needs to be added to the arbiter because
        we want for each worker to be (re-)started to see the same key.
        """
        setattr(arbiter, 'zato_deployment_key', uuid4().hex)

    def destroy(self):
        """ A Spring Python hook for closing down all the resources held.
        """
        if self.singleton_server:

            # Close all the connector subprocesses this server has possibly started
            pairs = ((AMQP_CONNECTOR.CLOSE.value, MESSAGE_TYPE.TO_AMQP_CONNECTOR_ALL),
                    (JMS_WMQ_CONNECTOR.CLOSE.value, MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_ALL),
                    (ZMQ_CONNECTOR.CLOSE.value, MESSAGE_TYPE.TO_ZMQ_CONNECTOR_ALL),
                    )

            for action, msg_type in pairs:
                msg = {}
                msg['action'] = action
                msg['token'] = self.odb.token
                self.broker_client.publish(msg, msg_type=msg_type)
                time.sleep(0.2)

            # Broker client
            self.broker_client.close()

            # Scheduler
            self.singleton_server.scheduler.stop()

            # Pick-up processor
            self.singleton_server.pickup.stop()

            # Cluster-wide flags
            if self.singleton_server.is_cluster_wide:
                self.odb.clear_cluster_wide()

        # Tell the ODB we've gone through a clean shutdown but only if this is
        # the main process going down (Arbiter) not one of Gunicorn workers.
        # We know it's the main process because its ODB's session has never
        # been initialized.
        if not self.odb.session_initialized:

            self.config.odb_data = self.get_config_odb_data(self)
            self.set_odb_pool()

            self.odb.init_session(ZATO_ODB_POOL_NAME, self.config.odb_data, self.odb.pool, False)

            self.odb.server_up_down(self.odb.token, SERVER_UP_STATUS.CLEAN_DOWN)
            self.odb.close()

    # Convenience API
    stop = destroy

# ##############################################################################

    def on_broker_msg_singleton(self, msg):
        getattr(self.singleton_server, 'on_broker_msg_{}'.format(code_to_name[msg.action]))(msg)

# ##############################################################################

    def notify_new_package(self, package_id):
        """ Publishes a message on the broker so all the servers (this one including
        can deploy a new package).
        """
        msg = {'action': HOT_DEPLOY.CREATE.value, 'package_id': package_id}
        self.broker_client.publish(msg)
