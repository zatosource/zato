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
from logging import INFO, WARN
from pathlib import Path
from platform import system as platform_system
from random import seed as random_seed
from time import monotonic
from traceback import format_exc
from uuid import uuid4

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock

# Zato
from zato.common.config_dispatcher import ConfigDispatchReceiver, ConfigDispatcher
from zato.common.ext.bunch import Bunch, bunchify
from zato.common.api import API_Key, DATA_FORMAT, EnvFile, EnvVariable, GENERIC, Groups, HotDeploy, SERVER_STARTUP, \
    SEC_DEF_TYPE, SERVER_UP_STATUS, ZATO_ODB_POOL_NAME
from zato.common.bearer_token import BearerTokenManager
from zato.common.broker_message import HOT_DEPLOY, PUBSUB
from zato.common.const import SECRETS
from zato.common.ext_db.api import get_ext_db_session, is_ext_db_configured, is_ext_object_id, needs_ext_db
from zato.common.facade import SecurityFacade
from zato.common.json_internal import loads
from zato.common.log_streaming import LogStreamingManager
from zato.common.marshal_.api import MarshalAPI
from zato.common.odb.api import PoolStore
from zato.common.odb.post_process import ODBPostProcess
from zato.common.pubsub.matcher import PatternMatcher
from zato.common.pubsub.redis_backend import RedisPubSubBackend
from zato.common.pubsub.subscriptions_store import SubscriptionsStore
from zato.common.rate_limiting.common import client_address_headers
from zato.common.rate_limiting.manager import RateLimitingManager
from zato.common.rules.api import RulesManager
from zato.common.typing_ import cast_, intnone, optional, tuple_
from zato.common.util.api import absolutize, as_bool, get_config_from_file, get_user_config_name, \
    fs_safe_name, invoke_startup_services as _invoke_startup_services, make_list_from_string_list, new_cid_server, \
    parse_extra_into_dict, register_diag_handlers, spawn_greenlet, StaticConfig, utcnow
from zato.common.util.env import populate_environment_from_file
from zato.common.util.file_transfer import path_string_list_to_list
from zato.common.util.file_system import get_python_files
from zato.common.util.hot_deploy_ import extract_pickup_from_items
from zato.common.util.json_ import BasicParser
from zato.common.util.log_destinations import delete_log_destination, get_log_destinations, ping_log_destination, \
    set_log_destination
from zato.common.util.logging_ import get_logging_levels, set_logging_levels, test_logging_levels
from zato.common.util.platform_ import is_posix
from zato.common.util.time_ import TimeUtil
from zato.hl7.common import add_config_location as hl7_add_config_location
from zato.distlock import LockManager
from zato.server.base.parallel.config import ConfigLoader
from zato.server.base.config_manager import ConfigManager
from zato.server.config import ConfigStore
from zato.server.connection.mcp.session import MCPSessionReaper
from zato.server.connection.server.rpc.api import ConfigCtx as _ServerRPC_ConfigCtx, ServerRPC
from zato.server.connection.server.rpc.config import ODBConfigSource
from zato.server.groups.base import GroupsManager
from zato.server.groups.ctx import SecurityGroupsCtxBuilder
from zato.server.quota_tiers import QuotaTiersManager
from zato.server.scheduler_.client import ModuleCtx as SchedulerStreamCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:

    from zato.common.ext.bunch import Bunch as bunch_
    from kombu.transport.pyamqp import Message as KombuMessage
    from zato.common.crypto.api import ServerCryptoManager
    from zato.common.odb.api import ODBManager
    from zato.common.odb.model import Cluster as ClusterModel
    from zato.common.typing_ import any_, anydict, anylist, anyset, callable_, intset, strdict, strbytes, \
        strlist, strorlistnone, strnone, strorlist, strset, strtuple
    from zato.server.base.parallel.delivery import RedisPushDelivery
    from zato.server.service.store import ServiceStore
    from zato.input_output import IOProcessor  # type: ignore[attr-defined]
    from zato.server.startup_callable import StartupCallableTool

    bunch_ = bunch_
    KombuMessage = KombuMessage
    ODBManager = ODBManager
    random_seed = random_seed
    ServerCryptoManager = ServerCryptoManager
    ServiceStore = ServiceStore
    IOProcessor = IOProcessor # type: ignore
    StartupCallableTool = StartupCallableTool

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
redis_logger = logging.getLogger('zato_redis')


# ################################################################################################################################
# ################################################################################################################################

megabyte = 10 ** 6

floatpair = tuple_[float, float]

# ################################################################################################################################
# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

# How often, at most, a still-failing Redis stream listener logs a reminder (in seconds).
_listener_error_log_interval = 60.0

# ################################################################################################################################
# ################################################################################################################################

class ParallelServer(ConfigDispatchReceiver, ConfigLoader):
    """ Main server process.
    """
    odb: 'ODBManager'
    config: 'ConfigStore'
    crypto_manager: 'ServerCryptoManager'
    sql_pool_store: 'PoolStore'

    cluster: 'ClusterModel'
    config_manager: 'ConfigManager'
    service_store: 'ServiceStore'

    rpc: 'ServerRPC'
    config_dispatcher: 'ConfigDispatcher'
    zato_lock_manager: 'LockManager'
    startup_callable_tool: 'StartupCallableTool'
    bearer_token_manager: 'BearerTokenManager'
    security_facade: 'SecurityFacade'

    stop_after: 'intnone'
    deploy_auto_from: 'str' = ''

    env_name: 'str'

    groups_manager: 'GroupsManager'
    security_groups_ctx_builder: 'SecurityGroupsCtxBuilder'
    rate_limiting_manager: 'RateLimitingManager'
    quota_tiers_manager: 'QuotaTiersManager'

    pubsub_redis: 'RedisPubSubBackend'
    pubsub_push_delivery: 'RedisPushDelivery'
    pubsub_pattern_matcher: 'PatternMatcher'
    pubsub_subscriptions: 'SubscriptionsStore'

    work_dir:'str'
    encrypt_at_rest: 'bool'

# ################################################################################################################################

    @property
    def worker_store(self) -> 'ConfigManager':
        return self.config_manager

# ################################################################################################################################

    def __init__(self) -> 'None':
        self.logger = logger
        self.host = ''
        self.port = -1
        self.use_tls = False
        self.is_starting_first = '<not-set>'
        self.odb_data = Bunch()
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
        self.io_config = cast_('any_', None)
        self.connector_server_grace_time = None
        self.id = -1
        self.name = ''
        self.process_cid = new_cid_server()
        self.server_pid = -1
        self.cluster_id = -1
        self.cluster_name = ''
        self.startup_jobs = {}
        self.deployment_lock_expires = -1
        self.deployment_lock_timeout = -1
        self.deployment_key = ''
        self.has_gevent = True
        self.static_config = Bunch()
        self.component_enabled = Bunch()
        self.client_address_headers = client_address_headers
        self.return_tracebacks = False
        self.default_error_message = ''
        self.time_util = TimeUtil()
        self.preferred_address = ''
        self.crypto_use_tls = False
        self.pid = -1
        self.sync_internal = False
        self.shmem_size = -1.0
        self.has_fg = False
        self.env_file = ''
        self.env_variables_from_files:'strlist' = []
        self._hash_secret_method = ''
        self._hash_secret_rounds = -1
        self._hash_secret_salt_size = -1
        self.platform_system = platform_system().lower()
        self.user_config = Bunch()
        self.stderr_path = ''
        self.marshal_api = MarshalAPI()
        self.env_manager = None # This is taken from util/zato_environment.py:EnvironmentManager
        self.enforce_service_invokes = False
        self.json_parser = BasicParser()
        self.api_key_header = 'Zato-Default-Not-Set-API-Key-Header'
        self.api_key_header_wsgi = 'HTTP_' + self.api_key_header.upper().replace('-', '_')
        self.needs_x_zato_cid = False
        self._queue_bridge = None
        self._queue_bridge_started = False
        self.rate_limiting_manager = RateLimitingManager()

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

        self.access_logger = logging.getLogger('zato_access_log')
        self.access_logger_log = self.access_logger._log
        self.needs_access_log = self.access_logger.isEnabledFor(INFO)
        self.needs_all_access_log = True
        self.access_log_ignore = set()
        self.rest_log_ignore   = set()
        self.has_prometheus = True
        self.is_enabled_for_warn = logging.getLogger('zato').isEnabledFor(WARN)
        self.is_admin_enabled_for_info = logging.getLogger('zato_admin').isEnabledFor(INFO)

        # Rule engine
        self.rules = RulesManager()

        # The main config store
        self.config = ConfigStore()

        # Log streaming manager
        self.log_streaming_manager = LogStreamingManager()

# ################################################################################################################################

    def maybe_on_first_server(self, server:'ParallelServer') -> 'anyset':
        """ This method will execute code with a distributed lock held. We need a lock because we can have multiple server
        processes fighting over the right to redeploy services. The first server to obtain the lock will actually perform
        the redeployment and set a flag meaning that for this particular deployment key (and remember that each server restart
        means a new deployment key) the services have been already deployed. Further servers will check that the flag exists
        and will skip the deployment altogether.
        """
        def import_initial_services_jobs() -> 'anyset':

            # Zato
            from zato.common.util.api import find_internal_modules
            from zato.server.service import internal

            # All non-internal services that we have deployed
            locally_deployed = []

            # Internal modules with that are potentially to be deployed
            deploy_internal = find_internal_modules(internal)
            internal_service_modules = []

            # All internal modules were found, now we can build a list of what is to be enabled.
            if deploy_internal:
                for module_name in deploy_internal:
                    internal_service_modules.append(module_name)
            else:
                raise Exception('No internal modules found to be imported')

            internal = self.service_store.import_internal_services(internal_service_modules, self.base_dir, self.sync_internal)
            locally_deployed.extend(internal)

            logger.info('Deploying user-defined services (%s) (%s)', self.name, self.service_sources)

            user_defined_deployed:'anylist' = self.service_store.import_services_from_anywhere(
                self.service_modules + self.service_sources, self.base_dir).to_process

            locally_deployed.extend(user_defined_deployed)
            len_user_defined_deployed = len(user_defined_deployed)

            suffix = '' if len_user_defined_deployed == 1 else 's'

            # This will be always logged ..
            logger.info('Deployed %d user-defined service%s (%s)', len_user_defined_deployed, suffix, self.name)

            # .. whereas details are optional.
            if as_bool(os.environ.get('Zato_Log_User_Services_Deployed', False)):
                for item in sorted(elem.name for elem in user_defined_deployed):
                    logger.info('Deployed user service: %s', item)

            return set(locally_deployed)

        # Remove all the deployed services from the DB ..
        self.odb.drop_deployed_services(server.id)

        # .. deploy them back including any missing ones found on other servers.
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
        from zato.common.ext.bunch import bunchify

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
        from zato.common.ext.bunch import bunchify

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

        locally_deployed = self.maybe_on_first_server(server)

        return locally_deployed

# ################################################################################################################################

    def _read_user_config_from_directory(self, dir_name:'str') -> 'None':

        # Let HL7-FHIR mapping configs resolve their names against this directory too
        hl7_add_config_location(dir_name)

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

    def set_up_odb(self) -> 'None':
        # This is the call that creates an SQLAlchemy connection
        self.config.odb_data['fs_sql_config'] = self.fs_sql_config
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.config.odb_data
        self.odb.pool = self.sql_pool_store[ZATO_ODB_POOL_NAME].pool
        self.odb.token = self.config.odb_data.token.decode('utf8')
        self.odb.decrypt_func = self.decrypt

# ################################################################################################################################

    def get_config_session(self, *, object_type:'str'='', object_id:'int'=0) -> 'any_':
        """ Returns an SQL session for configuration objects - a session to the external AS2/AS4 database
        if one is configured and the object belongs to it, a session to the main ODB otherwise.
        """

        # AS2/AS4 objects are recognized either by their type ..
        if needs_ext_db(object_type):
            out = get_ext_db_session()
            return out

        # .. or by their id, which is always offset for objects from the external database.
        if is_ext_object_id(object_id):
            out = get_ext_db_session()
            return out

        out = self.odb.session()
        return out

# ################################################################################################################################

    def build_server_rpc(self) -> 'ServerRPC':

        # What our configuration backend is
        config_source = ODBConfigSource(self.odb, self.cluster_name, self.name, self.decrypt)

        # A combination of backend and runtime configuration
        config_ctx = _ServerRPC_ConfigCtx(config_source, self)

        # A publicly available RPC client
        return ServerRPC(config_ctx)

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

        # enmasse --import --input ./zato-export.yml /path/to/server/

        # .. find all the enmasse files in this directory ..
        for file_path in sorted(path.iterdir()):

            # .. and run enmasse with each of them.
            _ = commands.run_enmasse_async_import(file_path)

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

        # Easier to type
        self = parallel_server

        # This cannot be done in __init__ because each sub-process obviously has its own PID
        self.pid = os.getpid()

        # Used later on
        use_tls = as_bool(self.fs_server_config.crypto.use_tls)

        # This changed in 3.2 so we need to take both into account
        self.work_dir = self.fs_server_config.main.get('work_dir') or self.fs_server_config.hot_deploy.get('work_dir')
        self.work_dir = os.path.normpath(os.path.join(self.repo_location, self.work_dir))

        self.encrypt_at_rest = False

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

        # This is to handle SIGURG signals.
        if is_posix:
            register_diag_handlers()

        # Store the ODB configuration, create an ODB connection pool and have self.odb use it
        self.config.odb_data = self.get_config_odb_data(self)
        self.set_up_odb()

        # Now try grabbing the basic server's data from the ODB. No point
        # in doing anything else if we can't get past this point.
        server:'any_' = self.odb.fetch_server(self.config.odb_data)

        if not server:
            raise Exception('Server does not exist in the ODB')

        # Set up the server-wide default lock manager
        odb_data:'bunch_' = self.config.odb_data

        if is_posix:
            backend_type:'str' = 'fcntl' if odb_data.engine == 'sqlite' else odb_data.engine
        else:
            backend_type = 'zato-pass-through'

        self.zato_lock_manager = LockManager(backend_type, 'zato', self.odb.session)

        # Just to make sure distributed locking is configured correctly
        with self.zato_lock_manager(uuid4().hex):
            pass

        # Basic metadata
        self.id = server.id
        self.name = server.name

        from zato.server.metrics import set_server_info
        set_server_info(self.name)

        self.cluster = self.odb.cluster
        self.cluster_id = self.cluster.id
        self.cluster_name = self.cluster.name
        # SQL post-processing
        ODBPostProcess(self.odb.session(), None, self.cluster_id).run()

        # Things like initializing SQL data on demand
        self._pre_initialize()

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

        # Build the object responsible for quota tiers - it must exist before the config is set up
        # because tier references are resolved to concrete rules at config-build time.
        self.quota_tiers_manager = QuotaTiersManager(self)

        # Reads in all configuration from ODB
        self.config_manager = ConfigManager(self.config, self)
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

        # Some parts of the config manager's configuration are required during the deployment of services
        # which is why we are doing it here, before config_manager.init() is called.
        self.config_manager.early_init()

        # Deploys services
        locally_deployed = self._after_init_common(server) # type: ignore

        # Build objects responsible for groups
        self.groups_manager = GroupsManager(self)
        self.security_groups_ctx_builder = SecurityGroupsCtxBuilder(self)

        # Initializes config manager, including connectors
        self.config_manager.init()

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

        # Set up the broker client
        self.config_dispatcher = ConfigDispatcher(server=self)

        self.pubsub_pattern_matcher = PatternMatcher()
        self.pubsub_subscriptions = SubscriptionsStore()

        # Load pub/sub permissions from database into pattern matcher
        self._load_pubsub_permissions()

        # Let the config manager know the broker client is ready
        self.config_manager.set_config_dispatcher(self.config_dispatcher)
        self.config_manager.after_config_dispatcher_set()

        self._after_init_accepted(locally_deployed)
        self.odb.server_up_down(server.token, SERVER_UP_STATUS.RUNNING, True, self.host, self.port, self.preferred_address, use_tls)

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

        # All services are deployed, build MCP tool registries now ..
        self._build_mcp_tool_registries()

        # All services are deployed, so the auto-created REST channels can be filled in now,
        # idempotently - after the first start there is usually nothing missing and the pass
        # costs one SELECT and no writes at all.
        self._create_auto_rest_channels()

        # The server is started so we can deploy what we were told to handle on startup.
        if self.deploy_auto_from:
            self.handle_enmasse_auto_from()

        # Start the Redis pub/sub backend
        self._start_pubsub_redis()

        # Start the Rust scheduler thread (in-process)
        self._start_scheduler()

        # Start the queue bridge (Kafka, SQS, etc.)
        self._start_queue_bridge()

        # Start the listener that serves OpenAPI console requests
        self._start_openapi_console_listener()

        # Optionally, if we appear to be a Docker quickstart environment, log all details about the environment.
        self.log_environment_details()

        logger.info('Started `%s@%s` (pid: %s)', server.name, server.cluster.name, self.pid)

# ################################################################################################################################

    def _create_mcp_gateways(self) -> 'None':
        """ Creates wrappers for all the MCP gateways found in the configuration store.
        MCP gateways are skipped in init_generic_connections because their tool registries
        can only resolve services once all of them are deployed, which is why the wrappers
        are built here instead - after deployment at startup and on each config reload.
        """

        # Names of the MCP gateways that exist in the configuration store ..
        config_gateway_names = set()

        # .. create or recreate a wrapper for each MCP gateway found there ..
        for config_dict in self.config_manager.config_store.generic_connection.values():

            config = config_dict['config']
            config_type = config['type_']

            if config_type == GENERIC.CONNECTION.TYPE.GATEWAY_MCP:
                config_gateway_names.add(config['name'])
                config_as_bunch = bunchify(config)
                self.config_manager._create_generic_connection(config_as_bunch)

        # .. and drop the wrappers of gateways that no longer exist in the configuration store.
        gateway_mcp = self.config_manager.gateway_mcp
        removed_names = set(gateway_mcp) - config_gateway_names

        for name in removed_names:
            gateway_config = gateway_mcp.pop(name)
            gateway_config.conn.delete()

# ################################################################################################################################

    def _build_mcp_tool_registries(self) -> 'None':
        """ Creates MCP gateway wrappers and builds their tool registries.
        Called after all services (internal and user-defined) are deployed,
        so rebuild() can resolve every service on the allow list.
        """

        # Create the MCP gateway wrappers that were skipped during init_generic_connections ..
        self._create_mcp_gateways()

        # .. now all wrappers exist with their registries populated,
        # spawn a single reaper greenlet to periodically clean up expired sessions ..
        gateway_mcp_dict = self.config_manager.gateway_mcp
        self._mcp_session_reaper = MCPSessionReaper(gateway_mcp_dict)

        _ = spawn(self._mcp_session_reaper.run)

# ################################################################################################################################

    def _create_auto_rest_channels(self) -> 'None':
        """ The startup pass over auto-created REST channels - the same batch logic as at deployment
        time, run over all the deployed services as a whole. A failure never stops the server.
        """
        try:
            from zato.server.auto_channel import create_auto_channels
            service_names = list(self.service_store.name_to_impl_name)
            create_auto_channels(self, service_names)
        except Exception:
            logger.warning('Auto-created REST channels could not be built -> %s', format_exc())

# ################################################################################################################################

    def _start_scheduler(self) -> 'None':
        """ Connect to the standalone scheduler binary via Redis Streams and HTTP.
        """
        self._scheduler_started = False

        try:
            from zato.server.scheduler_.adapter import SchedulerODBAdapter
            from zato.server.scheduler_.client import SchedulerClient

            logger.info('Connecting to scheduler')

            scheduler_adapter = SchedulerODBAdapter(self.odb, self.cluster_id)

            self._scheduler = SchedulerClient()
            self._scheduler.reload(odb_adapter=scheduler_adapter)
            self._scheduler_started = True

            self._start_scheduler_fire_listener()
            self._start_scheduler_request_listener(scheduler_adapter)

            logger.info('Scheduler client connected, fire listener started')
        except Exception:
            logger.warning('Scheduler could not be started: %s', format_exc())

    def _start_scheduler_fire_listener(self) -> 'None':
        """ Starts a dedicated greenlet that consumes fire and timeout events
        from the scheduler via Redis Streams.
        """
        fire_redis = self._scheduler.new_redis_conn()

        fire_stream = SchedulerStreamCtx.Fire_Stream
        timeout_stream = SchedulerStreamCtx.Timeout_Stream
        group_name = 'server-fire'
        consumer_name = 'server-fire-0'

        for stream in (fire_stream, timeout_stream):
            self._ensure_stream_group(fire_redis, stream, group_name)

        def _fire_listener_loop() -> 'None':
            logger.info('Scheduler fire listener loop entering')

            error_since = 0.0
            last_logged = 0.0

            while True:
                try:
                    result = fire_redis.xreadgroup(
                        groupname=group_name,
                        consumername=consumer_name,
                        streams={fire_stream: '>', timeout_stream: '>'},
                        count=10,
                        block=1000,
                    )

                    # We are able to read from the streams again, so the error condition, if any, has cleared.
                    if error_since:
                        logger.info('Scheduler fire listener recovered')
                        error_since = 0.0

                    if not result:
                        continue

                    len_result = len(result)
                    logger.info('Fire event: got %d %s in batch', len_result, 'stream' if len_result == 1 else 'streams')

                    for stream_name, messages in result:  # type: ignore[union-attr]

                        len_messages = len(messages)
                        logger.info('Fire event: stream=%r %d %s stream_type=%s',
                            stream_name, len_messages, 'message' if len_messages == 1 else 'messages',
                            type(stream_name).__name__)

                        for msg_id, fields in messages:

                            logger.info('Fire event: msg_id=%s stream=%r matched_fire=%s matched_timeout=%s fields_keys=%s',
                                msg_id, stream_name,
                                stream_name == fire_stream,
                                stream_name == timeout_stream,
                                list(fields.keys()))

                            if stream_name == fire_stream:
                                _ = spawn(self._handle_fire_event, fields)
                            elif stream_name == timeout_stream:
                                _ = spawn(self._handle_timeout_event, fields)
                            else:
                                logger.warning('Fire event: UNMATCHED stream_name=%r (type=%s) fire_stream=%r (type=%s)',
                                    stream_name, type(stream_name).__name__,
                                    fire_stream, type(fire_stream).__name__)

                            _ = fire_redis.xack(stream_name, group_name, msg_id)

                except Exception as exc:
                    error_since, last_logged = self._handle_stream_listener_error(
                        'scheduler fire', exc, fire_redis, (fire_stream, timeout_stream), group_name,
                        error_since, last_logged)
                    sleep(1)

        _ = spawn(_fire_listener_loop)
        logger.info('Scheduler fire listener greenlet started')

    def _start_scheduler_request_listener(self, scheduler_adapter:'any_') -> 'None':
        """ Listens for request_jobs messages from the scheduler and responds with a reload. """
        req_redis = self._scheduler.new_redis_conn()

        request_stream = SchedulerStreamCtx.Request_Stream
        group_name = 'server-request'
        consumer_name = 'server-request-0'

        self._ensure_stream_group(req_redis, request_stream, group_name)

        def _request_listener_loop() -> 'None':
            logger.info('Scheduler request listener loop entering')

            error_since = 0.0
            last_logged = 0.0

            while True:
                try:
                    result = req_redis.xreadgroup(
                        groupname=group_name,
                        consumername=consumer_name,
                        streams={request_stream: '>'},
                        count=10,
                        block=5000,
                    )

                    # We are able to read from the stream again, so the error condition, if any, has cleared.
                    if error_since:
                        logger.info('Scheduler request listener recovered')
                        error_since = 0.0

                    if not result:
                        continue

                    for stream_name, messages in result:  # type: ignore[union-attr]
                        for msg_id, fields in messages:
                            command = fields['command']
                            if command == 'request_jobs':
                                logger.info('Scheduler requested jobs, sending reload')
                                self._scheduler.reload(odb_adapter=scheduler_adapter)
                            _ = req_redis.xack(stream_name, group_name, msg_id)

                except Exception as exc:
                    error_since, last_logged = self._handle_stream_listener_error(
                        'scheduler request', exc, req_redis, (request_stream,), group_name, error_since, last_logged)
                    sleep(1)

        _ = spawn(_request_listener_loop)
        logger.info('Scheduler request listener greenlet started')

    def _handle_fire_event(self, fields:'dict') -> 'None':
        """ Processes a fire event from the scheduler - invokes the target service.
        """
        import time as _time
        from json import loads as json_loads
        from zato.common.ext.bunch import Bunch
        from zato.common.api import SCHEDULER
        from zato.common.broker_message import SCHEDULER as SCHEDULER_MSG

        logger.info('Fire event: handler entered, fields_keys=%s', list(fields.keys()))

        payload_json = fields['payload']
        ctx = json_loads(payload_json)

        job_id = ctx['job_id']
        job_name = ctx['name']
        current_run = ctx['current_run']

        on_success_service = ctx.get('on_success_service')
        on_success_job = ctx.get('on_success_job')
        on_error_service = ctx.get('on_error_service')
        on_error_job = ctx.get('on_error_job')

        logger.info('Invoking service for job: id=%s name=%s run=%s', job_id, job_name, current_run)

        extra = ctx.get('extra')
        if extra and isinstance(extra, str):
            try:
                extra = json_loads(extra)
            except Exception:
                try:
                    extra = parse_extra_into_dict(extra)
                except Exception:
                    pass

        msg = Bunch({
            'action': SCHEDULER_MSG.JOB_EXECUTED.value,
            'name': ctx['name'],
            'service': ctx['service'],
            'payload': extra,
            'cid': new_cid_server(),
            'job_type': ctx['job_type'],
            'zato_ctx': {
                'scheduler_job_id': job_id,
                'scheduler_current_run': current_run,
            },
        })

        # Run the main service and capture the outcome ..
        outcome = SCHEDULER.OUTCOME.OK
        error_traceback = ''
        _t0 = _time.monotonic()

        try:
            self.config_manager.on_message_invoke_service(msg, 'scheduler', 'SCHEDULER_JOB_EXECUTED')
        except Exception:
            outcome = SCHEDULER.OUTCOME.ERROR
            error_traceback = format_exc()
            logger.warning('Fire event: service exception job_id=%s name=%s traceback=%s', job_id, job_name, error_traceback)

        duration_ms = int((_time.monotonic() - _t0) * 1000)

        logger.info('Fire event: before mark_complete job_id=%s name=%s outcome=%s duration_ms=%s run=%s error_tb_len=%s',
            job_id, job_name, outcome, duration_ms, current_run, len(error_traceback))

        # .. report the outcome to the Rust scheduler ..
        try:
            self._scheduler.mark_complete(job_id, outcome, duration_ms, current_run, error_traceback)
            logger.info('Fire event: mark_complete sent job_id=%s run=%s outcome=%s', job_id, current_run, outcome)
        except Exception:
            logger.warning('Fire event: mark_complete failed job_id=%s name=%s traceback=%s', job_id, job_name, format_exc())

        # .. and spawn callback greenlets based on the outcome.
        callback_context = {
            'job_id': job_id,
            'job_name': job_name,
            'outcome': outcome,
            'duration_ms': duration_ms,
            'error_traceback': error_traceback,
            'current_run': current_run,
        }

        if outcome == SCHEDULER.OUTCOME.OK:
            on_callback_service = on_success_service
            on_callback_job = on_success_job
        else:
            on_callback_service = on_error_service
            on_callback_job = on_error_job

        event_label = 'success' if outcome == SCHEDULER.OUTCOME.OK else 'error'

        if on_callback_service:
            _ = spawn(self._invoke_callback_service, on_callback_service, callback_context, event_label)

        if on_callback_job:
            _ = spawn(self._invoke_callback_job, on_callback_job, callback_context, event_label)

    def _invoke_callback_service(self, service_name:'str', callback_context:'dict', event_label:'str') -> 'None':
        """ Invokes a Zato service as a scheduler job callback, passing the original job's context.
        """
        from json import dumps as json_dumps
        from zato.common.ext.bunch import Bunch
        from zato.common.broker_message import SCHEDULER as SCHEDULER_MSG

        job_id = callback_context['job_id']
        job_name = callback_context['job_name']

        logger.info('Invoking %s callback service=%s for job_id=%s name=%s', event_label, service_name, job_id, job_name)

        payload = json_dumps(callback_context)

        message = Bunch({
            'action': SCHEDULER_MSG.JOB_EXECUTED.value,
            'name': f'callback:{job_name}',
            'service': service_name,
            'payload': payload,
            'cid': new_cid_server(),
            'job_type': 'interval_based',
            'zato_ctx': {
                'scheduler_job_id': job_id,
                'scheduler_current_run': callback_context['current_run'],
                'is_scheduler_callback': True,
            },
        })

        try:
            self.config_manager.on_message_invoke_service(message, 'scheduler', 'SCHEDULER_JOB_EXECUTED')
        except Exception:
            logger.warning('Callback service=%s failed for job_id=%s; traceback=%s', service_name, job_id, format_exc())

    def _invoke_callback_job(self, target_job_name:'str', callback_context:'dict', event_label:'str') -> 'None':
        """ Executes another scheduler job as a callback by looking up its ID and triggering it.
        """
        from contextlib import closing
        from zato.common.odb.model import Job

        source_job_id = callback_context['job_id']
        source_job_name = callback_context['job_name']

        try:
            with closing(self.odb.session()) as session:
                target_job = session.query(Job).filter_by(name=target_job_name, cluster_id=1).first()

            if target_job is None:
                logger.warning(
                    'Callback job=%s not found for source job_id=%s name=%s', target_job_name, source_job_id, source_job_name)
                return

            if not target_job.is_active:
                logger.info(
                    'Skipping inactive callback job=%s for source job_id=%s name=%s', target_job_name, source_job_id, source_job_name)
                return

            logger.info(
                'Triggering %s callback job=%s for source job_id=%s name=%s', event_label, target_job_name, source_job_id, source_job_name)

            target_job_id = target_job.id
            self._scheduler.execute_job(target_job_id)

        except Exception:
            logger.warning(
                'Callback job=%s failed for source job_id=%s; traceback=%s', target_job_name, source_job_id, format_exc())

    def _handle_timeout_event(self, fields:'dict') -> 'None':
        """ Processes a timeout event from the scheduler.
        """
        job_id = fields['job_id']
        current_run = fields['current_run']
        elapsed_ms = fields['elapsed_ms']
        error = fields['error']
        logger.warning('Scheduler timeout: job_id=%s run=%s elapsed_ms=%s error=%s', job_id, current_run, elapsed_ms, error)

# ################################################################################################################################

    def _invoke_queue_service(self, service_name:'str', data:'any_', headers:'anydict') -> 'any_':
        """ Invoked by the recv listener greenlet when a message is received
        from an external queue (Kafka, IBM MQ, etc.) via the queue bridge binary.
        """
        wsgi_environ = {'zato.request.headers': headers}
        response = self.invoke(service_name, data, wsgi_environ=wsgi_environ)
        return response

# ################################################################################################################################

    def _enrich_queue_bridge_config(self, config:'anydict') -> 'None':
        """ Decrypts the connection's secret, if any, into the password field the bridge expects.
        """
        secret = config.get('secret')
        if isinstance(secret, str) and secret:
            if secret.startswith(SECRETS.Encrypted_Indicator) or secret.startswith(SECRETS.PREFIX):
                secret = self.decrypt(secret)
            config['password'] = secret

# ################################################################################################################################

    def _start_queue_bridge(self) -> 'None':
        """ Connect to the standalone queue bridge binary via Redis Streams and HTTP.
        """
        from contextlib import closing
        from base64 import b64decode

        from zato.common.api import GENERIC
        from zato.server.generic.connection import GenericConnection
        from zato.common.odb.query.generic import connection_list

        try:
            from zato.server.queue_bridge.client import QueueBridgeClient

            logger.info('Connecting to queue bridge')

            channels = []
            outgoing = []

            channel_types = (GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA, GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ)
            outgoing_types = (GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA, GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ)

            with closing(self.odb.session()) as session:
                for type_ in channel_types + outgoing_types:
                    items = connection_list(session, self.cluster_id, type_, False)
                    for item in items:
                        conn = GenericConnection.from_model(item)
                        config = conn.to_dict()
                        self._enrich_queue_bridge_config(config)
                        logger.info('Queue bridge loading %s', type_)

                        if type_ in channel_types:
                            channels.append(config)
                        else:
                            outgoing.append(config)

            self._queue_bridge = QueueBridgeClient()
            ch_noun = 'channel' if len(channels) == 1 else 'channels'
            out_noun = 'outgoing connection' if len(outgoing) == 1 else 'outgoing connections'
            logger.info('Sending reload to queue bridge with %d %s and %d %s', len(channels), ch_noun, len(outgoing), out_noun)
            self._queue_bridge.reload(channels=channels, outgoing=outgoing)
            self._queue_bridge_started = True

            self._start_queue_bridge_request_listener()
            self._start_queue_bridge_recv_listener(b64decode)

            logger.info('Queue bridge client connected, recv listener started')
        except Exception:
            logger.warning('Queue bridge could not be started: %s', format_exc())

# ################################################################################################################################

    def _reload_queue_bridge(self) -> 'None':
        from contextlib import closing
        from zato.common.api import GENERIC
        from zato.server.generic.connection import GenericConnection
        from zato.common.odb.query.generic import connection_list

        channels = []
        outgoing = []

        channel_types = (GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA, GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ)
        outgoing_types = (GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA, GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ)

        with closing(self.odb.session()) as session:
            for type_ in channel_types + outgoing_types:
                items = connection_list(session, self.cluster_id, type_, False)
                for item in items:
                    conn = GenericConnection.from_model(item)
                    config = conn.to_dict()
                    self._enrich_queue_bridge_config(config)
                    if type_ in channel_types:
                        channels.append(config)
                    else:
                        outgoing.append(config)

        ch_noun = 'channel' if len(channels) == 1 else 'channels'
        out_noun = 'outgoing connection' if len(outgoing) == 1 else 'outgoing connections'
        logger.info('Reloading queue bridge with %d %s and %d %s', len(channels), ch_noun, len(outgoing), out_noun)
        self._queue_bridge.reload(channels=channels, outgoing=outgoing)  # type: ignore[union-attr]

# ################################################################################################################################

    def _ensure_stream_group(self, redis_conn:'any_', stream:'str', group_name:'str') -> 'None':
        """ Creates a Redis stream and its consumer group idempotently.
        """
        try:
            _ = redis_conn.xgroup_create(stream, group_name, id='$', mkstream=True)
        except Exception as exc:

            # The group already exists, which is fine - anything else is a real error.
            if 'BUSYGROUP' not in str(exc):
                raise

# ################################################################################################################################

    def _handle_stream_listener_error(
        self,
        listener_name:'str',
        exception:'Exception',
        redis_conn:'any_',
        streams:'strtuple',
        group_name:'str',
        error_since:'float',
        last_logged:'float',
        ) -> 'floatpair':
        """ Handles an error from a Redis stream listener loop. A missing stream or consumer group, e.g. one deleted
        by another process that cleared this Redis database, is logged as a single concise line and recreated
        so the listener heals itself. Any other error logs the full traceback when the condition starts,
        then only a one-line reminder at most once a minute.
        """
        now = monotonic()
        error_text = str(exception)
        is_missing_group = 'NOGROUP' in error_text

        # Log when the condition starts - a missing stream or group gets one concise line,
        # anything else gets the full traceback ..
        if not error_since:
            error_since = now
            last_logged = now
            if is_missing_group:
                logger.warning('Recreating stream and group in %s listener: %s', listener_name, error_text)
            else:
                logger.warning('Error in %s listener: %s', listener_name, format_exc())

        # .. and only a one-line reminder at most once a minute afterwards ..
        elif now - last_logged >= _listener_error_log_interval:
            last_logged = now
            elapsed = int(now - error_since)
            logger.warning('Listener %s still failing after %ss: %s', listener_name, elapsed, exception)

        # .. if the stream or group no longer exists, recreate it so the listener heals itself.
        if is_missing_group:
            try:
                for stream in streams:
                    self._ensure_stream_group(redis_conn, stream, group_name)
            except Exception:
                # Redis may be temporarily unavailable - the next loop iteration will try again.
                pass

        return error_since, last_logged

# ################################################################################################################################

    def _start_queue_bridge_request_listener(self) -> 'None':
        """ Listens for request_config messages from the queue bridge and responds with a reload.
        The bridge sends them when it starts after this server is already up, e.g. when it is restarted.
        """
        request_redis = self._queue_bridge.new_redis_conn() # type: ignore[union-attr]

        request_stream = 'zato:queue_bridge:stream:request'
        group_name = 'server-request'
        consumer_name = 'server-request-0'

        self._ensure_stream_group(request_redis, request_stream, group_name)

        def _request_listener_loop() -> 'None':
            logger.info('Queue bridge request listener loop entering')

            error_since = 0.0
            last_logged = 0.0

            while True:
                try:
                    result = request_redis.xreadgroup(
                        groupname=group_name,
                        consumername=consumer_name,
                        streams={request_stream: '>'},
                        count=10,
                        block=5000,
                    )

                    # We are able to read from the stream again, so the error condition, if any, has cleared.
                    if error_since:
                        logger.info('Queue bridge request listener recovered')
                        error_since = 0.0

                    if not result:
                        continue

                    for stream_name, messages in result: # type: ignore[union-attr]
                        for msg_id, fields in messages:
                            command = fields['command']
                            if command == 'request_config':
                                logger.info('Queue bridge requested config, sending reload')
                                self._reload_queue_bridge()
                            _ = request_redis.xack(stream_name, group_name, msg_id)

                except Exception as exc:
                    error_since, last_logged = self._handle_stream_listener_error(
                        'queue bridge request', exc, request_redis, (request_stream,), group_name, error_since, last_logged)
                    sleep(1)

        _ = spawn(_request_listener_loop)
        logger.info('Queue bridge request listener greenlet started')

# ################################################################################################################################

    def _start_queue_bridge_recv_listener(self, b64decode:'any_') -> 'None':
        """ Starts a dedicated greenlet that consumes recv events from the queue bridge via Redis Streams.
        """
        from json import dumps as json_dumps, loads as json_loads

        recv_redis = self._queue_bridge.new_redis_conn()  # type: ignore[union-attr]

        recv_stream = 'zato:queue_bridge:stream:recv'
        group_name = 'server-recv'
        consumer_name = 'server-recv-0'

        self._ensure_stream_group(recv_redis, recv_stream, group_name)

        def _recv_listener_loop() -> 'None':

            error_since = 0.0
            last_logged = 0.0

            while True:
                try:
                    result = recv_redis.xreadgroup(
                        groupname=group_name,
                        consumername=consumer_name,
                        streams={recv_stream: '>'},
                        count=10,
                        block=1000,
                    )

                    # We are able to read from the stream again, so the error condition, if any, has cleared.
                    if error_since:
                        logger.info('Queue bridge recv listener recovered')
                        error_since = 0.0

                    if not result:
                        continue

                    for stream_name, messages in result:  # type: ignore[union-attr]
                        for msg_id, fields in messages:
                            service_name = fields['service']
                            payload_b64 = fields['payload']
                            payload = b64decode(payload_b64)

                            headers_json = fields['headers']
                            if headers_json:
                                headers = json_loads(headers_json)
                            else:
                                headers = {}

                            response = self._invoke_queue_service(service_name, payload, headers)

                            # Messages that carry a reply-to queue get the service's response
                            # sent back automatically, with no action needed in the service itself.
                            reply_to_queue = fields['reply_to_queue']
                            if reply_to_queue and response:
                                if isinstance(response, bytes):
                                    reply_data = response
                                elif isinstance(response, str):
                                    reply_data = response.encode('utf8')
                                else:
                                    reply_data = json_dumps(response).encode('utf8')

                                _ = self._queue_bridge.send_reply( # type: ignore[union-attr]
                                    fields['channel_name'],
                                    reply_to_queue,
                                    fields['reply_to_queue_manager'],
                                    fields['message_id'],
                                    reply_data,
                                )

                            _ = recv_redis.xack(stream_name, group_name, msg_id)

                except Exception as exc:
                    error_since, last_logged = self._handle_stream_listener_error(
                        'queue bridge recv', exc, recv_redis, (recv_stream,), group_name, error_since, last_logged)
                    sleep(1)

        _ = spawn(_recv_listener_loop)

        logger.info('Queue bridge recv listener greenlet started')

# ################################################################################################################################

    def _start_openapi_console_listener(self) -> 'None':
        """ Starts the greenlet that answers OpenAPI console requests arriving via Redis Streams.
        """
        try:
            from zato.server.openapi_console.listener import start_openapi_console_listener
            start_openapi_console_listener(self)
        except Exception:
            logger.warning('OpenAPI console listener could not be started: %s', format_exc())

# ################################################################################################################################

    def _start_pubsub_redis(self):

        from zato.common.pubsub.disk_store import DiskMessageStore
        from zato.common.redis_env import build_redis_connect_args, get_redis_conn_from_values, get_redis_values_from_section
        from zato.server.base.parallel.delivery import RedisPushDelivery

        # The [redis] section of server.conf describes the connection, SSL included
        redis_values = get_redis_values_from_section(self.fs_server_config.redis)

        # .. set up the disk store for message payloads ..
        work_dir = self.work_dir
        disk_store_base_dir = os.path.join(work_dir, 'pubsub-messages')
        disk_store = DiskMessageStore(disk_store_base_dir, crypto_manager=self.crypto_manager)

        redis_conn = get_redis_conn_from_values(redis_values, decode_responses=True)
        self.pubsub_redis = RedisPubSubBackend(redis_conn, disk_store, server=self)

        self.config_manager._sync_pubsub_subscriptions()
        self.config_manager._sync_pubsub_topics()

        # .. pass connection params so each delivery greenlet creates its own connection ..
        redis_conn_params = build_redis_connect_args(redis_values, decode_responses=True)

        self.pubsub_push_delivery = RedisPushDelivery(self, redis_conn_params)

        # The built-in subscriber that delivers messages published to the outbound AS4 topic -
        # it has to exist before any user service publishes its first AS4 message.
        self._setup_as4_delivery_subscription()

        for sub_key in self.config_manager._push_subs:
            self.pubsub_push_delivery.start_sub_key(sub_key)

        logger.info('PubSub Redis backend started')

# ################################################################################################################################

    def _setup_as4_delivery_subscription(self) -> 'None':
        """ Registers the built-in push subscription that consumes the outbound AS4 topic
        and hands each message over to the AS4 delivery service.
        """
        from zato.common.api import AS4, PubSub
        from zato.common.facade import _service_sub_key_prefix

        sub_key = _service_sub_key_prefix + AS4.Delivery_Service

        # Create the topic stream and the consumer group in Redis ..
        self.pubsub_redis.subscribe(sub_key, AS4.Default.Outbound_Topic)

        # .. and register the push config so a delivery greenlet picks it up.
        self.config_manager._push_subs[sub_key] = [{
            'sub_key': sub_key,
            'topic_name': AS4.Default.Outbound_Topic,
            'push_type': PubSub.Push_Type.Service,
            'push_service_name': AS4.Delivery_Service,
            'rest_push_endpoint_id': None,
        }]

# ################################################################################################################################

    def _pre_initialize(self) -> 'None':

        from contextlib import closing
        from zato.common.util.channel import ensure_as2_channel_exists, ensure_as2_mdn_channel_exists, \
            ensure_openapi_channel_exists
        from zato.common.util.gateway import ensure_mcp_gateway_exists
        from zato.common.util.scheduler import ensure_alerting_job_exists, ensure_as2_rotation_job_exists, \
            ensure_b2b_alerting_job_exists

        with closing(self.odb.session()) as session:
            openapi_created = ensure_openapi_channel_exists(session, self.cluster_id)
            mcp_created = ensure_mcp_gateway_exists(session, self.cluster_id)

            # The job completing AS2 certificate rotations always lives in the main ODB,
            # no matter where the AS2 connections themselves are stored.
            as2_rotation_job_created = ensure_as2_rotation_job_exists(session, self.cluster_id)

            # So does the job running the B2B alerting sweep.
            b2b_alerting_job_created = ensure_b2b_alerting_job_exists(session, self.cluster_id)

            # And the job running the generic alerting sweep.
            alerting_job_created = ensure_alerting_job_exists(session, self.cluster_id)

            if openapi_created or mcp_created or as2_rotation_job_created or b2b_alerting_job_created or alerting_job_created:
                session.commit()

            if openapi_created:
                logger.info('Created OpenAPI handler channel')

            if mcp_created:
                logger.info('Created MCP gateway')

            if as2_rotation_job_created:
                logger.info('Created AS2 rotation completion job')

            if b2b_alerting_job_created:
                logger.info('Created B2B alerting job')

            if alerting_job_created:
                logger.info('Created alerting sweep job')

        # AS2 channels are auto-created in the external AS2/AS4 database when one is configured
        if is_ext_db_configured():
            as2_session = get_ext_db_session()
        else:
            as2_session = self.odb.session()

        with closing(as2_session) as session:
            as2_created = ensure_as2_channel_exists(session, self.cluster_id)
            as2_mdn_created = ensure_as2_mdn_channel_exists(session, self.cluster_id)

            if as2_created or as2_mdn_created:
                session.commit()

            if as2_created:
                logger.info('Created AS2 inbound channel')

            if as2_mdn_created:
                logger.info('Created AS2 async MDN channel')

# ################################################################################################################################

    def _load_pubsub_permissions(self) -> 'None':
        """ Load pub/sub permissions from database into the pattern matcher.
        """
        # stdlib
        from contextlib import closing

        # Zato
        from zato.common.api import PubSub
        from zato.common.odb.model import PubSubPermission, PubSubSubscription, SecurityBase

        with closing(self.odb.session()) as session:

            permissions = session.query(
                PubSubPermission.pattern,
                PubSubPermission.access_type,
                SecurityBase.username,
                SecurityBase.name
            ).join(
                SecurityBase, PubSubPermission.sec_base_id == SecurityBase.id
            ).filter(
                PubSubPermission.cluster_id == self.cluster_id
            ).filter(
                SecurityBase.is_active == True  # noqa: E712
            ).all()



            client_permissions = {}
            username_to_sec_name = {}

            for pattern_str, _access_type, username, sec_name in permissions:

                if username not in client_permissions:
                    client_permissions[username] = []
                    username_to_sec_name[username] = sec_name

                # Parse the combined pattern string (e.g. "pub=demo.*\nsub=orders.*")
                for line in pattern_str.split('\n'):
                    line = line.strip()
                    if line.startswith('pub='):
                        client_permissions[username].append({
                            'pattern': line[4:],
                            'access_type': PubSub.API_Client.Publisher
                        })
                    elif line.startswith('sub='):
                        client_permissions[username].append({
                            'pattern': line[4:],
                            'access_type': PubSub.API_Client.Subscriber
                        })

            for username, perms in client_permissions.items():
                self.pubsub_pattern_matcher.add_client(username, perms)

                sec_name = username_to_sec_name.get(username)
                if sec_name:
                    _ = self.pubsub_subscriptions.register_user(username, sec_name)

            # Load subscriptions with sub_keys and their topics
            subscriptions = session.query(
                PubSubSubscription.sub_key,
                SecurityBase.username,
                SecurityBase.name
            ).join(
                SecurityBase, PubSubSubscription.sec_base_id == SecurityBase.id
            ).filter(
                PubSubSubscription.cluster_id == self.cluster_id
            ).filter(
                SecurityBase.is_active == True  # noqa: E712
            ).all()

            for sub_key, username, sec_name in subscriptions:
                _ = self.pubsub_subscriptions.register_user(username, sec_name, sub_key)

# ################################################################################################################################

    def reload_config(self):

        # Optionally, log what we're doing ..
        if _needs_details:
            logger.debug('Config reloading')

        # .. actually set up the configuration ..
        self.set_up_config(self) # type: ignore

        # .. now reload it ..
        self.config_manager.init()
        self.config_manager.init_pubsub()

        # .. MCP gateways are skipped in init_generic_connections, and by the time
        # a config reload runs, all services are already deployed, so their wrappers
        # and tool registries can be rebuilt here ..
        self._create_mcp_gateways()

        # .. reload pub/sub permissions from database ..
        self._load_pubsub_permissions()

        # .. notify the pub/sub server too ..
        pubsub_msg = Bunch()
        pubsub_msg.cid = new_cid_server()
        pubsub_msg.action = PUBSUB.RELOAD_CONFIG.value

        # .. reload the scheduler if it was started ..
        if getattr(self, '_scheduler_started', False):
            from zato.server.scheduler_.adapter import SchedulerODBAdapter
            scheduler_adapter = SchedulerODBAdapter(self.odb, self.cluster_id)
            self._scheduler.reload(odb_adapter=scheduler_adapter)

        # .. reload the queue bridge if it was started ..
        if self._queue_bridge_started:
            self._reload_queue_bridge()

        # .. finally, log what happened.
        logger.info('Config loaded OK')

# ################################################################################################################################

    def get_logging(self) -> 'strdict':
        out = get_logging_levels()
        return out

# ################################################################################################################################

    def test_logging(self, text:'str') -> 'strdict':
        out = test_logging_levels(text)
        return out

# ################################################################################################################################

    def set_logging(self, text:'str') -> 'strdict':
        out = set_logging_levels(text)
        return out

# ################################################################################################################################

    def get_log_destinations(self) -> 'strdict':
        out = get_log_destinations(self.repo_location)
        return out

# ################################################################################################################################

    def set_log_destination(self, vendor:'str', destination:'strdict') -> 'strdict':
        out = set_log_destination(self.repo_location, vendor, destination)
        return out

# ################################################################################################################################

    def delete_log_destination(self, vendor:'str', destination_id:'int') -> 'strdict':
        out = delete_log_destination(self.repo_location, vendor, destination_id)
        return out

# ################################################################################################################################

    def ping_log_destination(self, vendor:'str', destination_id:'int') -> 'strdict':
        out = ping_log_destination(self.repo_location, vendor, destination_id)
        return out

# ################################################################################################################################

    def import_enmasse(self, file_content:'str', file_name:'str') -> 'str':

        # stdlib
        import json
        import tempfile

        # Zato
        from zato.server.commands import CommandsFacade

        # Local aliases
        commands = CommandsFacade()
        commands.init(self)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            _ = temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            result = commands.run_enmasse_sync_import(temp_file_path)

            response = {
                'is_ok': result.is_ok,
                'exit_code': result.exit_code,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'is_timeout': result.is_timeout,
                'timeout_msg': result.timeout_msg if result.is_timeout else '',
                'total_time': result.total_time,
                'len_stdout_human': result.len_stdout_human,
                'len_stderr_human': result.len_stderr_human,
            }

            return json.dumps(response)

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
        finally:
            os.unlink(temp_file_path)

# ################################################################################################################################

    def export_enmasse(self):

        # Zato
        from zato.server.commands import CommandsFacade

        facade = CommandsFacade()
        facade.init(self)

        result = facade.run_enmasse_sync_export()

        if result.is_ok:
            with open('/tmp/enmasse-export.yaml') as f:
                data = f.read()
            return data
        else:
            return result.stderr

# ################################################################################################################################

    def import_demo_scheduler(self):

        import zato.server.service.internal.scheduler
        from zato.server.commands import CommandsFacade

        config_path = os.path.join(os.path.dirname(zato.server.service.internal.scheduler.__file__), 'demo-enmasse.yaml')

        facade = CommandsFacade()
        facade.init(self)

        result = facade.run_enmasse_sync_import(config_path)
        return result.is_ok

# ################################################################################################################################

    def import_demo_hl7(self):

        from zato.server.demo import import_demo_data

        result = import_demo_data(self)
        return result

# ################################################################################################################################

    def get_hl7_mllp_port(self):
        """ Returns the port the shared HL7 MLLP listener accepts connections on in this process -
        zero when no listener is running, i.e. when there are no MLLP channels.
        """
        from zato.server.generic.api.channel_hl7_mllp import get_internal_port

        result = get_internal_port()
        return result

# ################################################################################################################################

    def import_demo_ibm_mq(self):

        import zato.server.service.internal.ibm_mq
        from zato.server.commands import CommandsFacade

        config_path = os.path.join(os.path.dirname(zato.server.service.internal.ibm_mq.__file__), 'demo-enmasse.yaml')

        facade = CommandsFacade()
        facade.init(self)

        result = facade.run_enmasse_sync_import(config_path)
        return result.is_ok

# ################################################################################################################################

    def import_demo_kafka(self):

        import zato.server.service.internal.kafka
        from zato.server.commands import CommandsFacade

        config_path = os.path.join(os.path.dirname(zato.server.service.internal.kafka.__file__), 'demo-enmasse.yaml')

        facade = CommandsFacade()
        facade.init(self)

        result = facade.run_enmasse_sync_import(config_path)
        return result.is_ok

# ################################################################################################################################

    def import_demo_pubsub(self):

        import zato.server.service.internal.pubsub
        from zato.common.api import Default_Demo_PubSub_Service_File_Data
        from zato.common.util.open_ import open_w
        from zato.server.commands import CommandsFacade

        pubsub_dir = os.path.dirname(zato.server.service.internal.pubsub.__file__)
        config_path = os.path.join(pubsub_dir, 'demo-enmasse.yaml')

        full_path = os.path.join(self.hot_deploy_config.pickup_dir, 'demo_pubsub_services.py')

        with open_w(full_path) as f:
            f.write(Default_Demo_PubSub_Service_File_Data)

        facade = CommandsFacade()
        facade.init(self)

        result = facade.run_enmasse_sync_import(config_path)

        if not result.is_ok:
            logger.warning('import_demo_pubsub: enmasse failed, stdout=%s, stderr=%s',
                result.stdout.strip(), result.stderr.strip())

        return result.is_ok

# ################################################################################################################################

    def import_test_pubsub_enmasse(self):

        # Zato
        from zato.server.commands import CommandsFacade
        import zato.server.service.internal.pubsub

        config_path = os.path.join(os.path.dirname(zato.server.service.internal.pubsub.__file__), 'enmasse.yaml')

        facade = CommandsFacade()
        facade.init(self)

        result = facade.run_enmasse_sync_import(config_path)
        return result.is_ok

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
        self.api_key_header_wsgi = 'HTTP_' + self.api_key_header.upper().replace('-', '_')

# ################################################################################################################################

    def invoke_startup_services(self) -> 'None':
        stanza = 'startup_services'
        _invoke_startup_services('Parallel', stanza, self.fs_server_config, self.repo_location, self.config_dispatcher, None)

# ################################################################################################################################

    def _set_ide_password(self, ide_username:'str', ide_password:'str') -> 'None':
        service_name = 'zato.security.basic-auth.change-password'
        request = {
            'name': ide_username,
            'is_active': True,
            'type_': SEC_DEF_TYPE.BASIC_AUTH,
            'password': ide_password,
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

    def invoke(self, service:'str', request:'any_'=None, *args:'any_', **kwargs:'any_') -> 'any_':
        """ Invokes a service either in our own process or, if PID is given on input, in another process of this server.
        """
        response = self.config_manager.invoke(
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
        return self.config_manager.invoke(service, request, is_async=True, callback=callback, *args, **kwargs)

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

    @staticmethod
    def start_server_process(server:'ParallelServer', deployment_key:'str') -> 'None':
        """ Initializes the server process.
        """

        # Each subprocess needs to have the random number generator re-seeded.
        random_seed()

        server.startup_callable_tool.invoke(SERVER_STARTUP.PHASE.BEFORE_POST_FORK, kwargs={
            'server': server,
        })

        server.server_pid = os.getpid()
        ParallelServer.start_server(server, deployment_key)

# ################################################################################################################################

    def cleanup_on_stop(self) -> 'None':
        """ A shutdown cleanup procedure.
        """

        # Tell the ODB we've gone through a clean shutdown but only if the
        # ODB session has never been initialized (pre-server-start path).
        if not self.odb.session_initialized:

            self.config.odb_data = self.get_config_odb_data(self)
            self.config.odb_data['fs_sql_config'] = self.fs_sql_config
            self.set_up_odb()

            self.odb.init_session(ZATO_ODB_POOL_NAME, self.config.odb_data, self.odb.pool, False)

            self.odb.server_up_down(self.odb.token, SERVER_UP_STATUS.CLEAN_DOWN)
            self.odb.close()

        # Cleanup
        else:

            # Set the flag to True only the first time we are called, otherwise simply return
            if self._is_process_closing:
                return
            else:
                self._is_process_closing = True

            # .. stop the Redis pub/sub backend ..
            self.pubsub_push_delivery.stop()
            self.pubsub_redis.redis.close()

            # Close SQL pools
            self.sql_pool_store.cleanup_on_stop()

            logger.info('Stopping server process (%s:%s) (%s)', self.name, self.pid, os.getpid())

            import sys
            sys.exit(0)

# ################################################################################################################################

    def notify_new_package(self, package_id:'int') -> 'None':
        """ Publishes a message on the broker so all the servers (this one including
        can deploy a new package).
        """
        msg = {'action': HOT_DEPLOY.CREATE_SERVICE.value, 'package_id': package_id}
        self.config_dispatcher.publish(msg)

# ################################################################################################################################
# ################################################################################################################################

# Shortcut API methods

    def api_service_store_get_service_name_by_id(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self.service_store.get_service_name_by_id(*args, **kwargs)

    def api_config_manager_basic_auth_get_by_id(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self.config_manager.basic_auth_get_by_id(*args, **kwargs)

    def api_config_manager_reconnect_generic(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self.config_manager.reconnect_generic(*args, **kwargs) # type: ignore

# ################################################################################################################################

    def get_bearer_token(self, security_id:'str'='', raw_params:'any_'=None) -> 'any_':
        return self.bearer_token_manager.get_bearer_token_from_odb(self.odb, security_id, raw_params)

# ################################################################################################################################

    def check_attr_exists(
        self,
        entity_type:'str',
        attr_name:'str',
        value:'any_',
        filter_name:'str'='',
        filter_value:'str'='',
        soap_action:'str'='',
        method:'str'='',
        http_accept:'str'='',
        ) -> 'str':
        import json
        from contextlib import closing
        from sqlalchemy import text

        # Map logical entity types used by the frontend to actual ODB table names ..
        _entity_type_to_table = {
            'security': 'sec_base',
            'generic_connection': 'generic_conn',
            'outgoing_rest': 'http_soap',
            'outgoing_soap': 'http_soap',
            'outgoing_as4': 'http_soap',
            'channel_rest': 'http_soap',
            'channel_soap': 'http_soap',
            'channel_as4': 'http_soap',
            'channel_openapi': 'generic_conn',
            'outgoing_amqp': 'out_amqp',
            'outgoing_ftp': 'out_ftp',
            'outgoing_odoo': 'out_odoo',
            'outgoing_sql': 'sql_pool',
            'groups': 'generic_object',
            'scheduler': 'job',
            'channel_amqp': 'channel_amqp',
            'email_imap': 'email_imap',
            'email_smtp': 'email_smtp',
            'http_soap': 'http_soap',
            'pubsub_topic': 'pubsub_topic',
        }

        # The http_soap table stores channels and outgoing connections together,
        # so uniqueness must be scoped by the connection direction and transport.
        # Groups are rows in generic_object and OpenAPI channels are rows in generic_conn,
        # so both must be scoped by their respective type_ discriminator columns -
        # the unique index on generic_object is (name, type_, cluster_id), regardless of subtype ..
        _entity_type_to_extra_where = {
            'outgoing_rest': "connection = 'outgoing' AND transport = 'plain_http'",
            'outgoing_soap': "connection = 'outgoing' AND transport = 'soap'",
            'outgoing_as4':  "connection = 'outgoing' AND transport = 'as4'",
            'channel_rest':  "connection = 'channel' AND transport = 'plain_http'",
            'channel_soap':  "connection = 'channel' AND transport = 'soap'",
            'channel_as4':   "connection = 'channel' AND transport = 'as4'",
            'channel_openapi': "type_ = '{}'".format(GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI),
            'groups': "type_ = '{}'".format(Groups.Type.Group_Parent),
        }

        # Every entity type must be mapped explicitly - a silent fall-through to the entity type itself
        # would turn the next unmapped type into a confusing SQL-level error instead of a clear one ..
        table_name = _entity_type_to_table.get(entity_type)
        if not table_name:
            raise Exception(f'Unmapped entity type `{entity_type}` in check_attr_exists')

        # A channel's url_path is shared across all transports, so this check must mirror
        # ensure_channel_is_unique from the create service - scoped by connection and soap_action
        # but not by transport, with a clash reported only when the existing channel also uses
        # the same HTTP method and the same Accept header ..
        if attr_name == 'url_path' and entity_type in ('channel_rest', 'channel_soap'):

            url_path_query = "SELECT method, opaque1 FROM http_soap WHERE url_path = :val " \
                "AND connection = 'channel' AND soap_action = :soap_action"
            url_path_params = {'val': value, 'soap_action': soap_action}

            with closing(self.odb.session()) as session:
                result = session.execute(
                    text(url_path_query),  # type: ignore[operator]
                    url_path_params
                )
                rows = result.fetchall()

            exists = False

            for row in rows:

                # .. the opaque JSON column genuinely may be NULL in the database ..
                opaque_raw = row[1]
                if opaque_raw is None:
                    opaque = {}
                else:
                    opaque = json.loads(opaque_raw)

                    # .. the column may be doubly-encoded depending on which code path saved it ..
                    if isinstance(opaque, str):
                        opaque = json.loads(opaque)

                # .. the http_accept key genuinely may be absent from opaque data ..
                row_http_accept = opaque.get('http_accept')

                # .. this is the same rule the create service applies in ensure_channel_is_unique.
                if row[0] == method and row_http_accept == http_accept:
                    exists = True
                    break

            out = json.dumps({'exists': exists})
            return out

        # The value we are checking for is always bound under this key ..
        params = {'val': value}

        # .. start with the primary equality condition ..
        where = f'{attr_name} = :val'

        # .. append any entity-specific scoping conditions ..
        extra_where = _entity_type_to_extra_where.get(entity_type)
        if extra_where:
            where = f'{where} AND {extra_where}'

        # .. and, when a scoping filter is given, narrow the check down further so that
        # .. it matches the real ODB unique constraint (e.g. username is unique per sec_type) ..
        if filter_name:
            where = f'{where} AND {filter_name} = :filter_value'
            params['filter_value'] = filter_value

        with closing(self.odb.session()) as session:
            query = f'SELECT 1 FROM {table_name} WHERE {where} LIMIT 1'

            result = session.execute(
                text(query),  # type: ignore[operator]
                params
            )

            exists = result.fetchone() is not None

        out = json.dumps({'exists': exists})
        return out

# ################################################################################################################################
# ################################################################################################################################

servernone = optional[ParallelServer]

# ################################################################################################################################
# ################################################################################################################################
