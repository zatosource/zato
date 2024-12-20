# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Monkey-patching modules individually can be about 20% faster,
# or, in absolute terms, instead of 275 ms it may take 220 ms.
from gevent.monkey import patch_builtins, patch_contextvars, patch_thread, patch_time, patch_os, patch_queue, patch_select, \
     patch_selectors, patch_signal, patch_socket, patch_ssl, patch_subprocess, patch_sys

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
try:
    import cloghandler # type: ignore
except ImportError:
    pass
else:
    cloghandler = cloghandler # For pyflakes

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

# stdlib
import locale
import logging
import os
import ssl
import sys
from logging.config import dictConfig

# Update logging.Logger._log to make it a bit faster
from zato.common.microopt import logging_Logger_log
from logging import Logger
Logger._log = logging_Logger_log # type: ignore

# YAML
import yaml

# Zato
from zato.common.api import IPC, OS_Env, SERVER_STARTUP, TRACE1, ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.crypto.api import ServerCryptoManager
from zato.common.ext.configobj_ import ConfigObj
from zato.common.ipaddress_ import get_preferred_ip
from zato.common.kvdb.api import KVDB
from zato.common.odb.api import ODBManager, PoolStore
from zato.common.repo import RepoManager
from zato.common.simpleio_ import get_sio_server_config
from zato.common.typing_ import cast_
from zato.common.util.api import absjoin, asbool, get_config, get_kvdb_config_for_log, is_encrypted, parse_cmd_line_options, \
     register_diag_handlers, store_pidfile
from zato.common.util.env import populate_environment_from_file
from zato.common.util.platform_ import is_linux, is_mac, is_windows
from zato.common.util.open_ import open_r
from zato.server.base.parallel import ParallelServer
from zato.server.ext import zunicorn
from zato.server.ext.zunicorn.app.base import Application
from zato.server.service.store import ServiceStore
from zato.server.startup_callable import StartupCallableTool
from zato.sso.api import SSOAPI
from zato.sso.util import new_user_id, normalize_sso_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, callable_, dictnone, strintnone
    from zato.server.ext.zunicorn.config import Config as ZunicornConfig
    callable_ = callable_

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

        if asbool(self.crypto_config.use_tls):
            self.cfg.set('ssl_version', getattr(ssl, 'PROTOCOL_{}'.format(self.crypto_config.tls_protocol)))
            self.cfg.set('ciphers', self.crypto_config.tls_ciphers)
            self.cfg.set('cert_reqs', getattr(ssl, 'CERT_{}'.format(self.crypto_config.tls_client_certs.upper())))
            self.cfg.set('ca_certs', absjoin(self.repo_location, self.crypto_config.ca_certs_location))
            self.cfg.set('keyfile', absjoin(self.repo_location, self.crypto_config.priv_key_location))
            self.cfg.set('certfile', absjoin(self.repo_location, self.crypto_config.cert_location))
            self.cfg.set('do_handshake_on_connect', True)

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
    kvdb_logger = logging.getLogger('zato_kvdb')

    crypto_manager = ServerCryptoManager(repo_location, secret_key=options['secret_key'], stdin_data=read_stdin_data())
    secrets_config = ConfigObj(os.path.join(repo_location, 'secrets.conf'), use_zato=False)
    server_config = get_config(repo_location, 'server.conf', crypto_manager=crypto_manager, secrets_conf=secrets_config)
    pickup_config = get_config(repo_location, 'pickup.conf')

    if server_config.main.get('debugger_enabled'):
        import debugpy
        debugger_host = server_config.main.debugger_host
        debugger_port = server_config.main.debugger_port
        logger.info('Debugger waiting for connections on %s:%s', debugger_host, debugger_port)
        _ = debugpy.listen((debugger_host, debugger_port))
        debugpy.wait_for_client()

    sio_config = get_config(repo_location, 'simple-io.conf', needs_user_config=False)
    sio_config = get_sio_server_config(sio_config)

    sso_config = get_config(repo_location, 'sso.conf', needs_user_config=False)
    normalize_sso_config(sso_config)

    # Now that we have access to server.conf, greenify libraries required to be made greenlet-friendly,
    # assuming that there are any - otherwise do not do anything.
    to_greenify = []
    for key, value in server_config.get('greenify', {}).items():
        if asbool(value):
            if not os.path.exists(key):
                raise ValueError('No such path `{}`'.format(key))
            else:
                to_greenify.append(key)

    # Go ahead only if we actually have anything to greenify
    if to_greenify:
        import greenify # type: ignore
        greenify.greenify()
        for name in to_greenify:
            result = greenify.patch_lib(name)
            if not result:
                raise ValueError('Library `{}` could not be greenified'.format(name))
            else:
                logger.info('Greenified library `%s`', name)

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
        'sso_config': sso_config,
        'base_dir': base_dir,
    })

    # Start monitoring as soon as possible
    if server_config.get('newrelic', {}).get('config'):
        import newrelic.agent # type: ignore
        newrelic.agent.initialize(
            server_config.newrelic.config, server_config.newrelic.environment or None, server_config.newrelic.ignore_errors or None,
            server_config.newrelic.log_file or None, server_config.newrelic.log_level or None)

    zunicorn.SERVER_SOFTWARE = server_config.misc.get('http_server_header', 'Apache')

    # Store KVDB config in logs, possibly replacing its password if told to
    kvdb_config = get_kvdb_config_for_log(server_config.kvdb)
    kvdb_logger.info('Main process config `%s`', kvdb_config)

    user_locale = server_config.misc.get('locale', None)
    if user_locale:
        _ = locale.setlocale(locale.LC_ALL, user_locale)
        value = 12345
        logger.info('Locale is `%s`, amount of %s -> `%s`', user_locale, value, locale.currency(
            value, grouping=True))

    if server_config.misc.http_proxy:
        os.environ['http_proxy'] = server_config.misc.http_proxy

    # Basic components needed for the server to boot up
    kvdb = KVDB()
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
    server.kvdb = kvdb
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
    server.json_schema_dir = os.path.join(server.base_dir, 'config', 'repo', 'schema', 'json')
    server.fs_server_config = server_config
    server.fs_sql_config = get_config(repo_location, 'sql.conf', needs_user_config=False)
    server.logging_config = logging_config
    server.logging_conf_path = logging_conf_path
    server.sio_config = sio_config
    server.sso_config = sso_config
    server.user_config.update(server_config.user_config_items)
    server.preferred_address = preferred_address
    server.sync_internal = options['sync_internal']
    server.env_manager = env_manager
    server.jwt_secret = server.fs_server_config.misc.jwt_secret.encode('utf8')
    server.startup_callable_tool = startup_callable_tool
    server.stop_after = stop_after # type: ignore
    server.is_sso_enabled = server.fs_server_config.component_enabled.sso
    if server.is_sso_enabled:
        server.sso_api = SSOAPI(server, sso_config, cast_('callable_', None), crypto_manager.encrypt, server.decrypt,
            crypto_manager.hash_secret, crypto_manager.verify_hash, new_user_id)

    if scheduler_api_password := server.fs_server_config.scheduler.get('scheduler_api_password'):
        if is_encrypted(scheduler_api_password):
            server.fs_server_config.scheduler.scheduler_api_password = crypto_manager.decrypt(scheduler_api_password)

    server.return_tracebacks = asbool(server_config.misc.get('return_tracebacks', True))
    server.default_error_message = server_config.misc.get('default_error_message', 'An error has occurred')

    # Turn the repo dir into an actual repository and commit any new/modified files
    RepoManager(repo_location).ensure_repo_consistency()

    # For IPC communication
    ipc_password = crypto_manager.generate_secret()
    ipc_password = ipc_password.decode('utf8')

    # .. this is for our own process ..
    server.set_ipc_password(ipc_password)

    # .. this is for other processes.
    ipc_password_encrypted = crypto_manager.encrypt(ipc_password, needs_str=True)
    _ipc_password_key = IPC.Credentials.Password_Key
    os.environ[_ipc_password_key] = ipc_password_encrypted

    profiler_enabled = server_config.get('profiler', {}).get('enabled', False)
    sentry_config = server_config.get('sentry') or {}

    dsn = sentry_config.pop('dsn', None)
    if dsn:

        from raven import Client
        from raven.handlers.logging import SentryHandler

        handler_level = sentry_config.pop('level')
        client = Client(dsn, **sentry_config)

        handler = SentryHandler(client=client)
        handler.setLevel(getattr(logging, handler_level))

        logger = logging.getLogger('')
        logger.addHandler(handler)

        for name in logging.Logger.manager.loggerDict:
            if name.startswith('zato'):
                logger = logging.getLogger(name)
                logger.addHandler(handler)

    if asbool(profiler_enabled):

        # Repoze
        from repoze.profile import ProfileMiddleware

        profiler_dir = os.path.abspath(os.path.join(base_dir, server_config.profiler.profiler_dir))
        server.on_wsgi_request = ProfileMiddleware(
            server.on_wsgi_request,
            log_filename = os.path.join(profiler_dir, server_config.profiler.log_filename),
            cachegrind_filename = os.path.join(profiler_dir, server_config.profiler.cachegrind_filename),
            discard_first_request = server_config.profiler.discard_first_request,
            flush_at_shutdown = server_config.profiler.flush_at_shutdown,
            path = server_config.profiler.url_path,
            unwind = server_config.profiler.unwind)

    os_environ = server_config.get('os_environ', {})
    for key, value in os_environ.items():
        os.environ[key] = value

    # Run the hook right before the Gunicorn-level server actually starts
    startup_callable_tool.invoke(SERVER_STARTUP.PHASE.IMPL_BEFORE_RUN, kwargs={
        'zato_gunicorn_app': zato_gunicorn_app,
    })

    # This will optionally enable the RAM usage profiler.
    memory_profiler_key = OS_Env.Zato_Enable_Memory_Profiler
    enable_memory_profiler = os.environ.get(memory_profiler_key)

    if enable_memory_profiler:

        # stdlib
        from tempfile import mkdtemp

        # memray
        import memray # type: ignore

        # Create an empty directory to store the output in ..
        dir_name = mkdtemp(prefix='zato-memory-profiler-')

        # .. now, the full path to the memory profile file ..
        full_path = os.path.join(dir_name, 'zato-memory-profile.bin')

        # .. we can start the memray's tracker now ..
        with memray.Tracker(full_path):
            logger.info('Starting with memory profiler; output in -> %s', full_path)

            # .. finally, start the server
            start_wsgi_app(zato_gunicorn_app, start_gunicorn_app)

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
