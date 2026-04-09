# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Silence warnings before any imports
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, message='.*multi-threaded.*fork.*')
warnings.filterwarnings('ignore', category=UserWarning, message='.*pkg_resources is deprecated.*')

# Monkey-patching modules individually can be about 20% faster,
# or, in absolute terms, instead of 275 ms it may take 220 ms.
from gevent.monkey import patch_builtins, patch_contextvars, patch_thread, patch_time, patch_os, patch_queue, patch_select, \
     patch_selectors, patch_signal, patch_socket, patch_ssl, patch_subprocess, patch_sys

# Note that the order of patching matters, just like in patch_all
patch_os()
patch_time()
patch_thread()
patch_sys()
patch_socket()
patch_select()
patch_selectors()
patch_ssl()
patch_subprocess()
patch_builtins()
patch_signal()
patch_queue()
patch_contextvars()

# ConcurrentLogHandler - updates stdlib's logging config on import so this needs to stay after gevent patches
try:
    import cloghandler # type: ignore
except ImportError:
    pass
else:
    cloghandler = cloghandler # For pyflakes

# stdlib
import logging
import os

# Reusable
true_values = {'true', '1', 'y', 'yes'}

# Datadog monitoring - read config from env vars set by start.py
datadog_main_agent = os.environ.get('Zato_Datadog_Main_Agent')
datadog_metrics_agent = os.environ.get('Zato_Datadog_Metrics_Agent')
datadog_service_name = os.environ.get('Zato_Datadog_Service_Name') or 'zato.server'

datadog_enabled_env = os.environ.get('Zato_Datadog_Enabled')
datadog_enabled_env = datadog_enabled_env.lower() in true_values if datadog_enabled_env else False

is_datadog_enabled = datadog_enabled_env or bool(datadog_main_agent or datadog_metrics_agent)

if is_datadog_enabled:

    # Check if we need DD debug logs ..
    has_debug = os.environ.get('Zato_Datadog_Debug_Enabled')
    has_debug = has_debug.lower() in {'true', '1'} if has_debug else False
    has_debug = str(has_debug).lower()

    # .. and assign that accordingly ..
    os.environ['DD_TRACE_DEBUG'] = has_debug

    # .. set agent host if configured - must be done before importing ddtrace ..
    if datadog_main_agent:
        main_host, main_port = datadog_main_agent.split(':')
        os.environ['DD_AGENT_HOST'] = main_host
        os.environ['DD_TRACE_AGENT_PORT'] = main_port

    # .. set dogstatsd host if configured ..
    if datadog_metrics_agent:
        metrics_host, metrics_port = datadog_metrics_agent.split(':')
        os.environ['DD_DOGSTATSD_HOST'] = metrics_host
        os.environ['DD_DOGSTATSD_PORT'] = metrics_port

    # .. set service name - always ensure it exists ..
    os.environ['DD_SERVICE'] = datadog_service_name

    # .. now import and patch ddtrace after env vars are set ..
    from ddtrace import patch as dd_patch
    dd_patch(gevent=True)

# Grafana Cloud monitoring - values read later in run() after logging is configured
grafana_cloud_instance_id = None
grafana_cloud_api_key = None
grafana_cloud_endpoint = None
is_grafana_cloud_enabled = False

# stdlib
import locale
import signal
import sys
from logging.config import dictConfig
from random import seed as random_seed
from uuid import uuid4

# Update logging.Logger._log to make it a bit faster
from zato.common.microopt import logging_Logger_log
from logging import Logger
Logger._log = logging_Logger_log # type: ignore

# YAML
import yaml

# gevent
from gevent import signal_handler as gevent_signal_handler
from gevent.pywsgi import WSGIServer

# Zato
from zato.common.api import SERVER_STARTUP, TRACE1, ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.crypto.api import ServerCryptoManager
from zato.common.ext.configobj_ import ConfigObj
from zato.common.ipaddress_ import get_preferred_ip
from zato.common.odb.api import ODBManager, PoolStore
from zato.common.repo import RepoManager
from zato.common.simpleio_ import get_sio_server_config
from zato.common.util.api import asbool, get_config, is_encrypted, parse_cmd_line_options, \
     register_diag_handlers, store_pidfile, utcnow
from zato.common.util.env import populate_environment_from_file
from zato.common.util.platform_ import is_linux, is_mac, is_windows
from zato.common.util.open_ import open_r
from zato.server.base.parallel import ParallelServer
from zato.server.service.store import ServiceStore
from zato.server.startup_callable import StartupCallableTool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, callable_, dictnone, strintnone
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

# Silence out SQLAlchemy warnings
from sqlalchemy import exc as sa_exc
warnings.filterwarnings('ignore',  category=sa_exc.SAWarning, message='.*')

# ################################################################################################################################
# ################################################################################################################################

#
# Needed for SQLAlchemy 1.4
#
import oracledb
oracledb.version = '8.3.0'
sys.modules['cx_Oracle'] = oracledb

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    host = 'host'
    port = 'port'

    Env_Bind_Host = 'Zato_Config_Bind_Host'
    Env_Bind_Port = 'Zato_Config_Bind_Port'

    Env_Map = {
        host: Env_Bind_Host,
        port: Env_Bind_Port,
    }

# ################################################################################################################################
# ################################################################################################################################

class ZatoWSGIServer(WSGIServer):
    """ The main HTTP server. Currently a gevent WSGIServer,
    can be replaced with a StreamServer + Rust handler in the future.
    """
    _server_software:'str' = 'Apache'

    @property
    def server_info(self) -> 'str':
        return self._server_software

# ################################################################################################################################
# ################################################################################################################################

def _get_config_value(config_main:'Bunch', config_key:'str') -> 'strintnone':
    """ Reads a config value from environment variables first, then from the config file.
    """
    env_key = ModuleCtx.Env_Map[config_key]

    if value := os.environ.get(env_key):
        return value

    if value := config_main.get(config_key): # type: ignore
        return value # type: ignore

    return None

# ################################################################################################################################

def _parse_bind_config(config_main:'Bunch') -> 'tuple':
    """ Extracts bind host and port from configuration.
    """
    host = ''
    port = ''

    # Check environment variables first, then config keys
    if _host := _get_config_value(config_main, 'host'):
        host = str(_host)

    if _port := _get_config_value(config_main, 'port'):
        port = str(_port)

    return host, port

# ################################################################################################################################

def _create_wsgi_server(
    host:'str',
    port:'int',
    wsgi_app:'any_',
    server_software:'str'
    ) -> 'ZatoWSGIServer':
    """ Creates the WSGI server. This function is the extension point
    for replacing the transport with a StreamServer + Rust handler.
    """
    out = ZatoWSGIServer((host, port), wsgi_app, log=None)
    out._server_software = server_software
    return out

# ################################################################################################################################

def get_bin_dir() -> 'str':

    # This is where the py or python.exe command is
    bin_dir = os.path.dirname(sys.executable)

    return bin_dir

# ################################################################################################################################

def get_code_dir(bin_dir:'str') -> 'str':

    # Now, built the path up to the code_dir, which is is the directory with our code, not the directory where the server is.
    if is_linux or is_mac:
        levels = ['..']
    else:
        levels = ['..', '..', '..']

    code_dir = os.path.join(bin_dir, *levels)
    code_dir = os.path.abspath(code_dir)

    return code_dir

# ################################################################################################################################

def get_util_dir(code_dir:'str') -> 'str':
    util_dir = os.path.join(code_dir, 'util')
    return util_dir

# ################################################################################################################################

def get_env_manager_base_dir(code_dir:'str') -> 'str':
    if is_windows:
        base_dir = os.path.join(code_dir, 'bundle-ext', 'python-windows')
        return base_dir
    else:
        return code_dir

# ################################################################################################################################

def run(base_dir:'str', start_server:'bool'=True, options:'dictnone'=None) -> 'ParallelServer | None':

    # Zato
    from zato.common.util.cli import read_stdin_data

    # Type hints
    preferred_address: 'str'

    options = options or {}

    # Store a pidfile before doing anything else
    store_pidfile(base_dir)

    # Now, import environment variables and store the variable for later use
    if env_file := options.get('env_file', ''):
        initial_env_variables = populate_environment_from_file(env_file)
    else:
        initial_env_variables = []

    # For dumping stacktraces
    if is_linux:
        register_diag_handlers()

    # Capture warnings to log files
    logging.captureWarnings(True)

    #
    # Look up the standalone zato_environment.py module to import its manager object.
    # The module needs to be standalone because it runs when install.sh does,
    # that is, before the entire codebase is compiled, which is why we, in runtime,
    # need to add its path here explicitly.
    #

    bin_dir  = get_bin_dir()
    code_dir = get_code_dir(bin_dir)
    util_dir = get_util_dir(code_dir)
    env_manager_base_dir = get_env_manager_base_dir(code_dir)

    # .. make it importable ..
    sys.path.insert(0, util_dir)

    # .. now, we can import the environment manager class ..
    from zato_environment import EnvironmentManager # type: ignore

    # .. build the object that we now have access to ..
    env_manager:'any_' = EnvironmentManager(env_manager_base_dir, bin_dir)

    # .. and run the initial runtime setup, based on environment variables.
    env_manager.runtime_setup_with_env_variables()

    # Start initializing the server now
    os.chdir(base_dir)

    # We know we don't need warnings because users may explicitly configure no certificate validation.
    # We don't want for urllib3 to warn us about it.
    import requests as _r
    _r.packages.urllib3.disable_warnings() # type: ignore

    repo_location = os.path.join(base_dir, 'config', 'repo')

    # Configure the logging first, before configuring the actual server.
    logging.addLevelName('TRACE1', TRACE1) # type: ignore
    logging_conf_path = os.path.join(repo_location, 'logging.conf')

    with open_r(logging_conf_path) as f:
        _logging_config:'str' = f.read()
        _logging_config = _logging_config.replace('ConcurrentRotatingFileHandler', 'RotatingFileHandler')

        logging_config = yaml.safe_load(_logging_config)
        dictConfig(logging_config)

    logger = logging.getLogger(__name__)

    # Read Grafana Cloud config
    global grafana_cloud_instance_id, grafana_cloud_api_key, grafana_cloud_endpoint, is_grafana_cloud_enabled

    grafana_cloud_instance_id = os.environ.get('Zato_Grafana_Cloud_Instance_ID')
    grafana_cloud_api_key = os.environ.get('Zato_Grafana_Cloud_API_Key')
    grafana_cloud_endpoint = os.environ.get('Zato_Grafana_Cloud_Endpoint')

    if not (grafana_cloud_instance_id and grafana_cloud_api_key and grafana_cloud_endpoint):
        try:
            import redis as redis_lib
            redis_client = redis_lib.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            if redis_client.get('zato:grafana_cloud:is_enabled') == 'true':
                grafana_cloud_instance_id = grafana_cloud_instance_id or redis_client.get('zato:grafana_cloud:instance_id')
                grafana_cloud_api_key = grafana_cloud_api_key or redis_client.get('zato:grafana_cloud:runtime_token')
                grafana_cloud_endpoint = grafana_cloud_endpoint or redis_client.get('zato:grafana_cloud:endpoint')
        except Exception:
            pass

    is_grafana_cloud_enabled = bool(grafana_cloud_instance_id and grafana_cloud_api_key and grafana_cloud_endpoint)

    crypto_manager = ServerCryptoManager(repo_location, secret_key=options['secret_key'], stdin_data=read_stdin_data())
    secrets_config = ConfigObj(os.path.join(repo_location, 'secrets.conf'), use_zato=False)
    server_config = get_config(repo_location, 'server.conf', crypto_manager=crypto_manager, secrets_conf=secrets_config)
    pickup_config = get_config(repo_location, 'pickup.conf')

    sio_config = get_config(repo_location, 'simple-io.conf', needs_user_config=False)
    sio_config = get_sio_server_config(sio_config)

    server_config.main.token = server_config.main.token.encode('utf8')

    # Do not proceed unless we can be certain our own preferred address or IP can be obtained.
    preferred_address = server_config.preferred_address.get('address') or ''

    if not preferred_address:
        _host = server_config.main.get('host') or '0.0.0.0'
        _port = server_config.main.get('port') or ''
        preferred_address = get_preferred_ip(f'{_host}:{_port}', server_config.preferred_address)

    if not preferred_address and not server_config.server_to_server.boot_if_preferred_not_found:
        msg = 'Unable to start the server. Could not obtain a preferred address, please configure [bind_options] in server.conf'
        logger.warning(msg)
        raise Exception(msg)

    # Create the startup callable tool as soon as practical
    startup_callable_tool = StartupCallableTool(server_config)

    # Run the hook before there is any server object created
    startup_callable_tool.invoke(SERVER_STARTUP.PHASE.FS_CONFIG_ONLY, kwargs={
        'server_config': server_config,
        'pickup_config': pickup_config,
        'sio_config': sio_config,
        'base_dir': base_dir,
    })

    # Server software header for HTTP responses
    server_software = server_config.misc.get('http_server_header', 'Apache')

    user_locale = server_config.misc.get('locale', None)
    if user_locale:
        _ = locale.setlocale(locale.LC_ALL, user_locale)
        value = 12345
        logger.info('Locale is `%s`, amount of %s -> `%s`', user_locale, value, locale.currency(
            value, grouping=True))

    if server_config.misc.http_proxy:
        os.environ['http_proxy'] = server_config.misc.http_proxy

    # Parse bind configuration
    zato_host, zato_port = _parse_bind_config(server_config.main)

    # Basic components needed for the server to boot up
    odb_manager = ODBManager()
    odb_manager.well_known_data = ZATO_CRYPTO_WELL_KNOWN_DATA
    sql_pool_store = PoolStore()

    # Create it upfront here
    server = ParallelServer()

    service_store = ServiceStore(
        services={},
        odb=odb_manager,
        server=server,
        is_testing=False
    )

    server.odb = odb_manager
    server.service_store = service_store
    server.service_store.server = server
    server.sql_pool_store = sql_pool_store
    server.stderr_path = options.get('stderr_path') or ''

    # Assigned here because it is a circular dependency
    odb_manager.parallel_server = server

    stop_after = options.get('stop_after') or os.environ.get('Zato_Stop_After')  or os.environ.get('ZATO_STOP_AFTER')
    if stop_after:
        stop_after = int(stop_after)

    # Set deployment lock timeouts from config
    server.deployment_lock_expires = int(server_config.main.deployment_lock_expires)
    server.deployment_lock_timeout = int(server_config.main.deployment_lock_timeout)

    server.has_fg = options.get('fg') or False
    server.env_file = env_file
    server.env_variables_from_files[:] = initial_env_variables
    server.deploy_auto_from = options.get('deploy_auto_from') or ''
    server.crypto_manager = crypto_manager
    server.odb_data = server_config.odb
    server.host = zato_host
    server.port = zato_port
    server.use_tls = server_config.crypto.use_tls
    server.repo_location = repo_location
    server.pickup_config = pickup_config
    server.base_dir = base_dir
    server.user_conf_location = server.set_up_user_config_location()
    server.logs_dir = os.path.join(server.base_dir, 'logs')
    server.tls_dir = os.path.join(server.base_dir, 'config', 'repo', 'tls')
    server.static_dir = os.path.join(server.base_dir, 'config', 'repo', 'static')
    server.fs_server_config = server_config
    server.fs_sql_config = get_config(repo_location, 'sql.conf', needs_user_config=False)
    server.logging_config = logging_config
    server.logging_conf_path = logging_conf_path
    server.sio_config = sio_config
    server.user_config.update(server_config.user_config_items)
    server.preferred_address = preferred_address
    server.sync_internal = options['sync_internal']
    server.env_manager = env_manager
    server.startup_callable_tool = startup_callable_tool
    server.stop_after = stop_after # type: ignore

    # Monitoring
    server.is_datadog_enabled = is_datadog_enabled
    server.is_grafana_cloud_enabled = is_grafana_cloud_enabled
    server.env_name = os.environ.get('Zato_Env_Name', '')

    if scheduler_api_password := server.fs_server_config.scheduler.get('scheduler_api_password'):
        if is_encrypted(scheduler_api_password):
            server.fs_server_config.scheduler.scheduler_api_password = crypto_manager.decrypt(scheduler_api_password)

    server.return_tracebacks = asbool(server_config.misc.get('return_tracebacks', True))
    server.default_error_message = server_config.misc.get('default_error_message', 'An error has occurred')

    # Turn the repo dir into an actual repository and commit any new/modified files
    RepoManager(repo_location).ensure_repo_consistency()

    os_environ = server_config.get('os_environ') or {}
    for key, value in os_environ.items():
        os.environ[key] = value

    # Run the hook right before the server actually starts
    startup_callable_tool.invoke(SERVER_STARTUP.PHASE.IMPL_BEFORE_RUN, kwargs={
        'server': server,
    })

    # If we are not starting the server, return the ParallelServer instance for the caller
    if not start_server:
        return server

    # Set the worker index for this process - single-process model, always worker 0
    os.environ['ZATO_SERVER_WORKER_IDX'] = '0'

    # Re-seed the random number generator
    random_seed()

    # Set the PID of the worker process
    server.worker_pid = os.getpid()

    # Generate a deployment key for this server run
    deployment_key = '{}.{}'.format(utcnow().isoformat(), uuid4().hex)

    # Invoke the pre-server-start hook
    server.startup_callable_tool.invoke(SERVER_STARTUP.PHASE.BEFORE_POST_FORK, kwargs={
        'server': server,
    })

    # Initialize the server - this sets up ODB, services, broker, etc.
    ParallelServer.start_server(server, deployment_key)

    # Create the WSGI server
    wsgi_server = _create_wsgi_server(zato_host, int(zato_port), server.on_wsgi_request, server_software)

    logger.info('Starting gevent WSGIServer on %s:%s', zato_host, zato_port)

    # Graceful shutdown handler
    def _on_shutdown() -> 'None':
        logger.info('Shutting down server')
        wsgi_server.stop()
        _ = server.cleanup_on_stop()

    gevent_signal_handler(signal.SIGTERM, _on_shutdown)
    gevent_signal_handler(signal.SIGINT, _on_shutdown)

    # Start serving - this blocks until the server is stopped
    wsgi_server.serve_forever()

    return None

# ################################################################################################################################

if __name__ == '__main__':

    env_key_name = 'ZATO_SERVER_BASE_DIR'
    env_server_base_dir = os.environ.get(env_key_name)

    if env_server_base_dir:

        logging.info('Using environment key %s -> %s', env_key_name, env_server_base_dir)

        server_base_dir = env_server_base_dir
        cmd_line_options = {
            'fg': True,
            'sync_internal': True,
            'secret_key': '',
            'stderr_path': None,
            'env_file': '',
            'stop_after': None,
            'deploy_auto_from': ''
        }
    else:
        server_base_dir = sys.argv[1]
        cmd_line_options = sys.argv[2]
        cmd_line_options = parse_cmd_line_options(cmd_line_options)

    if not os.path.isabs(server_base_dir):
        server_base_dir = os.path.abspath(os.path.join(os.getcwd(), server_base_dir))

    _ = run(server_base_dir, options=cmd_line_options)

# ################################################################################################################################
# ################################################################################################################################
