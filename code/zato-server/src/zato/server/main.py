# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Silence warnings before any imports
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, message='.*multi-threaded.*fork.*')

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
datadog_main_agent = os.environ.get('Zato_Datadog_Main_Agent') or ''
datadog_metrics_agent = os.environ.get('Zato_Datadog_Metrics_Agent') or ''

datadog_enabled_env = os.environ.get('Zato_Datadog_Enabled') or ''
datadog_enabled_env = datadog_enabled_env.lower() in true_values

is_datadog_enabled = datadog_enabled_env or bool(datadog_main_agent or datadog_metrics_agent)

if is_datadog_enabled:

    # Datadog
    from ddtrace import patch as dd_patch

    # Check if we need DD debug logs ..
    has_debug = os.environ.get('Zato_Datadog_Debug_Enabled') or ''
    has_debug = has_debug.lower() in {'true', '1'}
    has_debug = str(has_debug).lower()

    # .. and assign that accordingly ..
    os.environ['DD_TRACE_DEBUG'] = has_debug

    # .. set agent host if configured ..
    if datadog_main_agent:
        main_host, main_port = datadog_main_agent.split(':')
        os.environ['DD_AGENT_HOST'] = main_host
        os.environ['DD_TRACE_AGENT_PORT'] = main_port

    # .. set dogstatsd host if configured ..
    if datadog_metrics_agent:
        metrics_host, metrics_port = datadog_metrics_agent.split(':')
        os.environ['DD_DOGSTATSD_HOST'] = metrics_host
        os.environ['DD_DOGSTATSD_PORT'] = metrics_port

    # .. now we can configure patch DD to work with gevent ..
    dd_patch(gevent=True)

# Grafana Cloud monitoring

is_grafana_cloud_enabled = os.environ.get('Zato_Grafana_Cloud_Enabled') or ''
is_grafana_cloud_enabled = is_grafana_cloud_enabled.lower() in true_values

if is_grafana_cloud_enabled:
    '''
    #
    # Grafana
    #

    import socket
    from opentelemetry.sdk.resources import Resource
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

    host_name = socket.gethostname()

    resource = Resource.create({
        'service.name': 'zato4',
        'service.instance.id': 'dev4',
        'service.namespace': 'api4',
        'deployment.environment': 'dev',
        'host.id': host_name,
        'host.name': host_name,
    })

    log_provider = LoggerProvider(resource=resource)
    log_exporter = OTLPLogExporter(endpoint='http://localhost:4318/v1/logs')
    log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    set_logger_provider(log_provider)

    handler = LoggingHandler(level=logging.INFO, logger_provider=log_provider)
    logging.getLogger().addHandler(handler)
    '''

# stdlib
import locale
import sys
from logging.config import dictConfig

# Update logging.Logger._log to make it a bit faster
from zato.common.microopt import logging_Logger_log
from logging import Logger
Logger._log = logging_Logger_log # type: ignore

# YAML
import yaml

# Zato
from zato.common.api import SERVER_STARTUP, TRACE1, ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.crypto.api import ServerCryptoManager
from zato.common.ext.configobj_ import ConfigObj
from zato.common.ipaddress_ import get_preferred_ip
from zato.common.odb.api import ODBManager, PoolStore
from zato.common.repo import RepoManager
from zato.common.simpleio_ import get_sio_server_config
from zato.common.util.api import asbool, get_config, is_encrypted, parse_cmd_line_options, \
     register_diag_handlers, store_pidfile
from zato.common.util.env import populate_environment_from_file
from zato.common.util.platform_ import is_linux, is_mac, is_windows
from zato.common.util.open_ import open_r
from zato.server.base.parallel import ParallelServer
from zato.server.ext import zunicorn
from zato.server.ext.zunicorn.app.base import Application
from zato.server.service.store import ServiceStore
from zato.server.startup_callable import StartupCallableTool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, callable_, dictnone, strintnone
    from zato.server.ext.zunicorn.config import Config as ZunicornConfig
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

    num_threads     = 'num_threads'
    bind_host       = 'bind_host'
    bind_port       = 'bind_port'

    Env_Num_Threads = 'Zato_Config_Num_Threads'
    Env_Bind_Host   = 'Zato_Config_Bind_Host'
    Env_Bind_Port   = 'Zato_Config_Bind_Port'

    Env_Map = {
        num_threads: Env_Num_Threads,
        bind_host:   Env_Bind_Host,
        bind_port:   Env_Bind_Port,
    }

# ################################################################################################################################
# ################################################################################################################################

class ZatoGunicornApplication(Application):

    cfg: 'ZunicornConfig'

    def __init__(
        self,
        zato_wsgi_app:'ParallelServer',
        repo_location:'str',
        config_main:'Bunch',
        crypto_config:'Bunch',
        *args:'any_',
        **kwargs:'any_'
    ) -> 'None':
        self.zato_wsgi_app = zato_wsgi_app
        self.repo_location = repo_location
        self.config_main = config_main
        self.crypto_config = crypto_config
        self.zato_host = ''
        self.zato_port = -1
        self.zato_config = {}
        super(ZatoGunicornApplication, self).__init__(*args, **kwargs)

# ################################################################################################################################

    def get_config_value(self, config_key:'str') -> 'strintnone':

        # First, map the config key to its corresponding environment variable
        env_key = ModuleCtx.Env_Map[config_key]

        # First, check if we have such a value among environment variables ..
        if value := os.environ.get(env_key):

            # .. if yes, we can return it now ..
            return value

        # .. we are here if there was no such environment variable ..
        # .. but maybe there is a config key on its own ..
        if value := self.config_main.get(config_key): # type: ignore

            # ..if yes, we can return it ..
            return value # type: ignore

        # .. we are here if we have nothing to return, so let's do it explicitly.
        return None

# ################################################################################################################################

    def init(self, *ignored_args:'any_', **ignored_kwargs:'any_') -> 'None':

        self.cfg.set('post_fork', self.zato_wsgi_app.post_fork) # Initializes a worker
        self.cfg.set('on_starting', self.zato_wsgi_app.on_starting) # Generates the deployment key
        self.cfg.set('before_pid_kill', self.zato_wsgi_app.before_pid_kill) # Cleans up before the worker exits
        self.cfg.set('worker_exit', self.zato_wsgi_app.worker_exit) # Cleans up after the worker exits

        for k, v in self.config_main.items():
            if k.startswith('gunicorn') and v:
                k = k.replace('gunicorn_', '')
                if k == 'bind':
                    if not ':' in v:
                        raise ValueError('No port found in main.gunicorn_bind')
                    else:
                        host, port = v.split(':')
                        self.zato_host = host
                        self.zato_port = port
                self.cfg.set(k, v)
            else:
                if 'deployment_lock' in k:
                    v = int(v)

                self.zato_config[k] = v

        # Override pre-3.2 names with non-gunicorn specific ones ..

        # .. number of processes / threads ..
        if num_threads := self.get_config_value('num_threads'):
            self.cfg.set('workers', num_threads)

        # .. what interface to bind to ..
        if bind_host := self.get_config_value('bind_host'): # type: ignore
            self.zato_host = bind_host

        # .. what is our main TCP port ..
        if bind_port := self.get_config_value('bind_port'): # type: ignore
            self.zato_port = bind_port

        # .. now, set the bind config value once more in self.cfg  ..
        # .. because it could have been overwritten via bind_host or bind_port ..
        bind = f'{self.zato_host}:{self.zato_port}'
        self.cfg.set('bind', bind)

        for name in('deployment_lock_expires', 'deployment_lock_timeout'):
            setattr(self.zato_wsgi_app, name, self.zato_config[name])

        self.zato_wsgi_app.has_gevent = 'gevent' in self.cfg.settings['worker_class'].value

    def load(self):
        return self.zato_wsgi_app.on_wsgi_request

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

def run(base_dir:'str', start_gunicorn_app:'bool'=True, options:'dictnone'=None) -> 'ParallelServer | None':

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
        preferred_address = get_preferred_ip(server_config.main.gunicorn_bind, server_config.preferred_address)

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

    zunicorn.SERVER_SOFTWARE = server_config.misc.get('http_server_header', 'Apache')

    user_locale = server_config.misc.get('locale', None)
    if user_locale:
        _ = locale.setlocale(locale.LC_ALL, user_locale)
        value = 12345
        logger.info('Locale is `%s`, amount of %s -> `%s`', user_locale, value, locale.currency(
            value, grouping=True))

    if server_config.misc.http_proxy:
        os.environ['http_proxy'] = server_config.misc.http_proxy

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

    zato_gunicorn_app = ZatoGunicornApplication(server, repo_location, server_config.main, server_config.crypto)

    server.has_fg = options.get('fg') or False
    server.env_file = env_file
    server.env_variables_from_files[:] = initial_env_variables
    server.deploy_auto_from = options.get('deploy_auto_from') or ''
    server.crypto_manager = crypto_manager
    server.odb_data = server_config.odb
    server.host = zato_gunicorn_app.zato_host
    server.port = zato_gunicorn_app.zato_port
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

    # Run the hook right before the Gunicorn-level server actually starts
    startup_callable_tool.invoke(SERVER_STARTUP.PHASE.IMPL_BEFORE_RUN, kwargs={
        'zato_gunicorn_app': zato_gunicorn_app,
    })

    # .. no memory profiler here.
    start_wsgi_app(zato_gunicorn_app, start_gunicorn_app)

# ################################################################################################################################

def start_wsgi_app(zato_gunicorn_app:'any_', start_gunicorn_app:'bool') -> 'None':

    if start_gunicorn_app:
        zato_gunicorn_app.run()
    else:
        return zato_gunicorn_app.zato_wsgi_app

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
