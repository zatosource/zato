# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, os, signal
from datetime import datetime
from logging import INFO
from re import IGNORECASE
from tempfile import mkstemp
from traceback import format_exc
from uuid import uuid4

# anyjson
from anyjson import dumps

# gevent
import gevent
import gevent.monkey # Needed for Cassandra

# globre
import globre

# Paste
from paste.util.converters import asbool

# Spring Python
from springpython.context import DisposableObject

# Zato
from zato.broker import BrokerMessageReceiver
from zato.broker.client import BrokerClient
from zato.bunch import Bunch
from zato.common import DATA_FORMAT, KVDB, SERVER_UP_STATUS, ZATO_ODB_POOL_NAME
from zato.common.broker_message import HOT_DEPLOY, MESSAGE_TYPE, TOPICS
from zato.common.ipc.api import IPCAPI
from zato.common.posix_ipc_util import ServerStartupIPC
from zato.common.time_util import TimeUtil
from zato.common.util import absolutize, get_config, get_kvdb_config_for_log, get_user_config_name, hot_deploy, \
     invoke_startup_services as _invoke_startup_services, new_cid, spawn_greenlet, StaticConfig, register_diag_handlers
from zato.distlock import LockManager
from zato.server.base.worker import WorkerStore
from zato.server.config import ConfigStore
from zato.server.connection.server import Servers
from zato.server.base.parallel.config import ConfigLoader
from zato.server.base.parallel.http import HTTPHandler
from zato.server.pickup import PickupManager

# ################################################################################################################################

logger = logging.getLogger(__name__)
kvdb_logger = logging.getLogger('zato_kvdb')

megabyte = 10**6

# ################################################################################################################################

class ParallelServer(DisposableObject, BrokerMessageReceiver, ConfigLoader, HTTPHandler):
    """ Main server process.
    """
    def __init__(self):
        self.host = None
        self.port = None
        self.crypto_manager = None
        self.odb = None
        self.odb_data = None
        self.config = None
        self.repo_location = None
        self.user_conf_location = None
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
        self.pickup_config = None
        self.connector_server_grace_time = None
        self.id = None
        self.name = None
        self.worker_id = None
        self.worker_pid = None
        self.cluster = None
        self.cluster_id = None
        self.kvdb = None
        self.startup_jobs = None
        self.worker_store = None
        self.request_dispatcher_dispatch = None
        self.deployment_lock_expires = None
        self.deployment_lock_timeout = None
        self.deployment_key = ''
        self.app_context = None
        self.has_gevent = None
        self.delivery_store = None
        self.static_config = None
        self.component_enabled = Bunch()
        self.client_address_headers = ['HTTP_X_ZATO_FORWARDED_FOR', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']
        self.broker_client = None
        self.return_tracebacks = None
        self.default_error_message = None
        self.time_util = None
        self.preferred_address = None
        self.crypto_use_tls = None
        self.servers = None
        self.zato_lock_manager = None
        self.pid = None
        self.sync_internal = None
        self.ipc_api = IPCAPI(False)
        self.ipc_forwarder = IPCAPI(True)
        self.fifo_response_buffer_size = 0.1 # In megabytes
        self.live_msg_browser = None
        self.is_first_worker = None
        self.shmem_size = -1.0
        self.server_startup_ipc = ServerStartupIPC()

        # Allows users store arbitrary data across service invocations
        self.user_ctx = Bunch()
        self.user_ctx_lock = gevent.lock.RLock()

        self.access_logger = logging.getLogger('zato_access_log')
        self.access_logger_log = self.access_logger._log
        self.needs_access_log = self.access_logger.isEnabledFor(INFO)
        self.has_pubsub_audit_log = logging.getLogger('zato_pubsub_audit').isEnabledFor('INFO')

        # The main config store
        self.config = ConfigStore()

        gevent.signal(signal.SIGINT, self.destroy)

# ################################################################################################################################

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
                    msg.action = HOT_DEPLOY.CREATE_SERVICE.value
                    msg.msg_type = MESSAGE_TYPE.TO_PARALLEL_ALL
                    msg.package_id = hot_deploy(self, file_name, full_path, notify=False)

                    # .. and tell the worker to actually deploy all the services the package contains.
                    gevent.spawn(self.worker_store.on_broker_msg_HOT_DEPLOY_CREATE_SERVICE, msg)

                    logger.info('Deployed an extra service found: %s (%s)', name, service_id)

# ################################################################################################################################

    def maybe_on_first_worker(self, server, redis_conn):
        """ This method will execute code with a distibuted lock held. We need a lock because we can have multiple worker
        processes fighting over the right to redeploy services. The first worker to grab the lock will actually perform
        the redeployment and set a flag meaning that for this particular deployment key (and remember that each server restart
        means a new deployment key) the services have been already deployed. Further workers will check that the flag exists
        and will skip the deployment altogether.
        """
        def import_initial_services_jobs(is_first):
            # (re-)deploy the services from a clear state
            locally_deployed = []

            locally_deployed.extend(self.service_store.import_internal_services(
                self.internal_service_modules, self.base_dir, self.sync_internal, is_first))

            locally_deployed.extend(self.service_store.import_services_from_anywhere(
                self.service_modules + self.service_sources, self.base_dir))

            return set(locally_deployed)

        lock_name = '{}{}:{}'.format(KVDB.LOCK_SERVER_STARTING, self.fs_server_config.main.token, self.deployment_key)
        already_deployed_flag = '{}{}:{}'.format(KVDB.LOCK_SERVER_ALREADY_DEPLOYED,
            self.fs_server_config.main.token, self.deployment_key)

        logger.debug('Will use the lock_name: `%s`', lock_name)

        with self.zato_lock_manager(lock_name, ttl=self.deployment_lock_expires, block=self.deployment_lock_timeout):
            if redis_conn.get(already_deployed_flag):
                # There has been already the first worker who's done everything there is to be done so we may just return.
                is_first = False
                logger.debug('Not attempting to grab the lock_name:`%s`', lock_name)

                # Simply deploy services, including any missing ones, the first worker has already cleared out the ODB
                locally_deployed = import_initial_services_jobs(is_first)

                return is_first, locally_deployed

            else:
                # We are this server's first worker so we need to re-populate
                # the database and create the flag indicating we're done.
                is_first = True
                logger.debug('Got lock_name:`%s`, ttl:`%s`', lock_name, self.deployment_lock_expires)

                # .. Remove all the deployed services from the DB ..
                self.odb.drop_deployed_services(server.id)

                # .. deploy them back including any missing ones found on other servers.
                locally_deployed = import_initial_services_jobs(is_first)

                # Add the flag to Redis indicating that this server has already
                # deployed its services. Note that by default the expiration
                # time is more than a century in the future. It will be cleared out
                # next time the server will be started.

                redis_conn.set(already_deployed_flag, dumps({'create_time_utc':datetime.utcnow().isoformat()}))
                redis_conn.expire(already_deployed_flag, self.deployment_lock_expires)

                return is_first, locally_deployed

# ################################################################################################################################

    def get_full_name(self):
        """ Returns this server's full name in the form of server@cluster.
        """
        return '{}@{}'.format(self.name, self.cluster.name)

# ################################################################################################################################

    def _after_init_common(self, server):
        """ Initializes parts of the server that don't depend on whether the
        server's been allowed to join the cluster or not.
        """
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

        # TimeUtil needs self.kvdb so it can be set now
        self.time_util = TimeUtil(self.kvdb)

        # Service sources
        self.service_sources = []
        for name in open(os.path.join(self.repo_location, self.fs_server_config.main.service_sources)):
            name = name.strip()
            if name and not name.startswith('#'):
                self.service_sources.append(name)

        # User-config from ./config/repo/user-config
        for file_name in os.listdir(self.user_conf_location):
            conf = get_config(self.user_conf_location, file_name)

            # Not used at all in this type of configuration
            conf.pop('user_config_items', None)

            self.user_config[get_user_config_name(file_name)] = conf

        # Convert size of FIFO response buffers to megabytes
        self.fifo_response_buffer_size = int(float(self.fs_server_config.misc.fifo_response_buffer_size) * megabyte)

        is_first, locally_deployed = self.maybe_on_first_worker(server, self.kvdb.conn)

        return is_first, locally_deployed

# ################################################################################################################################

    def set_odb_pool(self):
        # This is the call that creates an SQLAlchemy connection
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.config.odb_data
        self.odb.pool = self.sql_pool_store[ZATO_ODB_POOL_NAME].pool
        self.odb.token = self.config.odb_data.token

# ################################################################################################################################

    @staticmethod
    def start_server(parallel_server, zato_deployment_key=None):

        # Easier to type
        self = parallel_server

        # This cannot be done in __init__ because each sub-process obviously has its own PID
        self.pid = os.getpid()

        # This also cannot be done in __init__ which doesn't have this variable yet
        self.is_first_worker = int(os.environ['ZATO_SERVER_WORKER_IDX']) == 0

        # Used later on
        use_tls = asbool(self.fs_server_config.crypto.use_tls)

        # Will be None if we are not running in background.
        if not zato_deployment_key:
            zato_deployment_key = '{}.{}'.format(datetime.utcnow().isoformat(), uuid4().hex)

        self.deployment_key = zato_deployment_key

        register_diag_handlers()

        # Create all POSIX IPC objects now that we have the deployment key
        self.shmem_size = int(float(self.fs_server_config.shmem.size) * 10**6) # Convert to megabytes as integer
        self.server_startup_ipc.create(self.deployment_key, self.shmem_size)

        # Store the ODB configuration, create an ODB connection pool and have self.odb use it
        self.config.odb_data = self.get_config_odb_data(self)
        self.set_odb_pool()

        # Now try grabbing the basic server's data from the ODB. No point
        # in doing anything else if we can't get past this point.
        server = self.odb.fetch_server(self.config.odb_data)

        if not server:
            raise Exception('Server does not exist in the ODB')

        # Set up the server-wide default lock manager
        odb_data = self.config.odb_data
        backend_type = 'fcntl' if odb_data.engine == 'sqlite' else odb_data.engine
        self.zato_lock_manager = LockManager(backend_type, 'zato', self.odb.session)

        # Just to make sure distributed locking is configured correctly
        with self.zato_lock_manager(uuid4().hex):
            pass

        # Basic metadata
        self.id = server.id
        self.name = server.name
        self.cluster_id = server.cluster_id
        self.cluster = self.odb.cluster
        self.worker_id = '{}.{}.{}.{}'.format(self.cluster_id, self.id, self.worker_pid, new_cid())

        # Looked up upfront here and assigned to services in their store
        self.enforce_service_invokes = asbool(self.fs_server_config.misc.enforce_service_invokes)

        # For server-to-server communication
        self.servers = Servers(self.odb, self.cluster.name)
        logger.info('Preferred address of `%s@%s` (pid: %s) is `http%s://%s:%s`', self.name,
            self.cluster.name, self.pid, 's' if use_tls else '', self.preferred_address,
            self.port)

        # Reads in all configuration from ODB
        self.worker_store = WorkerStore(self.config, self)
        self.worker_store.invoke_matcher.read_config(self.fs_server_config.invoke_patterns_allowed)
        self.worker_store.target_matcher.read_config(self.fs_server_config.invoke_target_patterns_allowed)
        self.set_up_config(server)

        # Deploys services
        is_first, locally_deployed = self._after_init_common(server)

        # Initializes worker store, including connectors
        self.worker_store.init()
        self.request_dispatcher_dispatch = self.worker_store.request_dispatcher.dispatch

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

        self._after_init_accepted(locally_deployed)

        broker_callbacks = {
            TOPICS[MESSAGE_TYPE.TO_PARALLEL_ANY]: self.worker_store.on_broker_msg,
            TOPICS[MESSAGE_TYPE.TO_PARALLEL_ALL]: self.worker_store.on_broker_msg,
        }

        self.broker_client = BrokerClient(self.kvdb, 'parallel', broker_callbacks, self.get_lua_programs())
        self.worker_store.set_broker_client(self.broker_client)

        self.odb.server_up_down(server.token, SERVER_UP_STATUS.RUNNING, True, self.host,
            self.port, self.preferred_address, use_tls)

        # Startup services
        if is_first:
            self.invoke_startup_services(is_first)
            spawn_greenlet(self.set_up_pickup)

        # IPC
        if is_first:
            self.ipc_forwarder.name = self.name
            self.ipc_forwarder.pid = self.pid
            spawn_greenlet(self.ipc_forwarder.run)

        # IPC
        self.ipc_api.name = self.name
        self.ipc_api.pid = self.pid
        self.ipc_api.on_message_callback = self.worker_store.on_ipc_message
        spawn_greenlet(self.ipc_api.run)

        logger.info('Started `%s@%s` (pid: %s)', server.name, server.cluster.name, self.pid)

# ################################################################################################################################


    def invoke_startup_services(self, is_first):
        _invoke_startup_services(
            'Parallel', 'startup_services_first_worker' if is_first else 'startup_services_any_worker',
            self.fs_server_config, self.repo_location, self.broker_client, 'zato.notif.init-notifiers')

# ################################################################################################################################

    def set_up_pickup(self):

        empty = []

        # Fix up booleans and paths
        for stanza, stanza_config in self.pickup_config.items():

            # user_config_items is empty by default
            if not stanza_config:
                empty.append(stanza)
                continue

            stanza_config.read_on_pickup = asbool(stanza_config.get('read_on_pickup', True))
            stanza_config.parse_on_pickup = asbool(stanza_config.get('parse_on_pickup', True))
            stanza_config.delete_after_pick_up = asbool(stanza_config.get('delete_after_pick_up', True))
            stanza_config.case_insensitive = asbool(stanza_config.get('case_insensitive', True))
            stanza_config.pickup_from = absolutize(stanza_config.pickup_from, self.base_dir)
            stanza_config.is_service_hot_deploy = False

            mpt = stanza_config.get('move_processed_to')
            stanza_config.move_processed_to = absolutize(mpt, self.base_dir) if mpt else None

            recipients = stanza_config.recipients
            stanza_config.recipients = [recipients] if not isinstance(recipients, list) else recipients

            flags = globre.EXACT

            if stanza_config.case_insensitive:
                flags |= IGNORECASE

            patterns = stanza_config.patterns
            stanza_config.patterns = [patterns] if not isinstance(patterns, list) else patterns
            stanza_config.patterns = [globre.compile(elem, flags) for elem in stanza_config.patterns]

            if not os.path.exists(stanza_config.pickup_from):
                logger.warn('Pickup dir `%s` does not exist (%s)', stanza_config.pickup_from, stanza)

        for item in empty:
            del self.pickup_config[item]

        # Ok, now that we have configured everything that pickup.conf had
        # we still need to make it aware of services and how to pick them up from FS.

        stanza = 'zato_internal_service_hot_deploy'
        stanza_config = Bunch({
            'pickup_from': absolutize(self.fs_server_config.hot_deploy.pickup_dir, self.repo_location),
            'patterns': [globre.compile('*.py', globre.EXACT | IGNORECASE)],
            'read_on_pickup': False,
            'parse_on_pickup': False,
            'delete_after_pick_up': self.hot_deploy_config.delete_after_pick_up,
            'is_service_hot_deploy': True,
        })

        self.pickup_config[stanza] = stanza_config
        self.pickup = PickupManager(self, self.pickup_config)

        spawn_greenlet(self.pickup.run)

# ################################################################################################################################

    def invoke_all_pids(self, service, request, timeout=5, *args, **kwargs):
        """ Invokes a given service in each of processes current server has.
        """
        # PID -> response from that process
        out = {}

        # Get all current PIDs
        data = self.invoke('zato.info.get-worker-pids', serialize=False).getvalue(False)
        pids = data['response']['pids']

        # Underlying IPC needs strings on input instead of None
        request = request or ''

        for pid in pids:
            response = {
                'is_ok': False,
                'pid_data': None,
                'error_info': None
            }

            try:
                by_pid_response = self.invoke_by_pid(service, request, pid, timeout=timeout, *args, **kwargs)
                is_ok, pid_data = by_pid_response
                response['is_ok'] = is_ok
                response['pid_data' if is_ok else 'error_info'] = pid_data
            except Exception, e:
                response['error_info'] = format_exc(e)
            finally:
                out[pid] = response

        return out

# ################################################################################################################################

    def invoke_by_pid(self, service, request, target_pid, *args, **kwargs):
        """ Invokes a service in a worker process by the latter's PID.
        """
        return self.ipc_api.invoke_by_pid(service, request, target_pid, self.fifo_response_buffer_size, *args, **kwargs)

# ################################################################################################################################

    def invoke(self, service, request=None, *args, **kwargs):
        """ Invokes a service either in our own worker or, if PID is given on input, in another process of this server.
        """
        target_pid = kwargs.pop('pid', None)
        if target_pid and target_pid != self.pid:

            # We need it only in the other branch, not here.
            kwargs.pop('data_format', None)

            return self.invoke_by_pid(service, request, target_pid, *args, **kwargs)
        else:
            return self.worker_store.invoke(
                service, request,
                data_format=kwargs.pop('data_format', DATA_FORMAT.DICT),
                serialize=kwargs.pop('serialize', True),
                *args, **kwargs)

# ################################################################################################################################

    def invoke_async(self, service, request, callback, *args, **kwargs):
        """ Invokes a service in background.
        """
        return self.worker_store.invoke(service, request, is_async=True, callback=callback, *args, **kwargs)

# ################################################################################################################################

    def deliver_pubsub_msg(self, msg):
        """ A callback method invoked by pub/sub delivery tasks for each messages that is to be delivered.
        """
        self.invoke('pubapi1.deliver-message', msg)

# ################################################################################################################################

    @staticmethod
    def post_fork(arbiter, worker):
        """ A Gunicorn hook which initializes the worker.
        """
        worker.app.zato_wsgi_app.worker_pid = worker.pid
        ParallelServer.start_server(worker.app.zato_wsgi_app, arbiter.zato_deployment_key)

# ################################################################################################################################

    @staticmethod
    def on_starting(arbiter):
        """ A Gunicorn hook for setting the deployment key for this particular
        set of server processes. It needs to be added to the arbiter because
        we want for each worker to be (re-)started to see the same key.
        """
        setattr(arbiter, 'zato_deployment_key', '{}.{}'.format(datetime.utcnow().isoformat(), uuid4().hex))

# ################################################################################################################################

    def destroy(self):
        """ A Spring Python hook for closing down all the resources held.
        """
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

        # Per-worker cleanup
        else:

            # Close all POSIX IPC structures
            self.server_startup_ipc.close()

            self.invoke('zato.channel.web-socket.client.delete-by-server')
            self.invoke('zato.channel.web-socket.client.delete-by-server')

    # Convenience API
    stop = destroy

# ################################################################################################################################

    def notify_new_package(self, package_id):
        """ Publishes a message on the broker so all the servers (this one including
        can deploy a new package).
        """
        msg = {'action': HOT_DEPLOY.CREATE_SERVICE.value, 'package_id': package_id}
        self.broker_client.publish(msg)

# ################################################################################################################################
