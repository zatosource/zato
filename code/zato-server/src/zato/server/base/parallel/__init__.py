# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from copy import deepcopy
from datetime import timedelta
from json import loads
from logging import INFO, WARN
from pathlib import Path
from platform import system as platform_system
from random import seed as random_seed
from traceback import format_exc
from uuid import uuid4

# Bunch
from bunch import bunchify

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock

# Zato
from zato.broker import BrokerMessageReceiver
from zato.bunch import Bunch
from zato.common.api import API_Key, DATA_FORMAT, EnvFile, EnvVariable, HotDeploy, SERVER_STARTUP, \
    SEC_DEF_TYPE, ZATO_ODB_POOL_NAME
from zato.common.audit import audit_pii
from zato.common.broker_message import HOT_DEPLOY, PUBSUB
from zato.common.const import SECRETS
from zato.common.json_internal import loads
from zato.common.typing_ import cast_, intnone, optional
from zato.common.util.api import absolutize, as_bool, get_config_from_file, get_user_config_name, \
    fs_safe_name, invoke_startup_services as _invoke_startup_services, make_list_from_string_list, new_cid_server, \
    spawn_greenlet, StaticConfig, utcnow
from zato.common.util.env import populate_environment_from_file
from zato.common.util.file_transfer import path_string_list_to_list
from zato.common.util.file_system import get_python_files
from zato.common.util.hot_deploy_ import extract_pickup_from_items
from zato.common.util.json_ import BasicParser
from zato.common.util.platform_ import is_posix
from zato.common.util.time_ import TimeUtil
from zato.server.base.parallel.config import ConfigLoader
from zato.server.base.parallel.http import HTTPHandler
from zato.server.config import ConfigStore
from zato_server_core import ConfigStore as RustConfigStore

# ################################################################################################################################
# ################################################################################################################################

if 0:

    from bunch import Bunch as bunch_
    from ddtrace.trace import tracer as dd_tracer
    from ddtrace._trace.tracer import Tracer as DatadogTracer
    from kombu.transport.pyamqp import Message as KombuMessage
    from opentelemetry.trace import Tracer as OTLPTracer
    from zato.broker.api import BrokerCoreAPI
    from zato.common.bearer_token import BearerTokenManager
    from zato.common.crypto.api import ServerCryptoManager
    from zato.common.facade import SecurityFacade
    from zato.common.log_streaming import LogStreamingManager
    from zato.common.marshal_.api import MarshalAPI
    from zato.common.odb.api import ODBManager, PoolStore
    from zato.common.pubsub.backend import PubSubBackend
    from zato.common.pubsub.matcher import PatternMatcher
    from zato.common.pubsub.subscriptions_store import SubscriptionsStore
    from zato.common.rules.api import RulesManager
    from zato.common.typing_ import any_, anydict, anylist, anyset, callable_, intset, strdict, strbytes, \
        strlist, strorlistnone, strnone, strorlist, strset
    from zato.distlock import LockManager
    from zato.server.base.worker import WorkerStore
    from zato.server.connection.cache import Cache, CacheAPI
    from zato.server.connection.server.rpc.api import ConfigCtx as _ServerRPC_ConfigCtx, ServerRPC
    from zato.server.groups.base import GroupsManager
    from zato.server.groups.ctx import SecurityGroupsCtxBuilder
    from zato.server.service.store import ServiceStore
    from zato.server.startup_callable import StartupCallableTool

    bunch_ = bunch_
    KombuMessage = KombuMessage
    random_seed = random_seed
    ServerCryptoManager = ServerCryptoManager
    ServiceStore = ServiceStore
    SIOServerConfig = SIOServerConfig # type: ignore
    StartupCallableTool = StartupCallableTool

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
kvdb_logger = logging.getLogger('zato_broker')

# ################################################################################################################################
# ################################################################################################################################

megabyte = 10 ** 6

# ################################################################################################################################
# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

# ################################################################################################################################
# ################################################################################################################################

class ParallelServer(BrokerMessageReceiver, ConfigLoader, HTTPHandler):
    """ Main server process.
    """
    odb: 'ODBManager'  # ServiceStore dependency -- removed in Phase 6
    config_store: 'RustConfigStore'
    config: 'ConfigStore'
    crypto_manager: 'ServerCryptoManager'
    sql_pool_store: 'PoolStore'
    on_http_request: 'any_'

    worker_store: 'WorkerStore'
    service_store: 'ServiceStore'

    rpc: 'ServerRPC'
    broker_client: 'BrokerCoreAPI'
    zato_lock_manager: 'LockManager'
    startup_callable_tool: 'StartupCallableTool'
    bearer_token_manager: 'BearerTokenManager'
    security_facade: 'SecurityFacade'

    stop_after: 'intnone'
    deploy_auto_from: 'str' = ''

    datadog_tracer: 'DatadogTracer'
    otlp_tracer: 'OTLPTracer'

    is_datadog_enabled: 'bool'
    is_grafana_cloud_enabled: 'bool'

    env_name: 'str'

    groups_manager: 'GroupsManager'
    security_groups_ctx_builder: 'SecurityGroupsCtxBuilder'

    pubsub_backend: 'PubSubBackend'
    pubsub_pattern_matcher: 'PatternMatcher'
    pubsub_subscriptions: 'SubscriptionsStore'

    work_dir:'str'

    def __init__(self) -> 'None':
        self.logger = logger
        self.host = ''
        self.port = -1
        self.use_tls = False
        self.is_starting_first = '<not-set>'
        self.repo_location = ''
        self.user_conf_location:'strlist' = []
        self.user_conf_location_extra:'strset' = set()
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
        self.hot_deploy_config = Bunch()
        self.fs_server_config = None # type: any_
        self.fs_sql_config = Bunch()
        self.pickup_config = Bunch()
        self.logging_config = Bunch()
        self.logging_conf_path = 'server-'
        self.connector_server_grace_time = None
        self.id = -1
        self.name = ''
        self.process_cid = new_cid_server()
        self.worker_id = ''
        self.worker_pid = -1
        self.cluster_id = -1
        self.cluster_name = ''
        self.startup_jobs = {}
        self.deployment_lock_expires = -1
        self.deployment_lock_timeout = -1
        self.deployment_key = ''
        self.has_gevent = True
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
        self.is_first_worker = False
        self.process_idx = -1
        self.shmem_size = -1.0
        self.audit_pii = audit_pii
        self.has_fg = False
        self.env_file = ''
        self.env_variables_from_files:'strlist' = []
        self._hash_secret_method = ''
        self._hash_secret_rounds = -1
        self._hash_secret_salt_size = -1
        self.platform_system = platform_system().lower()
        self.user_config = Bunch()
        self.stderr_path = ''
        from zato.common.marshal_.api import MarshalAPI
        self.marshal_api = MarshalAPI()
        self.env_manager = None # This is taken from util/zato_environment.py:EnvironmentManager
        self.enforce_service_invokes = False
        self.json_parser = BasicParser()
        self.api_key_header = 'Zato-Default-Not-Set-API-Key-Header'
        self.api_key_header_http = 'HTTP_' + self.api_key_header.upper().replace('-', '_')
        self.needs_x_zato_cid = False

        # Our arbiter may potentially call the cleanup procedure multiple times
        # and this will be set to True the first time around.
        self._is_process_closing = False

        # Internal caches - not to be used by user services
        self.internal_cache_patterns = {}
        self.internal_cache_lock_patterns = RLock()

        # Gateway services allowed per channel (by channel ID)
        self.gateway_services_allowed = {}
        self.gateway_services_allowed_lock = RLock()

        # Allows users store arbitrary data across service invocations
        self.user_ctx = Bunch()
        self.user_ctx_lock = RLock()

        # HTTP methods allowed as a Python list
        self.http_methods_allowed = []

        # As above, but as a regular expression pattern
        self.http_methods_allowed_re = ''

        # A list of all the pub/sub hook services that will be invoked (alphabetically)
        # for any pub/sub message before it's delivered.
        self.pubsub_hooks:'strlist' = []

        self.access_logger = logging.getLogger('zato_access_log')
        self.access_logger_log = self.access_logger._log
        self.needs_access_log = self.access_logger.isEnabledFor(INFO)
        self.needs_all_access_log = True
        self.access_log_ignore = set()
        self.rest_log_ignore   = set()
        self.is_enabled_for_warn = logging.getLogger('zato').isEnabledFor(WARN)
        self.is_admin_enabled_for_info = logging.getLogger('zato_admin').isEnabledFor(INFO)

        # Rule engine
        from zato.common.rules.api import RulesManager
        self.rules = RulesManager()

        # The Rust-backed config store
        self.config_store = RustConfigStore()

        # The main config store (Python side, populated from Rust store)
        self.config = ConfigStore()

        # Log streaming manager
        from zato.common.log_streaming import LogStreamingManager
        self.log_streaming_manager = LogStreamingManager()

# ################################################################################################################################

    def maybe_on_first_worker(self, server:'ParallelServer') -> 'anyset':
        """ This method will execute code with a distibuted lock held. We need a lock because we can have multiple worker
        processes fighting over the right to redeploy services. The first worker to obtain the lock will actually perform
        the redeployment and set a flag meaning that for this particular deployment key (and remember that each server restart
        means a new deployment key) the services have been already deployed. Further workers will check that the flag exists
        and will skip the deployment altogether.
        """
        def import_initial_services_jobs() -> 'anyset':

            # Zato
            from zato.common.util.api import find_internal_modules
            from zato.server.service import internal

            locally_deployed = []

            manifest_path = self.service_store._find_manifest(self.base_dir)

            if manifest_path:
                logger.info('Using internal services manifest: %s', manifest_path)
                internal_deployed = self.service_store._import_from_manifest(manifest_path)
            elif getattr(self, 'enforce_manifest', False):
                logger.info('Building internal services manifest (enforce-manifest mode)')
                deploy_internal = find_internal_modules(internal)
                if not deploy_internal:
                    raise Exception('No internal modules found to be imported')
                internal_deployed = self.service_store._build_manifest(list(deploy_internal), self.base_dir)
            else:
                deploy_internal = find_internal_modules(internal)
                internal_service_modules = []
                if deploy_internal:
                    for module_name in deploy_internal:
                        internal_service_modules.append(module_name)
                else:
                    raise Exception('No internal modules found to be imported')
                internal_deployed = self.service_store.import_internal_services(
                    internal_service_modules, self.base_dir, self.sync_internal)

            locally_deployed.extend(internal_deployed)

            logger.info('Deploying user-defined services (%s) (%s)', self.name, self.service_sources)

            user_defined_deployed:'anylist' = self.service_store.import_services_from_anywhere(
                self.service_modules + self.service_sources, self.base_dir).to_process

            locally_deployed.extend(user_defined_deployed)
            len_user_defined_deployed = len(user_defined_deployed)

            suffix = '' if len_user_defined_deployed == 1 else 's'

            logger.info('Deployed %d user-defined service%s (%s)', len_user_defined_deployed, suffix, self.name)

            if as_bool(os.environ.get('Zato_Log_User_Services_Deployed', False)):
                for item in sorted(elem.name for elem in user_defined_deployed):
                    logger.info('Deployed user service: %s', item)

            return set(locally_deployed)

        # Deploy services
        locally_deployed = import_initial_services_jobs()

        return locally_deployed

# ################################################################################################################################

    def get_full_name(self) -> 'str':
        """ Returns this server's full name in the form of server@cluster.
        """
        return '{}@{}'.format(self.name, self.cluster_name)

# ################################################################################################################################

    def add_pickup_conf_from_env(self) -> 'None':

        # These exact names may exist in the environment ..
        name_list = ['Zato_Project_Root', 'Zato_Hot_Deploy_Dir', 'ZATO_HOT_DEPLOY_DIR']

        # .. same for these prefixes ..
        prefix_list = ['Zato_Project_Root_', 'Zato_Hot_Deploy_Dir_']

        # .. go through the specific names and add any matching ..
        for name in name_list:
            if path := os.environ.get(name, ''):
                self.add_pickup_conf_from_local_path(path, name)

        # .. go through the list of prefixes and add any matching too.
        for prefix in prefix_list:
            for name, path in os.environ.items():
                if name.startswith(prefix):
                    self.add_pickup_conf_from_local_path(path, name)

# ################################################################################################################################

    def add_pickup_conf_from_auto_deploy(self) -> 'None':

        # Look up Python hot-deployment directories ..
        path = os.path.join(self.deploy_auto_from, 'code')

        # .. and make it possible to deploy from them.
        self.add_pickup_conf_from_local_path(path, 'AutoDeploy')

# ################################################################################################################################

    def add_pickup_conf_from_local_path(self, paths:'str', source:'str', path_patterns:'strorlistnone'=None) -> 'None':

        # Bunchz
        from bunch import bunchify

        # Local variables
        path_patterns = path_patterns or HotDeploy.Default_Patterns
        path_patterns = path_patterns if isinstance(path_patterns, list) else [path_patterns] # type: ignore

        # We have hot-deployment configuration to process ..
        if paths:

            # .. log what we are about to do ..
            msg = f'Processing hot-deployment configuration paths `{paths!r}` (source -> {source})'
            logger.info(msg)

            # .. support multiple entries ..
            paths = make_list_from_string_list(paths, ':') # type: ignore

            # .. add  the actual configuration ..
            for path in paths:

                # .. make sure the path is actually given on input, e.g. it is not None or '' ..
                if not path:
                    msg = f'Ignoring empty hot-deployment configuration path `{path}` (source -> {source})'
                    logger.info(msg)
                    continue

                # .. log what we are about to do ..
                msg = f'Adding hot-deployment configuration from `{path}` (source -> {source})'
                logger.info(msg)

                # .. stay on the safe side because, here, we do not know where it will be used ..
                _fs_safe_name = fs_safe_name(path)

                # .. use this prefix to indicate that it is a directory to hot-deploy from ..
                key_name = '{}.{}'.format(HotDeploy.UserPrefix, _fs_safe_name)

                # .. store the configuration for later use now ..
                pickup_from = {
                    'pickup_from': path
                }
                self.pickup_config[key_name] = bunchify(pickup_from)

                # .. go through all the path patterns that point to user configuration (including enmasse) ..
                for path_pattern in path_patterns:

                    # .. get a list of matching paths ..
                    user_conf_paths = Path(path).rglob(path_pattern)
                    user_conf_paths = list(user_conf_paths)

                    # .. go through all the paths that matched ..
                    for user_conf_path in user_conf_paths:

                        # .. and add each of them to hot-deployment.
                        self._add_user_conf_from_path(str(user_conf_path), source)

# ################################################################################################################################

    def add_user_conf_from_env(self) -> 'None':

        # Local variables
        env_keys = ['Zato_User_Conf_Dir', 'ZATO_USER_CONF_DIR']

        # Look up user-defined configuration directories ..
        paths = os.environ.get('ZATO_USER_CONF_DIR', '')

        # .. try the other name too ..
        if not paths:
            paths = os.environ.get('Zato_User_Conf_Dir', '')

        # Go through all the possible environment keys ..
        for key in env_keys:

            # .. if we have user-config details to process ..
            if paths := os.environ.get(key, ''):

                # .. support multiple entries ..
                paths = paths.split(':')
                paths = [elem.strip() for elem in paths]

                # .. and the actual configuration.
                for path in paths:
                    source = f'env. variable found -> {key}'
                    self._add_user_conf_from_path(path, source)

# ################################################################################################################################

    def _add_user_conf_from_path(self, path:'str', source:'str') -> 'None':

        # Bunch
        from bunch import bunchify

        # Ignore files other than the below ones
        suffixes = ['ini', 'conf', 'yaml', 'yml']
        patterns = ['*.' + elem for elem in suffixes]
        patterns_str = ', '.join(patterns)

        # Log what we are about to do ..
        msg = f'Adding user-config from `{path}` ({source})'
        logger.info(msg)

        # .. look up files inside the directory and add the path to each
        # .. to a list of what should be loaded on startup ..
        if os.path.exists(path) and os.path.isdir(path):
            file_item_list = os.listdir(path)
            for file_item in file_item_list:
                for suffix in suffixes:
                    if file_item.endswith(suffix):
                        self.user_conf_location_extra.add(path)

        # .. stay on the safe side because, here, we do not know where it will be used ..
        _fs_safe_name = fs_safe_name(path)

        # .. use this prefix to indicate that it is a directory to deploy user configuration from  ..
        key_name = '{}.{}'.format(HotDeploy.UserConfPrefix, _fs_safe_name)

        # .. use a specific service if it is an enmasse file ..
        if 'enmasse' in path:
            service = 'zato.pickup.update-enmasse'

        # .. or default to the one for user config if it is not ..
        else:
            service= 'zato.pickup.update-user-conf'

        # .. and store the configuration for later use now.
        pickup_from = {
            'pickup_from': path,
            'patterns': patterns_str,
            'parse_on_pickup': False,
            'delete_after_pickup': False,
            'services': service,
        }

        self.pickup_config[key_name] = bunchify(pickup_from)

# ################################################################################################################################

    def add_pickup_conf_from_env_variables(self) -> 'None':

        # Code hot-deployment
        self.add_pickup_conf_from_env()

        # User configuration
        self.add_user_conf_from_env()

# ################################################################################################################################

    def add_pickup_conf_for_env_file(self) -> 'None':

        # If we have a file with environment variables, we want to listed to the changes to its contents ..
        if self.env_file:

            # .. but we need to have an absolute path ..
            if not os.path.isabs(self.env_file):
                logger.info(f'Env. file is not an absolute path, hot-deployment will not be enabled -> `{self.env_file}')
                return

            else:
                # .. extract the directory the file is in ..
                parent_dir = os.path.dirname(self.env_file)
                parent_dir = Path(parent_dir)
                parent_dir_name = parent_dir.name

                # .. and extract its own parent as well because this is needed in the call below ..
                grand_parent_dir = os.path.dirname(parent_dir)

                # .. and add it to hot-deployment.
                self.add_pickup_conf_from_local_path(grand_parent_dir, 'EnvFile', parent_dir_name)

# ################################################################################################################################

    def update_environment_variables_from_file(self, file_path:'str') -> 'None':

        # Prepare information about the variables that are to be deleted ..
        to_delete = deepcopy(self.env_variables_from_files)

        # .. load new variables, deleting the old ones along the way ..
        new_variables = populate_environment_from_file(file_path, to_delete=to_delete, use_print=False)

        # .. and populate the list for later use.
        self.env_variables_from_files = new_variables

# ################################################################################################################################

    def _after_init_common(self, server:'ParallelServer') -> 'anyset':
        """ Initializes parts of the server that don't depend on whether the server's been allowed to join the cluster or not.
        """

        # Static config files
        self.static_config = StaticConfig(self.static_dir)

        # Whether to add X-Zato-CID to outgoing responses
        needs_x_zato_cid = self.fs_server_config.misc.get('needs_x_zato_cid') or False
        self.needs_x_zato_cid = needs_x_zato_cid

        # Look up pickup configuration among environment variables
        # and add anything found to self.pickup_config.
        self.add_pickup_conf_from_env_variables()

        # Look up pickup configuration based on what should be auto-deployed on startup.
        if self.deploy_auto_from:
            self.add_pickup_conf_from_auto_deploy()

        # If we have a file with environment variables on input,
        # pick up changes to this file too.
        if self.env_file:
            self.add_pickup_conf_for_env_file()

        if _needs_details:
            logger.info('*' * 60)
            logger.info('Checking pickup self.base_dir `%s`', self.base_dir)
            logger.info('Checking pickup self.pickup_config `%s`', self.pickup_config)
            logger.info('Checking pickup Source_Directory `%s`', HotDeploy.Source_Directory)

        # Service sources from user-defined hot-deployment configuration ..
        for pickup_from in extract_pickup_from_items(self.base_dir, self.pickup_config, HotDeploy.Source_Directory):

            # .. log what we are about to do ..
            if isinstance(pickup_from, list):
                for project in pickup_from:
                    for item in project.pickup_from_path:
                        if _needs_details:
                            logger.info('Adding hot-deployment directory `%s` (HotDeploy.UserPrefix->Project)', item)
            else:
                if _needs_details:
                    logger.info('Adding hot-deployment directory `%s` (HotDeploy.UserPrefix->Path)', pickup_from)

            # .. and do append it for later use ..
            self.service_sources.append(pickup_from)

        # Read all the user config files that are already available on startup
        self.read_user_config()

        locally_deployed = self.maybe_on_first_worker(server)

        return locally_deployed

# ################################################################################################################################

    def _read_user_config_from_directory(self, dir_name:'str') -> 'None':

        # We assume that it will be always one of these file name suffixes,
        # note that we are not reading enmasse (.yaml and .yml) files here,
        # even though directories with enmasse files may be among what we have in self.user_conf_location_extra.
        suffixes_supported = ('.ini', '.conf', '.zrules')

        # User-config from ./config/repo/user-config
        for file_name in os.listdir(dir_name):

            # Reusable
            file_name = file_name.lower()

            # Reject files that actually contain environment variables
            if file_name == EnvFile.Default:
                continue

            # Reject files with suffixes that we do not recognize
            if not file_name.endswith(suffixes_supported):
                continue

            # Load rules ..
            if file_name.endswith('.zrules'):
                _ = self.rules.load_rules_from_file(os.path.join(dir_name, file_name))
                logger.info('Read rules from `%s` (dir:%s)', file_name, dir_name)

            # .. load a config file ..
            else:

                user_conf_full_path = os.path.join(dir_name, file_name)
                user_config_name = get_user_config_name(file_name)
                conf = get_config_from_file(user_conf_full_path, file_name)

                # Not used at all in this type of configuration
                _:'any_' = conf.pop('user_config_items', None)

                self.user_config[user_config_name] = conf

                logger.info('Read user config `%s` from `%s` (dir:%s)', user_config_name, file_name, dir_name)

# ################################################################################################################################

    def read_user_config(self):

        # Type hints
        dir_name:'str'

        # Reads config files from the default directory
        for dir_name in self.user_conf_location:
            self._read_user_config_from_directory(dir_name)

        # Reads config files from extra directories pointed to by ZATO_USER_CONF_DIR
        for dir_name in self.user_conf_location_extra:
            self._read_user_config_from_directory(dir_name)

# ################################################################################################################################

    def set_up_user_config_location(self) -> 'strlist':

        user_conf_location:'str' = self.pickup_config.get('user_conf', {}).get('pickup_from', '')
        return path_string_list_to_list(self.base_dir, user_conf_location)

# ################################################################################################################################

    def build_server_rpc(self) -> 'ServerRPC':

        from zato.server.connection.server.rpc.api import ConfigCtx as _ServerRPC_ConfigCtx, ServerRPC

        # A combination of runtime configuration (no ODB needed)
        config_ctx = _ServerRPC_ConfigCtx(None, self)

        # A publicly available RPC client
        return ServerRPC(config_ctx)

# ################################################################################################################################

    def handle_enmasse_auto_from(self) -> 'None':

        enmasse_dir = os.path.join(self.deploy_auto_from, 'enmasse')

        if not os.path.isdir(enmasse_dir):
            return

        for file_name in sorted(os.listdir(enmasse_dir)):
            if file_name.endswith(('.yaml', '.yml')):
                file_path = os.path.join(enmasse_dir, file_name)
                logger.info('Loading enmasse auto-deploy YAML: %s', file_path)
                self.config_store.load_yaml(file_path)

        self.reload_config()

# ################################################################################################################################

    def log_environment_details(self):

        # First, we need to have the correct variable set ..
        if log_details := os.environ.get(EnvVariable.Log_Env_Details) or True:

            # .. now, make sure it is set to True ..
            if as_bool(log_details):

                # .. now, we need to have the correct file available ..
                path = ['~', 'env', 'details', 'all-zato-env-details.txt']
                path = os.path.join(*path)
                path = os.path.expanduser(path)

                if os.path.exists(path):
                    with open(path) as f:
                        data = f.read()
                    self.logger.info(f'Environment details:\n{data}')

# ################################################################################################################################

    @staticmethod
    def start_server(parallel_server:'ParallelServer', zato_deployment_key:'str'='') -> 'None':

        # Deferred imports - loaded here to keep module-level import time low
        from zato.broker.api import BrokerCoreAPI
        from zato.common.bearer_token import BearerTokenManager
        from zato.common.facade import SecurityFacade
        from zato.common.pubsub.consumer import start_internal_consumer
        from zato.common.pubsub.matcher import PatternMatcher
        from zato.common.pubsub.backend import PubSubBackend
        from zato.common.pubsub.subscriptions_store import SubscriptionsStore
        from zato.distlock import LockManager
        from zato.server.base.worker import WorkerStore
        from zato.server.groups.base import GroupsManager
        from zato.server.groups.ctx import SecurityGroupsCtxBuilder
        from zato_broker_core import log_admin_info

        # Easier to type
        self = parallel_server

        # This cannot be done in __init__ because each sub-process obviously has its own PID
        self.pid = os.getpid()

        # This also cannot be done in __init__ which doesn't have this variable yet
        self.process_idx = int(os.environ['ZATO_SERVER_WORKER_IDX'])
        self.is_first_worker = self.process_idx == 0

        # Monitoring
        logger.info('Monitoring setup - datadog_enabled:%s grafana_cloud_enabled:%s',
            self.is_datadog_enabled, self.is_grafana_cloud_enabled)

        if self.is_datadog_enabled:
            self._set_up_datadog()

        if self.is_grafana_cloud_enabled:
            self._set_up_grafana_cloud()

        # Used later on
        use_tls = as_bool(self.fs_server_config.crypto.use_tls)

        # This changed in 3.2 so we need to take both into account
        self.work_dir = self.fs_server_config.main.get('work_dir') or self.fs_server_config.hot_deploy.get('work_dir')
        self.work_dir = os.path.normpath(os.path.join(self.repo_location, self.work_dir))

        for name in 'v1', 'v2':
            full_path = os.path.join(self.work_dir, 'events', name)
            if not os.path.exists(full_path):
                os.makedirs(full_path, mode=0o770, exist_ok=True)

        # Will be None if we are not running in background.
        if not zato_deployment_key:
            zato_deployment_key = '{}.{}'.format(utcnow().isoformat(), uuid4().hex)

        # Each time a server starts a new deployment key is generated to uniquely
        # identify this particular time the server is running.
        self.deployment_key = zato_deployment_key

        # Server identity from server.conf [misc] section
        self.name = self.fs_server_config.misc.initial_server_name
        self.cluster_name = self.fs_server_config.misc.initial_cluster_name
        self.id = 1
        self.cluster_id = 1
        self.worker_id = '{}.{}.{}.{}'.format(self.cluster_id, self.id, self.worker_pid, self.process_cid)

        # File-based lock manager (no ODB needed)
        self.zato_lock_manager = LockManager('fcntl', 'zato', None)

        with self.zato_lock_manager(uuid4().hex):
            pass

        # ODB pool -- still needed by ServiceStore for service deployment tracking (Phase 6 removes this).
        # Feed odb_data from server.conf into the Python ConfigStore so WorkerStore.init_sql can connect.
        odb_data = Bunch()
        odb_data.db_name = self.fs_server_config.odb.db_name
        odb_data.extra = self.fs_server_config.odb.extra
        odb_data.engine = self.fs_server_config.odb.engine
        odb_data.token = self.fs_server_config.main.token
        odb_data.is_odb = True
        odb_data.is_active = True

        if odb_data.engine != 'sqlite':
            odb_data.password = self.fs_server_config.odb.password
            odb_data.host = self.fs_server_config.odb.host
            odb_data.port = self.fs_server_config.odb.port
            odb_data.pool_size = self.fs_server_config.odb.pool_size
            odb_data.username = self.fs_server_config.odb.username

        self.config.odb_data = odb_data
        self.config.odb_data['fs_sql_config'] = self.fs_sql_config
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.config.odb_data
        self.odb.pool = self.sql_pool_store[ZATO_ODB_POOL_NAME].pool
        self.odb.token = self.config.odb_data.token if isinstance(self.config.odb_data.token, str) \
            else self.config.odb_data.token.decode('utf8')
        self.odb.decrypt_func = self.decrypt



        # Load enmasse YAML into the Rust ConfigStore
        self.load_enmasse_yaml()

        # Create a server-like object for compatibility
        server = Bunch()
        server.id = self.id
        server.name = self.name
        server.token = self.fs_server_config.main.token
        server.cluster = Bunch()
        server.cluster.id = self.cluster_id
        server.cluster.name = self.cluster_name
        server.cluster_id = self.cluster_id



        logger.info(
            'Preferred address of `%s@%s` (pid: %s) is `http%s://%s:%s`',
            self.name, self.cluster_name, self.pid, 's' if use_tls else '', self.preferred_address, self.port)

        # Configure which HTTP methods can be invoked via REST or SOAP channels
        methods_allowed = self.fs_server_config.http.methods_allowed
        methods_allowed:'strorlist' = methods_allowed if isinstance(methods_allowed, list) else [methods_allowed]
        self.http_methods_allowed.extend(methods_allowed)

        # As above, as a regular expression to be used in pattern matching
        http_methods_allowed_re = '|'.join(self.http_methods_allowed)
        self.http_methods_allowed_re = '({})'.format(http_methods_allowed_re)



        # Reads in all configuration from the Rust ConfigStore
        self.worker_store = WorkerStore(self.config, self)

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

        # API keys configuration
        self.set_up_api_key_config()

        # Some parts of the worker store's configuration are required during the deployment of services
        # which is why we are doing it here, before worker_store.init() is called.
        self.worker_store.early_init()

        locally_deployed = self._after_init_common(server) # type: ignore

        # Broker construction - start it in a greenlet so the Rust-heavy __init__
        # (fs_init, fs_start_http_server) overlaps with the Python setup below.
        def _init_broker():
            self.broker_client = BrokerCoreAPI(server=self)
            self.broker_client.ping_connection()
            self.broker_client.delete_queue(self.process_cid, 'server')
            self.broker_client.create_internal_queue('server')
            self.broker_client.start_consumer()

        broker_greenlet = spawn(_init_broker)

        # Build objects responsible for groups
        self.groups_manager = GroupsManager(self)
        self.security_groups_ctx_builder = SecurityGroupsCtxBuilder(self)

        # Initializes worker store, including connectors
        self.worker_store.init()

        # Security facade wrapper
        self.security_facade = SecurityFacade(self)

        # Bearer tokens (OAuth)
        self.bearer_token_manager = BearerTokenManager(self)

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

                value = as_bool(self.fs_server_config.hot_deploy.get(_name, True))
                self.hot_deploy_config[name] = value
            else:
                self.hot_deploy_config[name] = os.path.normpath(os.path.join(
                    self.hot_deploy_config.work_dir, self.fs_server_config.hot_deploy[name]))

        # Pub/sub objects that don't need the broker client yet
        self.pubsub_pattern_matcher = PatternMatcher()
        self.pubsub_subscriptions = SubscriptionsStore()
        self._load_pubsub_permissions()

        broker_greenlet.get()

        # Configure internal pub/sub
        _ = spawn_greenlet(
            start_internal_consumer,
            'zato.server',
            'server',
            'zato-server',
            self.on_pubsub_message
        )

        # Initialize the pub/sub backend using the broker client
        self.pubsub_backend = PubSubBackend(self.broker_client)

        # Register auth callbacks so the broker's Rust HTTP server
        # can validate credentials and permissions through the Zato security layer.
        self.broker_client.set_auth_callbacks(
            self._check_broker_credentials,
            self._check_broker_permission,
        )

        # Pre-load all Basic Auth credentials into Rust for GIL-free checking.
        self._push_broker_credentials()

        # Let the worker know the broker client is ready
        self.worker_store.set_broker_client(self.broker_client)
        self.worker_store.after_broker_client_set()

        self._after_init_accepted(locally_deployed)

        self.startup_callable_tool.invoke(SERVER_STARTUP.PHASE.IN_PROCESS_FIRST, kwargs={
            'server': self,
        })

        # Startup services
        self.invoke_startup_services()

        # Local file-based configuration to apply
        try:
            self.apply_local_config()
        except Exception as e:
            logger.info('Exception while applying local config -> %s', e)

        # Stops the environment after N seconds
        if self.stop_after:
            _ = spawn_greenlet(self._stop_after_timeout)

        # Invoke startup callables
        self.startup_callable_tool.invoke(SERVER_STARTUP.PHASE.AFTER_STARTED, kwargs={
            'server': self,
        })

        # Touch all the hot-directory files to trigger their deployment
        py_files = get_python_files(self.hot_deploy_config.pickup_dir)
        for item in py_files:
            _ = self.invoke('zato.hot-deploy.create', {
                'payload': item['data'],
                'payload_name': item['full_path']
            })

        # The server is started so we can deploy what we were told to handle on startup.
        if self.deploy_auto_from:
            self.handle_enmasse_auto_from()

        # Start the Rust scheduler thread (in-process, same pattern as the broker)
        self._start_scheduler()

        # Optionally, if we appear to be a Docker quickstart environment, log all details about the environment.
        self.log_environment_details()

        logger.info('Started `%s@%s` (pid: %s)', server.name, server.cluster.name, self.pid)

# ################################################################################################################################

    def _pre_initialize(self) -> 'None':
        pass

# ################################################################################################################################

    def _start_scheduler(self) -> 'None':
        """ Start the Rust scheduler thread inside this server process.
        """
        from json import loads as json_loads

        from zato.common.broker_message import SCHEDULER as SCHEDULER_MSG
        from zato_scheduler_core import scheduler_start

        self._scheduler_started = False

        def _scheduler_run_cb(spawn_fn, on_job_executed_cb, ctx_json):
            spawn_fn(on_job_executed_cb, ctx_json)

        def _on_job_executed(ctx_json):
            try:
                ctx = json_loads(ctx_json)
                msg = {
                    'action': SCHEDULER_MSG.JOB_EXECUTED.value,
                    'name': ctx['name'],
                    'service': ctx['service'],
                    'payload': ctx.get('extra') or '',
                    'cid': new_cid_server(),
                    'job_type': ctx['job_type'],
                    'zato_ctx': {
                        'scheduler_job_id': ctx['id'],
                    },
                }
                self.broker_client.invoke_async(msg)
            except Exception:
                logger.warning('Scheduler dispatch error: %s', format_exc())

        try:
            scheduler_start(
                self.config_store,
                _scheduler_run_cb,
                spawn,
                _on_job_executed,
                0.5,
            )
            self._scheduler_started = True
            logger.info('Scheduler started')
        except Exception:
            logger.warning('Scheduler could not be started: %s', format_exc())

# ################################################################################################################################

    def _load_pubsub_permissions(self) -> 'None':
        """ Load pub/sub permissions from the Rust ConfigStore into the pattern matcher.
        """
        # Zato
        from zato.common.api import PubSub
        from zato_broker_core import log_admin_info

        # Load permissions
        permissions = self.config_store.get_list('pubsub_permission')

        client_permissions = {}
        username_to_sec_name = {}

        for perm in permissions:
            security = perm.get('security', '')

            if security not in client_permissions:
                client_permissions[security] = []
                username_to_sec_name[security] = security

            for topic in perm.get('pub_topics', []):
                client_permissions[security].append({
                    'pattern': topic,
                    'access_type': PubSub.API_Client.Publisher
                })
            for topic in perm.get('sub_topics', []):
                client_permissions[security].append({
                    'pattern': topic,
                    'access_type': PubSub.API_Client.Subscriber
                })

        log_admin_info(f'Loading pub/sub config -> {len(client_permissions)} permission(s)')

        for username, perms in client_permissions.items():
            self.pubsub_pattern_matcher.add_client(username, perms)

            sec_name = username_to_sec_name.get(username)
            if sec_name:
                self.pubsub_subscriptions.register_user(username, sec_name)

            log_admin_info(f'Loaded permission -> user:{username}, rules:{len(perms)}')

        # Load subscriptions
        subscriptions = self.config_store.get_list('pubsub_subscription')
        log_admin_info(f'Loading pub/sub subscriptions -> {len(subscriptions)} subscription(s)')

        for sub in subscriptions:
            security = sub.get('security', '')
            delivery_type = sub.get('delivery_type', '')
            sub_key = f'{security}:{delivery_type}'
            self.pubsub_subscriptions.register_user(security, security, sub_key)
            log_admin_info(f'Loaded subscription -> sub_key:{sub_key}, user:{security}')

            for topic_name in sub.get('topic_list', []):
                self.pubsub_backend.subscribe(sub_key, topic_name)
                log_admin_info(f'Subscribed -> sub_key:{sub_key}, topic:{topic_name}')

# ################################################################################################################################

    def reload_config(self):

        if _needs_details:
            logger.debug('Config reloading')

        # Rebuild Python-side config from the Rust ConfigStore
        self.set_up_config(self) # type: ignore

        # Reinitialize workers and pub/sub
        self.worker_store.init()
        self.worker_store.init_pubsub()

        # Reload pub/sub permissions from ConfigStore
        self._load_pubsub_permissions()

        # Notify pub/sub
        pubsub_msg = Bunch()
        pubsub_msg.cid = new_cid_server()
        pubsub_msg.action = PUBSUB.RELOAD_CONFIG.value
        self.broker_client.publish_to_pubsub(pubsub_msg)

        logger.info('Config loaded OK')

# ################################################################################################################################

    def import_enmasse(self, file_content:'str', file_name:'str') -> 'str':

        import json

        try:
            self.config_store.load_yaml_string(file_content)
            self.reload_config()

            return json.dumps({
                'is_ok': True,
                'exit_code': 0,
                'stdout': 'Loaded into ConfigStore',
                'stderr': '',
                'is_timeout': False,
                'timeout_msg': '',
                'total_time': '',
                'len_stdout_human': '',
                'len_stderr_human': '',
            })

        except Exception:
            exc = format_exc()
            logger.warning('Could not import enmasse: %s', exc)
            return json.dumps({
                'is_ok': False,
                'exit_code': -1,
                'stdout': '',
                'stderr': exc,
                'is_timeout': False,
                'timeout_msg': '',
                'total_time': '',
                'len_stdout_human': '',
                'len_stderr_human': '',
            })

# ################################################################################################################################

    def export_enmasse(self):

        import yaml
        data = self.config_store.export_to_dict()
        return yaml.dump(data, default_flow_style=False, sort_keys=True)

# ################################################################################################################################

    def import_test_pubsub_enmasse(self):

        import zato.server.service.internal.pubsub

        config_path = os.path.join(os.path.dirname(zato.server.service.internal.pubsub.__file__), 'enmasse.yaml')
        self.config_store.load_yaml(config_path)
        self.reload_config()
        return True

# ################################################################################################################################

    def download_pubsub_openapi(self):

        # Zato
        import zato.server.service.internal.pubsub

        openapi_path = os.path.join(os.path.dirname(zato.server.service.internal.pubsub.__file__), 'openapi.yaml')

        with open(openapi_path) as f:
            data = f.read()

        return data

# ################################################################################################################################

    def set_scheduler_address(self, scheduler_address:'str') -> 'None':
        pass

# ################################################################################################################################

    def _stop_after_timeout(self):

        # psutil
        import psutil

        now = utcnow()
        stop_at = now + timedelta(seconds=cast_('int', self.stop_after))

        while now < stop_at:
            logger.info(f'Now is {now}; waiting to stop until {stop_at}')
            now = utcnow()
            sleep(1)

        logger.info(f'Stopping Zato after {self.stop_after}s')

        # All the pids that we will stop
        to_stop:'intset' = set()

        # Details of each process
        details = {}

        # Our own PID
        our_pid = os.getpid()

        # If a pid has any of these names in its name or command line,
        # we consider it a process that will be stopped.
        to_include = ['zato']

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

    def set_up_api_key_config(self):

        # Prefer the value from environment variables ..
        if not (api_key_header := os.environ.get(API_Key.Env_Key)):

            # .. otherwise, use the default one .
            api_key_header = API_Key.Default_Header

        # .. now, we can set it for later use.
        self.api_key_header = api_key_header
        self.api_key_header_http = 'HTTP_' + self.api_key_header.upper().replace('-', '_')

# ################################################################################################################################

    def invoke_startup_services(self) -> 'None':
        stanza = 'startup_services'
        _invoke_startup_services('Parallel', stanza, self.fs_server_config, self.repo_location, self.broker_client, None)

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
        cache = self.worker_store.cache_api.get_cache(cache_type, cache_name)
        return cache.get(key) # type: ignore

# ################################################################################################################################

    def set_in_cache(self, cache_type:'str', cache_name:'str', key:'str', value:'any_') -> 'any_':
        """ Sets a value in cache for input parameters.
        """
        cache = self.worker_store.cache_api.get_cache(cache_type, cache_name)
        return cache.set(key, value) # type: ignore

# ################################################################################################################################

    def _remove_response_root_elem(self, data:'strdict') -> 'strdict':
        keys = list(data.keys())
        if len(keys) == 1:
            root = keys[0]
            if root.startswith('zato_') or root == 'response':
                data = data[root]

        return data

# ################################################################################################################################

    def _remove_response_elem(self, data:'strdict | anylist') -> 'strdict | anylist':

        if isinstance(data, dict):
            data = self._remove_response_root_elem(data)
        else:
            for idx, item in enumerate(data):
                item = self._remove_response_root_elem(item)
                data[idx] = item

        return data

# ################################################################################################################################

    def _set_up_grafana_cloud(self):
        logger.info('Setting up Grafana Cloud monitoring')

        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

        resource = Resource.create({'service.name': 'zato.server'})

        trace_exporter = OTLPSpanExporter(endpoint='http://localhost:4318/v1/traces')
        processor = BatchSpanProcessor(trace_exporter)

        provider = TracerProvider(resource=resource)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

        self.otlp_tracer = trace.get_tracer('zato.server')

        metrics_exporter = OTLPMetricExporter(endpoint='http://localhost:4318/v1/metrics')
        metrics_reader = PeriodicExportingMetricReader(metrics_exporter, export_interval_millis=5000)
        metrics_provider = MeterProvider(resource=resource, metric_readers=[metrics_reader])

        self.otlp_meter = metrics_provider.get_meter('zato.server')
        self.otlp_gauges = {}
        self.otlp_gauges_lock = RLock()
        self.otlp_counters = {}
        self.otlp_counters_lock = RLock()

# ################################################################################################################################

    def _set_up_datadog(self):
        logger.info('Setting up Datadog monitoring')

        # Datadog
        from ddtrace.trace import tracer
        self.datadog_tracer = tracer

# ################################################################################################################################

    def on_pubsub_message(self, body:'any_', amqp_msg:'KombuMessage', name:'str', config:'dict') -> 'None':

        # Make sure we work with a dict ..
        if not isinstance(body, dict):
            body = loads(body)

        # .. which we can now turn into a Bunch ..
        body = bunchify(body)

        # .. and now we can call the actual handler now ..
        try:
            self.on_broker_msg(body)

        # .. indicate the message has not been processed
        except Exception:
            log_msg = f'Rejecting pub/sub message: body={body}, amqp_msg={amqp_msg}, e={format_exc()}'
            logger.warning(log_msg)
            amqp_msg.reject(requeue=True)

        # .. otherwise, confirm it's been consumed.
        else:
            amqp_msg.ack()

# ################################################################################################################################

    def invoke(self, service:'str', request:'any_'=None, *args:'any_', **kwargs:'any_') -> 'any_':
        """ Invokes a service either in our own worker or, if PID is given on input, in another process of this server.
        """
        response = self.worker_store.invoke(
            service, request,
            data_format=kwargs.pop('data_format', DATA_FORMAT.DICT),
            serialize=kwargs.pop('serialize', True),
            *args, **kwargs)
        return response

# ################################################################################################################################

    def on_ipc_invoke_callback(self, msg:'bunch_') -> 'anydict':

        service:'str' = msg['service']
        data:'any_'   = msg['data']

        response:'any_' = self.invoke(service, data)
        if isinstance(response, dict):
            if 'response' in response:
                response:'any_' = response['response']
        return response # type: ignore

# ################################################################################################################################

    def invoke_async(self, service:'str', request:'any_', callback:'callable_', *args:'any_', **kwargs:'any_') -> 'any_':
        """ Invokes a service in background.
        """
        return self.worker_store.invoke(service, request, is_async=True, callback=callback, *args, **kwargs)

# ################################################################################################################################

    def encrypt(self, data:'any_', prefix:'str'=SECRETS.PREFIX, *, needs_str:'bool'=True) -> 'strnone':
        """ Returns data encrypted using server's CryptoManager.
        """
        if data:
            data = data.encode('utf8') if isinstance(data, str) else data
            encrypted = self.crypto_manager.encrypt(data, needs_str=needs_str)
            return '{}{}'.format(prefix, encrypted)

# ################################################################################################################################

    def hash_secret(self, data:'str', name:'str'='zato.default') -> 'str':
        return self.crypto_manager.hash_secret(data, name)

# ################################################################################################################################

    def verify_hash(self, given:'str', expected:'str', name:'str'='zato.default') -> 'bool':
        return self.crypto_manager.verify_hash(given, expected, name)

# ################################################################################################################################

    def decrypt(self, data:'strbytes', _prefix:'str'=SECRETS.PREFIX, _marker:'str'=SECRETS.Encrypted_Indicator) -> 'str':
        """ Returns data decrypted using server's CryptoManager.
        """

        if isinstance(data, bytes):
            data = data.decode('utf8')

        if data and data.startswith((_prefix, _marker)): # type: ignore
            return self.decrypt_no_prefix(data.replace(_prefix, '', 1)) # type: ignore
        else:
            return data # Already decrypted, return as is # type: ignore

# ################################################################################################################################

    def decrypt_no_prefix(self, data:'str') -> 'str':
        return self.crypto_manager.decrypt(data)

# ################################################################################################################################

    def _check_broker_credentials(self, username:'str', password:'str') -> 'bool':
        """ Auth callback invoked by the Rust HTTP server for each request with Basic Auth. """
        try:
            result = self.worker_store.basic_auth_get(username)
            if result:
                return result.config.password
            return False
        except Exception:
            return False

# ################################################################################################################################

    def _push_broker_credentials(self) -> 'None':
        """ Push all known Basic Auth credentials into the Rust-side store
        so that check_credentials can run without acquiring the GIL. """
        try:
            ba_config = self.worker_store.request_dispatcher.url_data.basic_auth_config
            for name in ba_config:
                entry = ba_config[name]
                password = entry.config.password
                self.broker_client.set_credentials(name, password)
        except Exception:
            logger.warning('Could not push broker credentials to Rust store')

# ################################################################################################################################

    def _check_broker_permission(self, username:'str', topic_name:'str', action:'str') -> 'bool':
        """ Permission callback invoked by the Rust HTTP server on pub/sub endpoints. """
        try:
            return self.pubsub_pattern_matcher.is_allowed(username, topic_name, action)
        except Exception:
            return False

# ################################################################################################################################

    def cleanup_on_stop(self) -> 'None':
        """ A shutdown cleanup procedure.
        """

        # Only run cleanup once
        if self._is_process_closing:
            return
        else:
            self._is_process_closing = True

        # Stop the scheduler thread
        if getattr(self, '_scheduler_started', False):
            try:
                from zato_scheduler_core import scheduler_stop
                scheduler_stop(5.0)
                logger.info('Scheduler thread stopped')
            except Exception:
                logger.warning('Error stopping scheduler: %s', format_exc())

        # Stop the broker (including its Rust HTTP server and OS thread)
        if hasattr(self, 'broker_client') and self.broker_client:
            self.broker_client.stop_consumer()

        # Close SQL pools (user-defined outgoing connections only)
        if hasattr(self, 'sql_pool_store') and self.sql_pool_store:
            self.sql_pool_store.cleanup_on_stop()

        logger.info('Stopping server process (%s:%s) (%s)', self.name, self.pid, os.getpid())

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
        return self.worker_store.reconnect_generic(*args, **kwargs) # type: ignore

# ################################################################################################################################
# ################################################################################################################################

servernone = optional[ParallelServer]

# ################################################################################################################################
# ################################################################################################################################
