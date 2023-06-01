# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from datetime import datetime, timedelta
from logging import DEBUG, INFO, WARN
from pathlib import Path
from platform import system as platform_system
from random import seed as random_seed
from tempfile import mkstemp
from traceback import format_exc
from uuid import uuid4

# gevent
from gevent import sleep
from gevent.lock import RLock

# Needed for Cassandra
import gevent.monkey # type: ignore
gevent.monkey        # type: ignore

# Paste
from paste.util.converters import asbool

# Zato
from zato.broker import BrokerMessageReceiver
from zato.broker.client import BrokerClient
from zato.bunch import Bunch
from zato.common.api import DATA_FORMAT, default_internal_modules, HotDeploy, IPC, KVDB as CommonKVDB, RATE_LIMIT, \
    SERVER_STARTUP, SEC_DEF_TYPE, SERVER_UP_STATUS, ZatoKVDB as CommonZatoKVDB, ZATO_ODB_POOL_NAME
from zato.common.audit import audit_pii
from zato.common.audit_log import AuditLog
from zato.common.broker_message import HOT_DEPLOY, MESSAGE_TYPE
from zato.common.const import SECRETS
from zato.common.events.common import Default as EventsDefault
from zato.common.ipc.api import IPCAPI
from zato.common.json_internal import dumps, loads
from zato.common.kv_data import KVDataAPI
from zato.common.kvdb.api import KVDB
from zato.common.marshal_.api import MarshalAPI
from zato.common.oauth import OAuthStore, OAuthTokenClient
from zato.common.odb.api import PoolStore
from zato.common.odb.post_process import ODBPostProcess
from zato.common.pubsub import SkipDelivery
from zato.common.rate_limiting import RateLimiting
from zato.common.typing_ import cast_, intnone, optional
from zato.common.util.api import absolutize, get_config_from_file, get_kvdb_config_for_log, get_user_config_name, \
    fs_safe_name, hot_deploy, invoke_startup_services as _invoke_startup_services, new_cid, register_diag_handlers, \
    save_ipc_pid_port, spawn_greenlet, StaticConfig
from zato.common.util.file_transfer import path_string_list_to_list
from zato.common.util.json_ import BasicParser
from zato.common.util.platform_ import is_posix
from zato.common.util.posix_ipc_ import ConnectorConfigIPC, ServerStartupIPC
from zato.common.util.time_ import TimeUtil
from zato.common.util.tcp import wait_until_port_taken
from zato.distlock import LockManager
from zato.server.base.worker import WorkerStore
from zato.server.config import ConfigStore
from zato.server.connection.stats import ServiceStatsClient
from zato.server.connection.server.rpc.api import ConfigCtx as _ServerRPC_ConfigCtx, ServerRPC
from zato.server.connection.server.rpc.config import ODBConfigSource
from zato.server.connection.kvdb.api import KVDB as ZatoKVDB
from zato.server.base.parallel.config import ConfigLoader
from zato.server.base.parallel.http import HTTPHandler
from zato.server.base.parallel.subprocess_.api import CurrentState as SubprocessCurrentState, \
     StartConfig as SubprocessStartConfig
from zato.server.base.parallel.subprocess_.ftp import FTPIPC
from zato.server.base.parallel.subprocess_.ibm_mq import IBMMQIPC
from zato.server.base.parallel.subprocess_.zato_events import ZatoEventsIPC
from zato.server.base.parallel.subprocess_.outconn_sftp import SFTPIPC
from zato.server.sso import SSOTool

# ################################################################################################################################
# ################################################################################################################################

if 0:

    # Zato
    from zato.common.crypto.api import ServerCryptoManager
    from zato.common.odb.api import ODBManager
    from zato.common.odb.model import Cluster as ClusterModel
    from zato.common.typing_ import any_, anydict, anylist, anyset, callable_, strbytes, strlist, strnone
    from zato.server.commands import CommandResult
    from zato.server.connection.cache import Cache, CacheAPI
    from zato.server.connection.connector.subprocess_.ipc import SubprocessIPC
    from zato.server.ext.zunicorn.arbiter import Arbiter
    from zato.server.ext.zunicorn.workers.ggevent import GeventWorker
    from zato.server.service.store import ServiceStore
    from zato.simpleio import SIOServerConfig
    from zato.server.startup_callable import StartupCallableTool
    from zato.sso.api import SSOAPI

    ODBManager = ODBManager
    ServerCryptoManager = ServerCryptoManager
    ServiceStore = ServiceStore
    SIOServerConfig = SIOServerConfig
    SSOAPI = SSOAPI # type: ignore
    StartupCallableTool = StartupCallableTool
    SubprocessIPC = SubprocessIPC

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
kvdb_logger = logging.getLogger('zato_kvdb')

# ################################################################################################################################
# ################################################################################################################################

megabyte = 10 ** 6

# ################################################################################################################################
# ################################################################################################################################

_ipc_timeout = IPC.Default.Timeout

# ################################################################################################################################
# ################################################################################################################################

class ParallelServer(BrokerMessageReceiver, ConfigLoader, HTTPHandler):
    """ Main server process.
    """
    odb: 'ODBManager'
    kvdb: 'KVDB'
    config: 'ConfigStore'
    crypto_manager: 'ServerCryptoManager'
    sql_pool_store: 'PoolStore'
    kv_data_api: 'KVDataAPI'
    on_wsgi_request: 'any_'

    cluster: 'ClusterModel'
    worker_store: 'WorkerStore'
    service_store: 'ServiceStore'

    rpc: 'ServerRPC'
    sso_api: 'SSOAPI'
    rate_limiting: 'RateLimiting'
    broker_client: 'BrokerClient'
    zato_lock_manager: 'LockManager'
    startup_callable_tool: 'StartupCallableTool'
    oauth_store: 'OAuthStore'

    stop_after: 'intnone'
    deploy_auto_from: 'str' = ''

    def __init__(self) -> 'None':
        self.logger = logger
        self.host = ''
        self.port = -1
        self.is_starting_first = '<not-set>'
        self.odb_data = Bunch()
        self.repo_location = ''
        self.user_conf_location = []
        self.user_conf_location_extra = set()
        self.soap11_content_type = ''
        self.soap12_content_type = ''
        self.plain_xml_content_type = ''
        self.json_content_type = ''
        self.service_modules = []
        self.service_sources = []   # Set in a config file
        self.base_dir = ''
        self.logs_dir = ''
        self.tls_dir = ''
        self.static_dir = ''
        self.json_schema_dir = 'server-'
        self.sftp_channel_dir = 'server-'
        self.hot_deploy_config = Bunch()
        self.fs_server_config = None # type: any_
        self.fs_sql_config = Bunch()
        self.pickup_config = Bunch()
        self.logging_config = Bunch()
        self.logging_conf_path = 'server-'
        self.sio_config = cast_('SIOServerConfig', None)
        self.sso_config = Bunch()
        self.connector_server_grace_time = None
        self.id = -1
        self.name = ''
        self.worker_id = ''
        self.worker_pid = -1
        self.cluster_id = -1
        self.cluster_name = ''
        self.startup_jobs = {}
        self.deployment_lock_expires = -1
        self.deployment_lock_timeout = -1
        self.deployment_key = ''
        self.has_gevent = True
        self.request_dispatcher_dispatch = cast_('callable_', None)
        self.delivery_store = None
        self.static_config = Bunch()
        self.component_enabled = Bunch()
        self.client_address_headers = ['HTTP_X_ZATO_FORWARDED_FOR', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']
        self.return_tracebacks = False
        self.default_error_message = ''
        self.time_util = TimeUtil()
        self.preferred_address = ''
        self.crypto_use_tls = False
        self.pid = -1
        self.sync_internal = False
        self.ipc_api = IPCAPI()
        self.fifo_response_buffer_size = -1
        self.is_first_worker = False
        self.process_idx = -1
        self.shmem_size = -1.0
        self.server_startup_ipc = ServerStartupIPC()
        self.connector_config_ipc = ConnectorConfigIPC()
        self.is_sso_enabled = False
        self.audit_pii = audit_pii
        self.has_fg = False
        self.default_internal_pubsub_endpoint_id = 0
        self.jwt_secret = b''
        self._hash_secret_method = ''
        self._hash_secret_rounds = -1
        self._hash_secret_salt_size = -1
        self.sso_tool = SSOTool(self)
        self.platform_system = platform_system().lower()
        self.has_posix_ipc = is_posix
        self.user_config = Bunch()
        self.stderr_path = ''
        self.work_dir = 'ParallelServer-work_dir'
        self.events_dir = 'ParallelServer-events_dir'
        self.kvdb_dir = 'ParallelServer-kvdb_dir'
        self.marshal_api = MarshalAPI()
        self.env_manager = None # This is taken from util/zato_environment.py:EnvironmentManager
        self.enforce_service_invokes = False
        self.json_parser = BasicParser()

        # A server-wide publication counter, indicating which one the current publication is,
        # increased after each successful publication.
        self.pub_counter = 1

        # A lock to guard the publication counter.
        self.pub_counter_lock = RLock()

        # Transient API for in-RAM messages
        self.zato_kvdb = ZatoKVDB()

        # In-RAM statistics
        self.slow_responses = self.zato_kvdb.internal_create_list_repo(CommonZatoKVDB.SlowResponsesName)
        self.usage_samples = self.zato_kvdb.internal_create_list_repo(CommonZatoKVDB.UsageSamplesName)
        self.current_usage = self.zato_kvdb.internal_create_number_repo(CommonZatoKVDB.CurrentUsageName)
        self.pub_sub_metadata = self.zato_kvdb.internal_create_object_repo(CommonZatoKVDB.PubSubMetadataName)

        self.stats_client = ServiceStatsClient()
        self._stats_host = '<ParallelServer-_stats_host>'
        self._stats_port = -1

        # Audit log
        self.audit_log = AuditLog()

        # Current state of subprocess-based connectors
        self.subproc_current_state = SubprocessCurrentState()

        # Our arbiter may potentially call the cleanup procedure multiple times
        # and this will be set to True the first time around.
        self._is_process_closing = False

        # Internal caches - not to be used by user services
        self.internal_cache_patterns = {}
        self.internal_cache_lock_patterns = RLock()

        # Allows users store arbitrary data across service invocations
        self.user_ctx = Bunch()
        self.user_ctx_lock = RLock()

        # Connectors
        self.connector_ftp    = FTPIPC(self)
        self.connector_ibm_mq = IBMMQIPC(self)
        self.connector_sftp   = SFTPIPC(self)
        self.connector_events = ZatoEventsIPC(self)

        # HTTP methods allowed as a Python list
        self.http_methods_allowed = []

        # As above, but as a regular expression pattern
        self.http_methods_allowed_re = ''

        self.access_logger = logging.getLogger('zato_access_log')
        self.access_logger_log = self.access_logger._log
        self.needs_access_log = self.access_logger.isEnabledFor(INFO)
        self.needs_all_access_log = True
        self.access_log_ignore = set()
        self.has_pubsub_audit_log = logging.getLogger('zato_pubsub_audit').isEnabledFor(DEBUG)
        self.is_enabled_for_warn = logging.getLogger('zato').isEnabledFor(WARN)
        self.is_admin_enabled_for_info = logging.getLogger('zato_admin').isEnabledFor(INFO)

        # The main config store
        self.config = ConfigStore()

# ################################################################################################################################

    def set_ipc_password(self, password:'str') -> 'None':
        password = self.decrypt(password)
        self.ipc_api.password = password

# ################################################################################################################################

    def get_default_internal_pubsub_endpoint_id(self) -> 'int':

        # This value defaults to 0 and we populate it with the real value in self._after_init_accepted.
        return self.default_internal_pubsub_endpoint_id

# ################################################################################################################################

    def deploy_missing_services(self, locally_deployed:'anylist') -> 'None':
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
            missing = self.odb.get_missing_services(other_server, {item.name for item in locally_deployed})

            if missing:

                logger.info('Found extra services to deploy: %s', ', '.join(sorted(item.name for item in missing)))

                # (file_name, source_path) -> a list of services it contains
                modules = {}

                # Coalesce all service modules - it is possible that each one has multiple services
                # so we do want to deploy the same module over for each service found.
                for _ignored_service_id, name, source_path, source in missing:
                    file_name = os.path.basename(source_path)
                    _, tmp_full_path = mkstemp(suffix='-'+ file_name)

                    # Module names are unique so they can serve as keys
                    key = file_name

                    if key not in modules:
                        modules[key] = {
                            'tmp_full_path': tmp_full_path,
                            'services': [name] # We can append initial name already in this 'if' branch
                        }

                        # Save the source code only once here
                        f = open(tmp_full_path, 'wb')
                        _ = f.write(source)
                        f.close()

                    else:
                        modules[key]['services'].append(name)

                # Create a deployment package in ODB out of which all the services will be picked up ..
                for file_name, values in modules.items():
                    msg = Bunch()
                    msg.action = HOT_DEPLOY.CREATE_SERVICE.value
                    msg.msg_type = MESSAGE_TYPE.TO_PARALLEL_ALL
                    msg.package_id = hot_deploy(self, file_name, values['tmp_full_path'], notify=False)

                    # .. and tell the worker to actually deploy all the services the package contains.
                    # gevent.spawn(self.worker_store.on_broker_msg_HOT_DEPLOY_CREATE_SERVICE, msg)
                    self.worker_store.on_broker_msg_HOT_DEPLOY_CREATE_SERVICE(msg)

                    logger.info('Deployed extra services found: %s', sorted(values['services']))

# ################################################################################################################################

    def maybe_on_first_worker(self, server:'ParallelServer') -> 'anyset':
        """ This method will execute code with a distibuted lock held. We need a lock because we can have multiple worker
        processes fighting over the right to redeploy services. The first worker to obtain the lock will actually perform
        the redeployment and set a flag meaning that for this particular deployment key (and remember that each server restart
        means a new deployment key) the services have been already deployed. Further workers will check that the flag exists
        and will skip the deployment altogether.
        """
        def import_initial_services_jobs() -> 'anyset':

            # All non-internal services that we have deployed
            locally_deployed = []

            # Internal modules with that are potentially to be deployed
            internal_service_modules = []

            # This was added between 3.0 and 3.1, which is why it is optional
            deploy_internal = self.fs_server_config.get('deploy_internal', default_internal_modules)

            # Above, we potentially got the list of internal modules to be deployed as they were defined in server.conf.
            # However, if someone creates an environment and then we add a new module, this module will not neccessarily
            # exist in server.conf. This is why we need to add any such missing ones explicitly below.
            for internal_module, is_enabled in default_internal_modules.items():
                if internal_module not in deploy_internal:
                    deploy_internal[internal_module] = is_enabled

            # All internal modules were found, now we can build a list of what is to be enabled.
            for module_name, is_enabled in deploy_internal.items():
                if is_enabled:
                    internal_service_modules.append(module_name)

            locally_deployed.extend(self.service_store.import_internal_services(
                internal_service_modules, self.base_dir, self.sync_internal, cast_('bool', self.is_starting_first)))

            logger.info('Deploying user-defined services (%s)', self.name)

            user_defined_deployed = self.service_store.import_services_from_anywhere(
                self.service_modules + self.service_sources, self.base_dir).to_process

            locally_deployed.extend(user_defined_deployed)
            len_user_defined_deployed = len(user_defined_deployed)

            suffix = ' ' if len_user_defined_deployed == 1 else 's '

            logger.info('Deployed %d user-defined service%s (%s)', len_user_defined_deployed, suffix, self.name)

            return set(locally_deployed)

        lock_name = '{}{}:{}'.format(
            CommonKVDB.LOCK_SERVER_STARTING, self.fs_server_config.main.token, self.deployment_key)

        already_deployed_flag = '{}{}:{}'.format(
            CommonKVDB.LOCK_SERVER_ALREADY_DEPLOYED, self.fs_server_config.main.token, self.deployment_key)

        logger.debug('Using lock_name: `%s`', lock_name)

        with self.zato_lock_manager(lock_name, ttl=self.deployment_lock_expires, block=self.deployment_lock_timeout):
            if self.kv_data_api.get(already_deployed_flag):
                # There has been already the first worker who's done everything there is to be done so we may just return.
                self.is_starting_first = False
                logger.debug('Not attempting to obtain the lock_name:`%s`', lock_name)

                # Simply deploy services, including any missing ones, the first worker has already cleared out the ODB
                locally_deployed = import_initial_services_jobs()

                return locally_deployed

            else:
                # We are this server's first worker so we need to re-populate
                # the database and create the flag indicating we're done.
                self.is_starting_first = True
                logger.debug('Got lock_name:`%s`, ttl:`%s`', lock_name, self.deployment_lock_expires)

                # .. Remove all the deployed services from the DB ..
                self.odb.drop_deployed_services(server.id)

                # .. deploy them back including any missing ones found on other servers.
                locally_deployed = import_initial_services_jobs()

                # Add the flag to Redis indicating that this server has already
                # deployed its services. Note that by default the expiration
                # time is more than a century in the future. It will be cleared out
                # next time the server will be started.

                self.kv_data_api.set(
                    already_deployed_flag,
                    dumps({'create_time_utc':datetime.utcnow().isoformat()}),
                    self.deployment_lock_expires,
                )

                return locally_deployed

# ################################################################################################################################

    def get_full_name(self) -> 'str':
        """ Returns this server's full name in the form of server@cluster.
        """
        return '{}@{}'.format(self.name, self.cluster_name)

# ################################################################################################################################

    def add_pickup_conf_from_env(self) -> 'None':

        # Look up Python hot-deployment directories ..
        path = os.environ.get('ZATO_HOT_DEPLOY_DIR', '')

        # .. and make it possible to deploy from them.
        self._add_pickup_conf_from_local_path(path)

# ################################################################################################################################

    def add_pickup_conf_from_auto_deploy(self) -> 'None':

        # Look up Python hot-deployment directories ..
        path = os.path.join(self.deploy_auto_from, 'code')

        # .. and make it possible to deploy from them.
        self._add_pickup_conf_from_local_path(path)

# ################################################################################################################################

    def _add_pickup_conf_from_local_path(self, items:'str') -> 'None':

        # Bunch
        from bunch import bunchify

        # We have hot-deployment configuration to process ..
        if items:

            # .. support multiple entries ..
            items = items.split(':') # type: ignore
            items = [elem.strip() for elem in items] # type: ignore

            # .. add  the actual configuration ..
            for name in items:

                # .. log what we are about to do ..
                logger.info('Adding hot-deployment configuration from `%s` (env. variable found -> ZATO_HOT_DEPLOY_DIR)', name)

                # .. stay on the safe side because, here, we do not know where it will be used ..
                _fs_safe_name = fs_safe_name(name)

                # .. use this prefix to indicate that it is a directory to hot-deploy from ..
                key_name = '{}.{}'.format(HotDeploy.UserPrefix, _fs_safe_name)

                # .. and store the configuration for later use now.
                pickup_from = {
                    'pickup_from': name
                }
                self.pickup_config[key_name] = bunchify(pickup_from)

# ################################################################################################################################

    def add_user_conf_from_env(self) -> 'None':

        # Bunch
        from bunch import bunchify

        # Look up user-defined configuration directories
        items = os.environ.get('ZATO_USER_CONF_DIR', '')

        # Ignore files other than that
        suffixes = ['ini', 'conf']
        patterns = ['*.' + elem for elem in suffixes]
        patterns_str = ', '.join(patterns)

        # We have user-config details to process ..
        if items:

            # .. support multiple entries ..
            items = items.split(':')
            items = [elem.strip() for elem in items]

            # .. add  the actual configuration ..
            for name in items:

                # .. log what we are about to do ..
                logger.info('Adding user-config from `%s` (env. variable found -> ZATO_USER_CONF_DIR)', name)

                # .. look up files inside the directory and add the path to each
                # .. to a list of what should be loaded on startup ..
                if os.path.exists(name) and os.path.isdir(name):
                    file_item_list = os.listdir(name)
                    for file_item in file_item_list:
                        for suffix in suffixes:
                            if file_item.endswith(suffix):
                                self.user_conf_location_extra.add(name)

                # .. stay on the safe side because, here, we do not know where it will be used ..
                _fs_safe_name = fs_safe_name(name)

                # .. use this prefix to indicate that it is a directory to deploy user configuration from  ..
                key_name = '{}.{}'.format(HotDeploy.UserConfPrefix, _fs_safe_name)

                # .. and store the configuration for later use now.
                pickup_from = {
                    'pickup_from': name,
                    'patterns': patterns_str,
                    'parse_on_pickup': False,
                    'delete_after_pickup': False,
                    'services': 'zato.pickup.update-user-conf',
                }
                self.pickup_config[key_name] = bunchify(pickup_from)

# ################################################################################################################################

    def add_pickup_conf_from_env_variables(self) -> 'None':

        # Code hot-deployment
        self.add_pickup_conf_from_env()

        # User configuration
        self.add_user_conf_from_env()

# ################################################################################################################################

    def add_wsx_gateway_service_allowed(self) -> 'None':

        wsx_gateway_service_allowed = os.environ.get('Zato_WSX_Gateway_Service_Allowed', '')

        if wsx_gateway_service_allowed:

            config_wsx_gateway_service_allowed = self.fs_server_config.pubsub.wsx_gateway_service_allowed
            config_wsx_gateway_service_allowed = config_wsx_gateway_service_allowed or []

            self.fs_server_config.pubsub.wsx_gateway_service_allowed = config_wsx_gateway_service_allowed

            wsx_gateway_service_allowed = wsx_gateway_service_allowed.split(',')
            wsx_gateway_service_allowed = [elem.strip() for elem in wsx_gateway_service_allowed if elem]
            _ = self.fs_server_config.pubsub.wsx_gateway_service_allowed.extend(wsx_gateway_service_allowed)

# ################################################################################################################################

    def _after_init_common(self, server:'ParallelServer') -> 'anyset':
        """ Initializes parts of the server that don't depend on whether the server's been allowed to join the cluster or not.
        """
        def _normalise_service_source_path(name:'str') -> 'str':
            if not os.path.isabs(name):
                name = os.path.normpath(os.path.join(self.base_dir, name))
            return name

        # Patterns to match during deployment
        self.service_store.patterns_matcher.read_config(self.fs_server_config.deploy_patterns_allowed)

        # Static config files
        self.static_config = StaticConfig(self.static_dir)

        # SSO e-mail templates
        self.static_config.read_directory(os.path.join(self.static_dir, 'sso', 'email'))

        # Key-value DB
        kvdb_config = get_kvdb_config_for_log(self.fs_server_config.kvdb)
        kvdb_logger.info('Worker config `%s`', kvdb_config)

        self.kvdb.config = self.fs_server_config.kvdb
        self.kvdb.server = self
        self.kvdb.decrypt_func = self.crypto_manager.decrypt

        kvdb_logger.info('Worker config `%s`', kvdb_config)

        if self.fs_server_config.kvdb.host:
            self.kvdb.init()

        # New in 3.1, it may be missing in the config file
        if not self.fs_server_config.misc.get('sftp_genkey_command'):
            self.fs_server_config.misc.sftp_genkey_command = 'dropbearkey'

        # New in 3.2, may be missing in the config file
        allow_internal = self.fs_server_config.misc.get('service_invoker_allow_internal', [])
        allow_internal = allow_internal if isinstance(allow_internal, list) else [allow_internal]
        self.fs_server_config.misc.service_invoker_allow_internal = allow_internal

        # Service sources from server.conf
        for name in open(os.path.join(self.repo_location, self.fs_server_config.main.service_sources)):
            name = name.strip()
            if name and not name.startswith('#'):
                name = _normalise_service_source_path(name)
                self.service_sources.append(name)

        # Look up pickup configuration among environment variables
        # and add anything found to self.pickup_config.
        self.add_pickup_conf_from_env_variables()

        # Look up pickup configuration based on what should be auto-deployed on startup.
        if self.deploy_auto_from:
            self.add_pickup_conf_from_auto_deploy()

        # Append additional services that can be invoked through WebSocket gateways.
        self.add_wsx_gateway_service_allowed()

        # Service sources from user-defined hot-deployment configuration
        for key, value in self.pickup_config.items():
            if key.startswith(HotDeploy.UserPrefix):
                pickup_from = value.get('pickup_from')
                if pickup_from:
                    logger.info('Adding hot-deployment directory `%s` (HotDeploy.UserPrefix)', pickup_from)
                    pickup_from = _normalise_service_source_path(pickup_from)
                    self.service_sources.append(pickup_from)

        # Read all the user config files that are already available on startup
        self.read_user_config()

        # Convert size of FIFO response buffers to megabytes
        self.fifo_response_buffer_size = int(float(self.fs_server_config.misc.fifo_response_buffer_size) * megabyte)

        locally_deployed = self.maybe_on_first_worker(server)

        return locally_deployed

# ################################################################################################################################

    def _read_user_config_from_directory(self, dir_name:'str') -> 'None':

        # We assume that it will be always one of these file name suffixes
        suffixes_supported = ('.ini', '.conf')

        # User-config from ./config/repo/user-config
        for file_name in os.listdir(dir_name):

            # Reject files with suffixes that we do not recognize
            if not file_name.lower().endswith(suffixes_supported):
                continue

            user_conf_full_path = os.path.join(dir_name, file_name)
            user_config_name = get_user_config_name(file_name)
            conf = get_config_from_file(user_conf_full_path, file_name)

            # Not used at all in this type of configuration
            _ = conf.pop('user_config_items', None)

            self.user_config[user_config_name] = conf

            logger.info('Read user config `%s` from `%s` (dir:%s)', user_config_name, file_name, dir_name)

# ################################################################################################################################

    def read_user_config(self):

        # Reads config files from the default directory
        for dir_name in self.user_conf_location:
            self._read_user_config_from_directory(dir_name)

        # Reads config files from extra directories pointed to by ZATO_USER_CONF_DIR
        for dir_name in self.user_conf_location_extra:
            self._read_user_config_from_directory(dir_name)

# ################################################################################################################################

    def set_up_user_config_location(self) -> 'strlist':

        user_conf_location = self.pickup_config.get('user_conf', {}).get('pickup_from', '')
        return path_string_list_to_list(self.base_dir, user_conf_location)

# ################################################################################################################################

    def set_up_odb(self) -> 'None':
        # This is the call that creates an SQLAlchemy connection
        self.config.odb_data['fs_sql_config'] = self.fs_sql_config
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.config.odb_data
        self.odb.pool = self.sql_pool_store[ZATO_ODB_POOL_NAME].pool
        self.odb.token = self.config.odb_data.token.decode('utf8')
        self.odb.decrypt_func = self.decrypt

# ################################################################################################################################

    def build_server_rpc(self) -> 'ServerRPC':

        # What our configuration backend is
        config_source = ODBConfigSource(self.odb, self.cluster_name, self.name, self.decrypt)

        # A combination of backend and runtime configuration
        config_ctx = _ServerRPC_ConfigCtx(config_source, self)

        # A publicly available RPC client
        return ServerRPC(config_ctx)

# ################################################################################################################################

    def _run_stats_client(self, events_tcp_port:'int') -> 'None':
        self.stats_client.init('127.0.0.1', events_tcp_port)
        self.stats_client.run()

# ################################################################################################################################

    def _on_enmasse_completed(self, result:'CommandResult') -> 'None':

        self.logger.info('Enmasse stdout -> `%s`', result.stdout.strip())
        self.logger.info('Enmasse stderr -> `%s`', result.stderr.strip())

# ################################################################################################################################

    def handle_enmasse_auto_from(self) -> 'None':

        # Zato
        from zato.server.commands import CommandsFacade

        # Local aliases
        commands = CommandsFacade()
        commands.init(self)

        # Full path to a directory with enmasse files ..
        path = os.path.join(self.deploy_auto_from, 'enmasse')
        path = Path(path)

        # enmasse --import --replace-odb-objects --input ./zato-export.yml /path/to/server/

        # .. find all the enmasse files in this directory ..
        for file_path in sorted(path.iterdir()):

            command = f'enmasse --import --replace-odb-objects --input {file_path} {self.base_dir} --verbose'
            _ = commands.run_zato_cli_async(command, callback=self._on_enmasse_completed)

# ################################################################################################################################

    @staticmethod
    def start_server(parallel_server:'ParallelServer', zato_deployment_key:'str'='') -> 'None':

        # Easier to type
        self = parallel_server

        # This cannot be done in __init__ because each sub-process obviously has its own PID
        self.pid = os.getpid()

        # This also cannot be done in __init__ which doesn't have this variable yet
        self.process_idx = int(os.environ['ZATO_SERVER_WORKER_IDX'])
        self.is_first_worker = self.process_idx == 0

        # Used later on
        use_tls = asbool(self.fs_server_config.crypto.use_tls)

        # This changed in 3.2 so we need to take both into account
        self.work_dir = self.fs_server_config.main.get('work_dir') or self.fs_server_config.hot_deploy.get('work_dir')
        self.work_dir = os.path.normpath(os.path.join(self.repo_location, self.work_dir))

        # Make sure the directories for events exists
        events_dir_v1 = os.path.join(self.work_dir, 'events', 'v1')

        for name in 'v1', 'v2':
            full_path = os.path.join(self.work_dir, 'events', name)
            if not os.path.exists(full_path):
                os.makedirs(full_path, mode=0o770, exist_ok=True)

        # Set for later use - this is the version that we currently employ and we know that it exists.
        self.events_dir = events_dir_v1

        # Will be None if we are not running in background.
        if not zato_deployment_key:
            zato_deployment_key = '{}.{}'.format(datetime.utcnow().isoformat(), uuid4().hex)

        # Each time a server starts a new deployment key is generated to uniquely
        # identify this particular time the server is running.
        self.deployment_key = zato_deployment_key

        # This is to handle SIGURG signals.
        if is_posix:
            register_diag_handlers()

        # Configure paths and load data pertaining to Zato KVDB
        self.set_up_zato_kvdb()

        # Find out if we are on a platform that can handle our posix_ipc
        _skip_platform = self.fs_server_config.misc.get('posix_ipc_skip_platform')
        _skip_platform = _skip_platform if isinstance(_skip_platform, list) else [_skip_platform]
        _skip_platform = [elem for elem in _skip_platform if elem]
        self.fs_server_config.misc.posix_ipc_skip_platform = _skip_platform

        # Create all POSIX IPC objects now that we have the deployment key,
        # but only if our platform allows it.
        if self.has_posix_ipc:
            self.shmem_size = int(float(self.fs_server_config.shmem.size) * 10**6) # Convert to megabytes as integer
            self.server_startup_ipc.create(self.deployment_key, self.shmem_size)
            self.connector_config_ipc.create(self.deployment_key, self.shmem_size)
        else:
            self.server_startup_ipc = None
            self.connector_config_ipc = None

        # Store the ODB configuration, create an ODB connection pool and have self.odb use it
        self.config.odb_data = self.get_config_odb_data(self)
        self.set_up_odb()

        # Now try grabbing the basic server's data from the ODB. No point
        # in doing anything else if we can't get past this point.
        server = self.odb.fetch_server(self.config.odb_data)

        if not server:
            raise Exception('Server does not exist in the ODB')

        # Set up the server-wide default lock manager
        odb_data = self.config.odb_data

        if is_posix:
            backend_type = 'fcntl' if odb_data.engine == 'sqlite' else odb_data.engine
        else:
            backend_type = 'zato-pass-through'

        self.zato_lock_manager = LockManager(backend_type, 'zato', self.odb.session)

        # Just to make sure distributed locking is configured correctly
        with self.zato_lock_manager(uuid4().hex):
            pass

        # Basic metadata
        self.id = server.id
        self.name = server.name
        self.cluster = self.odb.cluster
        self.cluster_id = self.cluster.id
        self.cluster_name = self.cluster.name
        self.worker_id = '{}.{}.{}.{}'.format(self.cluster_id, self.id, self.worker_pid, new_cid())

        # SQL post-processing
        ODBPostProcess(self.odb.session(), None, self.cluster_id).run()

        # Set up SQL-based key/value API
        self.kv_data_api = KVDataAPI(cast_('int', self.cluster_id), self.odb)

        # Looked up upfront here and assigned to services in their store
        self.enforce_service_invokes = asbool(self.fs_server_config.misc.enforce_service_invokes)

        # For server-to-server RPC
        self.rpc = self.build_server_rpc()

        logger.info(
            'Preferred address of `%s@%s` (pid: %s) is `http%s://%s:%s`',
            self.name, self.cluster_name, self.pid, 's' if use_tls else '', self.preferred_address, self.port)

        # Configure which HTTP methods can be invoked via REST or SOAP channels
        methods_allowed = self.fs_server_config.http.methods_allowed
        methods_allowed = methods_allowed if isinstance(methods_allowed, list) else [methods_allowed]
        self.http_methods_allowed.extend(methods_allowed)

        # As above, as a regular expression to be used in pattern matching
        http_methods_allowed_re = '|'.join(self.http_methods_allowed)
        self.http_methods_allowed_re = '({})'.format(http_methods_allowed_re)

        # Reads in all configuration from ODB
        self.worker_store = WorkerStore(self.config, self)
        self.worker_store.invoke_matcher.read_config(self.fs_server_config.invoke_patterns_allowed)
        self.worker_store.target_matcher.read_config(self.fs_server_config.invoke_target_patterns_allowed)
        self.set_up_config(server) # type: ignore

        # Normalize hot-deploy configuration
        self.hot_deploy_config = Bunch()
        self.hot_deploy_config.pickup_dir = absolutize(self.fs_server_config.hot_deploy.pickup_dir, self.repo_location)
        self.hot_deploy_config.work_dir = self.work_dir
        self.hot_deploy_config.backup_history = int(self.fs_server_config.hot_deploy.backup_history)
        self.hot_deploy_config.backup_format = self.fs_server_config.hot_deploy.backup_format

        # The first name was used prior to v3.2, note pick_up vs. pickup
        if 'delete_after_pick_up':
            delete_after_pickup = self.fs_server_config.hot_deploy.get('delete_after_pick_up')
        else:
            delete_after_pickup = self.fs_server_config.hot_deploy.get('delete_after_pickup')

        self.hot_deploy_config.delete_after_pickup = delete_after_pickup

        # Added in 3.1, hence optional
        max_batch_size = int(self.fs_server_config.hot_deploy.get('max_batch_size', 1000))

        # Turn it into megabytes
        max_batch_size = max_batch_size * 1000

        # Finally, assign it to ServiceStore
        self.service_store.max_batch_size = max_batch_size

        # Rate limiting
        self.rate_limiting = RateLimiting()
        self.rate_limiting.cluster_id = cast_('int', self.cluster_id)
        self.rate_limiting.global_lock_func = self.zato_lock_manager
        self.rate_limiting.sql_session_func = self.odb.session

        # Set up rate limiting for ConfigDict-based objects, which includes everything except for:
        # * services  - configured in ServiceStore
        # * SSO       - configured in the next call
        self.set_up_rate_limiting()

        # Rate limiting for SSO
        self.set_up_sso_rate_limiting()

        # Some parts of the worker store's configuration are required during the deployment of services
        # which is why we are doing it here, before worker_store.init() is called.
        self.worker_store.early_init()

        # Deploys services
        locally_deployed = self._after_init_common(server) # type: ignore

        # Initializes worker store, including connectors
        self.worker_store.init()
        self.request_dispatcher_dispatch = self.worker_store.request_dispatcher.dispatch

        # Configure remaining parts of SSO
        self.configure_sso()

        # Configure the store to obtain OAuth tokens through
        self.set_up_oauth_store()

        # Cannot be done in __init__ because self.sso_config is not available there yet
        salt_size = self.sso_config.hash_secret.salt_size
        self.crypto_manager.add_hash_scheme('zato.default', self.sso_config.hash_secret.rounds, salt_size)

        # Support pre-3.x hot-deployment directories
        for name in('current_work_dir', 'backup_work_dir', 'last_backup_work_dir', 'delete_after_pickup'):

            # New in 2.0
            if name == 'delete_after_pickup':

                # For backward compatibility, we need to support both names
                old_name = 'delete_after_pick_up'

                if old_name in self.fs_server_config.hot_deploy:
                    _name = old_name
                else:
                    _name = name

                value = asbool(self.fs_server_config.hot_deploy.get(_name, True))
                self.hot_deploy_config[name] = value
            else:
                self.hot_deploy_config[name] = os.path.normpath(os.path.join(
                    self.hot_deploy_config.work_dir, self.fs_server_config.hot_deploy[name]))

        self.broker_client = BrokerClient(
            server_rpc=self.rpc, zato_client=None, scheduler_config=self.fs_server_config.scheduler)
        self.worker_store.set_broker_client(self.broker_client)

        self._after_init_accepted(locally_deployed)
        self.odb.server_up_down(
            server.token, SERVER_UP_STATUS.RUNNING, True, self.host, self.port, self.preferred_address, use_tls)

        # These flags are needed if we are the first worker or not
        has_ibm_mq = bool(self.worker_store.worker_config.definition_wmq.keys()) \
            and self.fs_server_config.component_enabled.ibm_mq
        has_sftp = bool(self.worker_store.worker_config.out_sftp.keys())
        has_stats = self.fs_server_config.component_enabled.stats

        subprocess_start_config = SubprocessStartConfig()

        subprocess_start_config.has_ibm_mq = has_ibm_mq
        subprocess_start_config.has_sftp   = has_sftp
        subprocess_start_config.has_stats  = has_stats

        # Directories for SSH keys used by SFTP channels
        self.sftp_channel_dir = os.path.join(self.repo_location, 'sftp', 'channel')

        # This is the first process
        if self.is_starting_first:

            logger.info('First worker of `%s` is %s', self.name, self.pid)

            self.startup_callable_tool.invoke(SERVER_STARTUP.PHASE.IN_PROCESS_FIRST, kwargs={
                'server': self,
            })

            # Clean up any old WSX connections possibly registered for this server
            # which may be still lingering around, for instance, if the server was previously
            # shut down forcibly and did not have an opportunity to run self.cleanup_on_stop
            self.cleanup_wsx()

            # Startup services
            self.invoke_startup_services()

            # Local file-based configuration to apply
            try:
                self.apply_local_config()
            except Exception as e:
                logger.info('Exception while applying local config -> %s', e)

            # Subprocess-based connectors
            if self.has_posix_ipc:
                self.init_subprocess_connectors(subprocess_start_config)

            # SFTP channels are new in 3.1 and the directories may not exist
            if not os.path.exists(self.sftp_channel_dir):
                os.makedirs(self.sftp_channel_dir)

        # These are subsequent processes
        else:
            self.startup_callable_tool.invoke(SERVER_STARTUP.PHASE.IN_PROCESS_OTHER, kwargs={
                'server': self,
            })

            if self.has_posix_ipc:
                self._populate_connector_config(subprocess_start_config)

        # Stops the environment after N seconds
        if self.stop_after:
            _ = spawn_greenlet(self._stop_after_timeout)

        # Per-process IPC tasks
        self.init_ipc()

        if is_posix:
            connector_config_ipc = cast_('ConnectorConfigIPC', self.connector_config_ipc)

            if self.component_enabled['stats']:

                # Statistics
                events_config = cast_('anydict', connector_config_ipc.get_config(ZatoEventsIPC.ipc_config_name, as_dict=True))
                events_tcp_port = events_config['port']
                self._run_stats_client(events_tcp_port)

        # Invoke startup callables
        self.startup_callable_tool.invoke(SERVER_STARTUP.PHASE.AFTER_STARTED, kwargs={
            'server': self,
        })

        # The server is started so we can deploy what we were told to handle on startup,
        # assuming that we are the first process in this server.
        if self.is_starting_first:
            if self.deploy_auto_from:
                self.handle_enmasse_auto_from()

        logger.info('Started `%s@%s` (pid: %s)', server.name, server.cluster.name, self.pid)

# ################################################################################################################################

    def init_ipc(self):

        # Name of the environment key that points to our password ..
        _ipc_password_key = IPC.Credentials.Password_Key

        # .. which we can extract ..
        ipc_password = os.environ[_ipc_password_key]

        # .. and decrypt it ..
        ipc_password = self.decrypt(ipc_password)

        # .. this is the same for all processes ..
        bind_host = self.fs_server_config.main.ipc_host

        # .. this is set to a different value for each process ..
        bind_port = self.fs_server_config.main.ipc_port_start + self.process_idx

        # .. now, the IPC server can be started ..
        spawn_greenlet(self.ipc_api.start_server,
            self.pid,
            self.base_dir,
            bind_host=bind_host,
            bind_port=bind_port,
            username=IPC.Credentials.Username,
            password=ipc_password,
            callback_func=self.on_ipc_invoke_callback,
        )

        # .. we can now store the information about what IPC port to use with this PID.
        save_ipc_pid_port(self.cluster_name, self.name, self.pid, bind_port)

# ################################################################################################################################

    def _stop_after_timeout(self):

        # psutil
        import psutil

        now = datetime.utcnow()
        stop_at = now + timedelta(seconds=cast_('int', self.stop_after))

        while now < stop_at:
            logger.info(f'Now is {now}; waiting to stop until {stop_at}')
            now = datetime.utcnow()
            sleep(1)

        logger.info(f'Stopping Zato after {self.stop_after}s')

        # All the pids that we will stop
        to_stop = set()

        # Details of each process
        details = {}

        # Our own PID
        our_pid = os.getpid()

        # If a pid has any of these names in its name or command line,
        # we consider it a process that will be stopped.
        to_include = ['zato', 'gunicorn']

        for proc in list(psutil.process_iter(['pid', 'name'])):
            proc_name = proc.name()
            proc_cmd_line = ' '.join(proc.cmdline())
            for item in to_include:
                if (item in proc_name) or (item in proc_cmd_line):
                    to_stop.add(proc.pid)
                    details[proc.pid] = f'{proc_name}; {proc_cmd_line}'
                    logger.info('Found PID: %s; Name: %s; Cmd. line: %s', proc.pid, proc_name, proc_cmd_line)
                    break

        logger.info('Pids collected: %s; our PID: %s', to_stop, our_pid)

        # Remove our PID so that we do not stop ourselves too early
        to_stop.remove(our_pid)

        # Now, we can stop all the other processes
        for pid in to_stop:
            logger.info('Stopping PID %s (%s)', pid, details[pid])
            os.kill(pid, 9)

        # Finally, we can stop ourselves
        os.kill(our_pid, 9)

# ################################################################################################################################

    def _populate_connector_config(self, config:'SubprocessStartConfig') -> 'None':
        """ Called when we are not the first worker and, if any connector is enabled,
        we need to get its configuration through IPC and populate our own accordingly.
        """

        ipc_config_name_to_enabled = {
            IBMMQIPC.ipc_config_name: config.has_ibm_mq,
            SFTPIPC.ipc_config_name: config.has_sftp,
            ZatoEventsIPC.ipc_config_name: config.has_stats,
        }

        for ipc_config_name, is_enabled in ipc_config_name_to_enabled.items():
            if is_enabled:
                response = self.connector_config_ipc.get_config(ipc_config_name)
                if response:
                    response = cast_('str', response)
                    response = loads(response)
                    connector_suffix = ipc_config_name.replace('zato-', '').replace('-', '_')
                    connector_attr = 'connector_{}'.format(connector_suffix)
                    connector = getattr(self, connector_attr) # type: SubprocessIPC
                    connector.ipc_tcp_port = response['port']

# ################################################################################################################################

    def init_subprocess_connectors(self, config:'SubprocessStartConfig') -> 'None':
        """ Sets up subprocess-based connectors.
        """
        # Common
        ipc_tcp_start_port = int(self.fs_server_config.misc.get('ipc_tcp_start_port', 34567))

        # IBM MQ
        if config.has_ibm_mq:

            # Will block for a few seconds at most, until is_ok is returned
            # which indicates that a connector started or not.
            try:
                if self.connector_ibm_mq.start_ibm_mq_connector(ipc_tcp_start_port):
                    self.connector_ibm_mq.create_initial_wmq_definitions(self.worker_store.worker_config.definition_wmq)
                    self.connector_ibm_mq.create_initial_wmq_outconns(self.worker_store.worker_config.out_wmq)
                    self.connector_ibm_mq.create_initial_wmq_channels(self.worker_store.worker_config.channel_wmq)
            except Exception as e:
                logger.warning('Could not create initial IBM MQ objects, e:`%s`', e)
            else:
                self.subproc_current_state.is_ibm_mq_running = True

        # SFTP
        if config.has_sftp and self.connector_sftp.start_sftp_connector(ipc_tcp_start_port):
            self.connector_sftp.create_initial_sftp_outconns(self.worker_store.worker_config.out_sftp)
            self.subproc_current_state.is_sftp_running = True

        # Prepare Zato events configuration
        events_config = self.fs_server_config.get('events') or {} # type: dict

        # This is optional in server.conf ..
        fs_data_path = events_config.get('fs_data_path') or ''
        fs_data_path = fs_data_path or EventsDefault.fs_data_path

        # An absolute path = someone chose it explicitly, we leave it is as it is.
        if os.path.isabs(fs_data_path):
            pass

        # .. otherwise, build a full path.
        else:
            fs_data_path = os.path.join(self.work_dir, fs_data_path, self.events_dir, 'zato.events')
            fs_data_path = os.path.abspath(fs_data_path)
            fs_data_path = os.path.normpath(fs_data_path)

        extra_options_kwargs = {
            'fs_data_path': fs_data_path,
            'sync_threshold': EventsDefault.sync_threshold,
            'sync_interval': EventsDefault.sync_interval,
        }

        if self.component_enabled['stats']:
            _ = self.connector_events.start_zato_events_connector(ipc_tcp_start_port, extra_options_kwargs=extra_options_kwargs)

            # Wait until the events connector started - this will let other parts
            # of the server assume that it is always available.
            _ = wait_until_port_taken(self.connector_events.ipc_tcp_port, timeout=5)

# ################################################################################################################################

    def set_up_sso_rate_limiting(self) -> 'None':
        for item in self.odb.get_sso_user_rate_limiting_info():
            item = cast_('any_', item)
            self._create_sso_user_rate_limiting(item.user_id, True, item.rate_limit_def)

# ################################################################################################################################

    def _create_sso_user_rate_limiting(
        self,
        user_id:'str',
        is_active:'bool',
        rate_limit_def:'str',
    ) -> 'None':
        self.rate_limiting.create({
            'id': user_id,
            'type_': RATE_LIMIT.OBJECT_TYPE.SSO_USER,
            'name': user_id,
            'is_active': is_active,
            'parent_type': None,
            'parent_name': None,
        }, rate_limit_def, True)

# ################################################################################################################################

    def _get_sso_session(self) -> 'any_':
        """ Returns a session function suitable for SSO operations.
        """
        pool_name = self.sso_config.sql.name
        if pool_name:
            try:
                pool = self.worker_store.sql_pool_store.get(pool_name)
            except KeyError:
                pool = None
            if not pool:
                raise Exception('SSO pool `{}` not found or inactive'.format(pool_name))
            else:
                session_func = pool.session
        else:
            session_func = self.odb.session

        return session_func()

# ################################################################################################################################

    def configure_sso(self) -> 'None':
        if self.is_sso_enabled:
            self.sso_api.post_configure(self._get_sso_session, self.odb.is_sqlite)

# ################################################################################################################################

    def invoke_startup_services(self) -> 'None':
        stanza = 'startup_services_first_worker' if self.is_starting_first else 'startup_services_any_worker'
        _invoke_startup_services('Parallel', stanza,
            self.fs_server_config, self.repo_location, self.broker_client, None,
            is_sso_enabled=self.is_sso_enabled)

# ################################################################################################################################

    def _set_ide_password(self, ide_username:'str', ide_password:'str') -> 'None':
        service_name = 'zato.security.basic-auth.change-password'
        request = {
            'name': ide_username,
            'is_active': True,
            'type_': SEC_DEF_TYPE.BASIC_AUTH,
            'password1': ide_password,
            'password2': ide_password,
        }
        _ = self.invoke(service_name, request)

# ################################################################################################################################

    def apply_local_config(self) -> 'None':

        # A quickstart environment directory we are potentially in
        env_dir  = os.path.join(self.base_dir, '..')
        env_dir = os.path.abspath(env_dir)

        # A configuration file that may potentially exist
        env_json = os.path.join(env_dir, 'env.json')

        # Proceed only if the config file exists at all
        if os.path.exists(env_json):

            # Log what we are about to do
            self.logger.info('Found local config file -> %s', env_json)

            with open(env_json) as f:
                data = f.read()
                conf = loads(data)

                ide_username = conf.get('ide_username')
                ide_password = conf.get('ide_password')

                if ide_username and ide_password:
                    self.logger.info('Setting password for IDE user `%s`', ide_username)
                    self._set_ide_password(ide_username, ide_password)

# ################################################################################################################################

    def get_default_cache(self) -> 'CacheAPI':
        """ Returns the server's default cache.
        """
        return cast_('CacheAPI', self.worker_store.cache_api.default)

# ################################################################################################################################

    def get_cache(self, cache_type:'str', cache_name:'str') -> 'Cache':
        """ Returns a cache object of given type and name.
        """
        return self.worker_store.cache_api.get_cache(cache_type, cache_name)

# ################################################################################################################################

    def get_from_cache(self, cache_type:'str', cache_name:'str', key:'str') -> 'any_':
        """ Returns a value from input cache by key, or None if there is no such key.
        """
        return self.worker_store.cache_api.get_cache(cache_type, cache_name).get(key)

# ################################################################################################################################

    def set_in_cache(self, cache_type:'str', cache_name:'str', key:'str', value:'any_') -> 'any_':
        """ Sets a value in cache for input parameters.
        """
        return self.worker_store.cache_api.get_cache(cache_type, cache_name).set(key, value)

# ################################################################################################################################

    def invoke_all_pids(self, service:'str', request:'any_', timeout:'int'=5, *args:'any_', **kwargs:'any_') -> 'anydict':
        """ Invokes a given service in each of processes current server has.
        """
        # PID -> response from that process
        out = {}

        # Per-PID response
        response:'anydict'

        try:
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
                    pid_data = self.invoke_by_pid(service, request, pid, timeout=timeout, *args, **kwargs)
                    response['pid_data'] = pid_data
                except Exception:
                    e = format_exc()
                    response['error_info'] = e
                finally:
                    out[pid] = response
        except Exception:
            logger.warning('PID invocation error `%s`', format_exc())
        finally:
            return out

# ################################################################################################################################

    def invoke_by_pid(
        self,
        service,    # type: str
        request,    # type: any_
        target_pid, # type: int
        timeout=_ipc_timeout, # type: int
        **kwargs    # type:any_
    ) -> 'any_':
        """ Invokes a service in a worker process by the latter's PID.
        """
        return self.ipc_api.invoke_by_pid(service, request, self.cluster_name, self.name, target_pid, timeout)

# ################################################################################################################################

    def invoke(self, service:'str', request:'any_'=None, *args:'any_', **kwargs:'any_') -> 'any_':
        """ Invokes a service either in our own worker or, if PID is given on input, in another process of this server.
        """
        target_pid = kwargs.pop('pid', None)
        if target_pid and target_pid != self.pid:

            # This cannot be used by self.invoke_by_pid
            data_format = kwargs.pop('data_format', None)

            _, data = self.invoke_by_pid(service, request, target_pid, *args, **kwargs)
            return dumps(data) if data_format == DATA_FORMAT.JSON else data
        else:
            return self.worker_store.invoke(
                service, request,
                data_format=kwargs.pop('data_format', DATA_FORMAT.DICT),
                serialize=kwargs.pop('serialize', True),
                *args, **kwargs)

# ################################################################################################################################

    def on_ipc_invoke_callback(self, msg:'Bunch') -> 'anydict':

        service = msg['service']
        data    = msg['data']

        return self.invoke(service, data)

# ################################################################################################################################

    def publish(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self.worker_store.pubsub.publish(*args, **kwargs)

# ################################################################################################################################

    def invoke_async(self, service:'str', request:'any_', callback:'callable_', *args:'any_', **kwargs:'any_') -> 'any_':
        """ Invokes a service in background.
        """
        return self.worker_store.invoke(service, request, is_async=True, callback=callback, *args, **kwargs)

# ################################################################################################################################

    def publish_pickup(self, topic_name:'str', request:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        """ Publishes a pickedup file to a named topic.
        """
        _ = self.invoke('zato.pubsub.publish.publish', {
            'topic_name': topic_name,
            'endpoint_id': self.default_internal_pubsub_endpoint_id,
            'has_gd': False,
            'data': dumps({
                'meta': {
                    'pickup_ts_utc': request['ts_utc'],
                    'stanza': request.get('stanza'),
                    'full_path': request['full_path'],
                    'file_name': request['file_name'],
                },
                'data': {
                    'raw': request['raw_data'],
                }
            })
        })

# ################################################################################################################################

    def deliver_pubsub_msg(self, msg:'any_') -> 'None':
        """ A callback method invoked by pub/sub delivery tasks for each messages that is to be delivered.
        """
        subscription = self.worker_store.pubsub.subscriptions_by_sub_key[msg.sub_key]
        topic = self.worker_store.pubsub.topics[subscription.config['topic_id']] # type: ignore

        if topic.before_delivery_hook_service_invoker:
            response = topic.before_delivery_hook_service_invoker(topic, msg)
            if response['skip_msg']:
                raise SkipDelivery(msg.pub_msg_id)

        _ = self.invoke('zato.pubsub.delivery.deliver-message', {'msg':msg, 'subscription':subscription})

# ################################################################################################################################

    def encrypt(self, data:'any_', prefix:'str'=SECRETS.PREFIX) -> 'strnone':
        """ Returns data encrypted using server's CryptoManager.
        """
        if data:
            data = data.encode('utf8') if isinstance(data, str) else data
            encrypted = self.crypto_manager.encrypt(data)
            encrypted = encrypted.decode('utf8')
            return '{}{}'.format(prefix, encrypted)

# ################################################################################################################################

    def hash_secret(self, data:'str', name:'str'='zato.default') -> 'str':
        return self.crypto_manager.hash_secret(data, name)

# ################################################################################################################################

    def verify_hash(self, given:'str', expected:'str', name:'str'='zato.default') -> 'bool':
        return self.crypto_manager.verify_hash(given, expected, name)

# ################################################################################################################################

    def decrypt(self, data:'strbytes', _prefix:'str'=SECRETS.PREFIX, _marker:'str'=SECRETS.EncryptedMarker) -> 'str':
        """ Returns data decrypted using server's CryptoManager.
        """

        if isinstance(data, bytes):
            data = data.decode('utf8')

        if data and data.startswith((_prefix, _marker)):
            return self.decrypt_no_prefix(data.replace(_prefix, '', 1))
        else:
            return data # Already decrypted, return as is

# ################################################################################################################################

    def decrypt_no_prefix(self, data:'str') -> 'str':
        return self.crypto_manager.decrypt(data)

# ################################################################################################################################

    def incr_pub_counter(self):
        with self.pub_counter_lock:
            self.pub_counter += 1

# ################################################################################################################################

    def get_pub_counter(self):
        with self.pub_counter_lock:
            return self.pub_counter

# ################################################################################################################################

    def set_up_zato_kvdb(self) -> 'None':

        self.kvdb_dir = os.path.join(self.work_dir, 'kvdb', 'v10')

        if not os.path.exists(self.kvdb_dir):
            os.makedirs(self.kvdb_dir, exist_ok=True)

        self.load_zato_kvdb_data()

# ################################################################################################################################

    def set_up_oauth_store(self) -> 'None':

        # Create the base object ..
        self.oauth_store = OAuthStore(
            self.worker_store.oauth_get_by_id,
            OAuthTokenClient.obtain_from_config
        )

        # .. and populate it with initial data now.
        for item_id in self.worker_store.oauth_get_all_id_list():
            self.oauth_store.create(item_id)

# ################################################################################################################################

    def load_zato_kvdb_data(self) -> 'None':

        #
        # Only now do we know what the full paths for KVDB data are so we can set them accordingly here ..
        #

        self.slow_responses.set_data_path(
            os.path.join(self.kvdb_dir, CommonZatoKVDB.SlowResponsesPath),
        )

        self.usage_samples.set_data_path(
            os.path.join(self.kvdb_dir, CommonZatoKVDB.UsageSamplesPath),
        )

        self.current_usage.set_data_path(
            os.path.join(self.kvdb_dir, CommonZatoKVDB.CurrentUsagePath),
        )

        self.pub_sub_metadata.set_data_path(
            os.path.join(self.kvdb_dir, CommonZatoKVDB.PubSubMetadataPath),
        )

        #
        # .. and now we can load all the data.
        #

        self.slow_responses.load_data()
        self.usage_samples.load_data()
        self.current_usage.load_data()
        self.pub_sub_metadata.load_data()

# ################################################################################################################################

    def save_zato_main_proc_state(self) -> 'None':
        self.slow_responses.save_data()
        self.usage_samples.save_data()
        self.current_usage.save_data()
        self.pub_sub_metadata.save_data()

# ################################################################################################################################

    @staticmethod
    def post_fork(arbiter:'Arbiter', worker:'any_') -> 'None':
        """ A Gunicorn hook which initializes the worker.
        """

        # Each subprocess needs to have the random number generator re-seeded.
        random_seed()

        # This is our parallel server
        server = worker.app.zato_wsgi_app # type: ParallelServer

        server.startup_callable_tool.invoke(SERVER_STARTUP.PHASE.BEFORE_POST_FORK, kwargs={
            'arbiter': arbiter,
            'worker': worker,
        })

        worker.app.zato_wsgi_app.worker_pid = worker.pid
        ParallelServer.start_server(server, arbiter.zato_deployment_key)

# ################################################################################################################################

    @staticmethod
    def on_starting(arbiter:'Arbiter') -> 'None':
        """ A Gunicorn hook for setting the deployment key for this particular
        set of server processes. It needs to be added to the arbiter because
        we want for each worker to be (re-)started to see the same key.
        """
        arbiter.zato_deployment_key = '{}.{}'.format(datetime.utcnow().isoformat(), uuid4().hex)

# ################################################################################################################################

    @staticmethod
    def worker_exit(arbiter:'Arbiter', worker:'GeventWorker') -> 'None':

        # Invoke cleanup procedures
        app = worker.app.zato_wsgi_app # type: ParallelServer
        app.cleanup_on_stop()

# ################################################################################################################################

    @staticmethod
    def before_pid_kill(arbiter:'Arbiter', worker:'GeventWorker') -> 'None':
        pass

# ################################################################################################################################

    def cleanup_wsx(self, needs_pid:'bool'=False) -> 'None':
        """ Delete persistent information about WSX clients currently registered with the server.
        """
        wsx_service = 'zato.channel.web-socket.client.delete-by-server'

        if self.service_store.is_deployed(wsx_service):
            self.invoke(wsx_service, {'needs_pid': needs_pid})

# ################################################################################################################################

    def cleanup_on_stop(self) -> 'None':
        """ A shutdown cleanup procedure.
        """

        # Tell the ODB we've gone through a clean shutdown but only if this is
        # the main process going down (Arbiter) not one of Gunicorn workers.
        # We know it's the main process because its ODB's session has never
        # been initialized.
        if not self.odb.session_initialized:

            self.config.odb_data = self.get_config_odb_data(self)
            self.config.odb_data['fs_sql_config'] = self.fs_sql_config
            self.set_up_odb()

            self.odb.init_session(ZATO_ODB_POOL_NAME, self.config.odb_data, self.odb.pool, False)

            self.odb.server_up_down(self.odb.token, SERVER_UP_STATUS.CLEAN_DOWN)
            self.odb.close()

        # Per-worker cleanup
        else:

            # Store Zato KVDB data on disk
            self.save_zato_main_proc_state()

            # Set the flag to True only the first time we are called, otherwise simply return
            if self._is_process_closing:
                return
            else:
                self._is_process_closing = True

            # Close SQL pools
            self.sql_pool_store.cleanup_on_stop()

            # Close all POSIX IPC structures
            if self.has_posix_ipc:
                self.server_startup_ipc.close()
                self.connector_config_ipc.close()

            # WSX connections for this server cleanup
            self.cleanup_wsx(True)

            logger.info('Stopping server process (%s:%s) (%s)', self.name, self.pid, os.getpid())

            import sys
            sys.exit(3) # Same as arbiter's WORKER_BOOT_ERROR

# ################################################################################################################################

    def notify_new_package(self, package_id:'int') -> 'None':
        """ Publishes a message on the broker so all the servers (this one including
        can deploy a new package).
        """
        msg = {'action': HOT_DEPLOY.CREATE_SERVICE.value, 'package_id': package_id} # type: ignore
        self.broker_client.publish(msg)

# ################################################################################################################################
# ################################################################################################################################

# Shortcut API methods

    def api_service_store_get_service_name_by_id(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self.service_store.get_service_name_by_id(*args, **kwargs)

    def api_worker_store_basic_auth_get_by_id(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self.worker_store.basic_auth_get_by_id(*args, **kwargs)

    def api_worker_store_reconnect_generic(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self.worker_store.reconnect_generic(*args, **kwargs)

    def is_active_outconn_wsx(self, conn_id:'str') -> 'bool':
        is_active = self.worker_store.is_active_generic_conn(conn_id)
        return is_active

# ################################################################################################################################
# ################################################################################################################################

servernone = optional[ParallelServer]

# ################################################################################################################################
# ################################################################################################################################
