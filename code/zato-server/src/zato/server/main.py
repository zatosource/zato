# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import locale, logging, os, ssl, sys
from logging.config import dictConfig

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
import cloghandler
cloghandler = cloghandler # For pyflakes

# Update logging.Logger._log to make it a bit faster
from zato.common.microopt import logging_Logger_log
from logging import Logger
Logger._log = logging_Logger_log

# gevent monkeypatch is needed
from gevent.monkey import patch_all
patch_all()

# Django
import django
from django.conf import settings

# Configure Django settings when the module is picked up
if not settings.configured:
    settings.configure()
    django.setup()

# Bunch
from bunch import Bunch

# ConfigObj
from configobj import ConfigObj

# gunicorn
import gunicorn
from gunicorn.app.base import Application

# psycopg2
import psycopg2

# psycogreen
from psycogreen.gevent import patch_psycopg as make_psycopg_green

# Repoze
from repoze.profile import ProfileMiddleware

# YAML
import yaml

# Zato
from zato.common import SERVER_STARTUP, TRACE1, ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.crypto import ServerCryptoManager
from zato.common.ipaddress_ import get_preferred_ip
from zato.common.kvdb import KVDB
from zato.common.odb.api import ODBManager, PoolStore
from zato.common.repo import RepoManager
from zato.common.util import absjoin, asbool, clear_locks, get_config, get_kvdb_config_for_log, parse_cmd_line_options, \
     register_diag_handlers, store_pidfile
from zato.common.util.cli import read_stdin_data
from zato.server.base.parallel import ParallelServer
from zato.server.service.store import ServiceStore
from zato.server.startup_callable import StartupCallableTool
from zato.sso.api import SSOAPI
from zato.sso.util import new_user_id, normalize_sso_config

# ################################################################################################################################

class ZatoGunicornApplication(Application):
    def __init__(self, zato_wsgi_app, repo_location, config_main, crypto_config, *args, **kwargs):
        self.zato_wsgi_app = zato_wsgi_app
        self.repo_location = repo_location
        self.config_main = config_main
        self.crypto_config = crypto_config
        self.zato_host = None
        self.zato_port = None
        self.zato_config = {}
        super(ZatoGunicornApplication, self).__init__(*args, **kwargs)

# ################################################################################################################################

    def init(self, *ignored_args, **ignored_kwargs):
        self.cfg.set('post_fork', self.zato_wsgi_app.post_fork) # Initializes a worker
        self.cfg.set('on_starting', self.zato_wsgi_app.on_starting) # Generates the deployment key
        self.cfg.set('worker_exit', self.zato_wsgi_app.worker_exit) # Cleans up after the worker

        for k, v in self.config_main.items():
            if k.startswith('gunicorn') and v:
                k = k.replace('gunicorn_', '')
                if k == 'bind':
                    if not ':' in v:
                        raise ValueError('No port found in main.gunicorn_bind `{}`, such as `{}:17010`'.format(v))
                    else:
                        host, port = v.split(':')
                        self.zato_host = host
                        self.zato_port = port
                self.cfg.set(k, v)
            else:
                if 'deployment_lock' in k:
                    v = int(v)

                self.zato_config[k] = v

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

def run(base_dir, start_gunicorn_app=True, options=None):
    options = options or {}

    # Store a pidfile before doing anything else
    store_pidfile(base_dir)

    # For dumping stacktraces
    register_diag_handlers()

    # Capture warnings to log files
    logging.captureWarnings(True)

    # Start initializing the server now
    os.chdir(base_dir)

    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass

    # We're doing it here even if someone doesn't use PostgreSQL at all
    # so we're not suprised when someone suddenly starts using PG.
    # TODO: Make sure it's registered for each of the subprocess
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

    # We know we don't need warnings because users may explicitly configure no certificate validation.
    # We don't want for urllib3 to warn us about it.
    import requests as _r
    _r.packages.urllib3.disable_warnings()

    repo_location = os.path.join(base_dir, 'config', 'repo')

    # Configure the logging first, before configuring the actual server.
    logging.addLevelName('TRACE1', TRACE1)
    logging_conf_path = os.path.join(repo_location, 'logging.conf')

    with open(logging_conf_path) as f:
        logging_config = yaml.load(f)
        dictConfig(logging_config)

    logger = logging.getLogger(__name__)
    kvdb_logger = logging.getLogger('zato_kvdb')

    crypto_manager = ServerCryptoManager(repo_location, secret_key=options['secret_key'], stdin_data=read_stdin_data())
    secrets_config = ConfigObj(os.path.join(repo_location, 'secrets.conf'), use_zato=False)
    server_config = get_config(repo_location, 'server.conf', crypto_manager=crypto_manager, secrets_conf=secrets_config)
    pickup_config = get_config(repo_location, 'pickup.conf')
    sio_config = get_config(repo_location, 'simple-io.conf', needs_user_config=False)
    sso_config = get_config(repo_location, 'sso.conf', needs_user_config=False)
    normalize_sso_config(sso_config)

    '''secrets_config_zato = secrets_config.get('zato')
    if secrets_config_zato:
        token = secrets_config_zato.get('server_conf.main.token')
        if token:
            secrets_config_zato['server_conf.main.token'] = token.encode('utf8')
            '''

    server_config.main.token = server_config.main.token.encode('utf8')

    # Do not proceed unless we can be certain our own preferred address or IP can be obtained.
    preferred_address = server_config.preferred_address.get('address')

    if not preferred_address:
        preferred_address = get_preferred_ip(server_config.main.gunicorn_bind, server_config.preferred_address)

    if not preferred_address and not server_config.server_to_server.boot_if_preferred_not_found:
        msg = 'Unable to start the server. Could not obtain a preferred address, please configure [bind_options] in server.conf'
        logger.warn(msg)
        raise Exception(msg)

    # Create the startup callable tool as soon as practical
    startup_callable_tool = StartupCallableTool(server_config)

    # Run the hook before there is any server object created
    startup_callable_tool.invoke(SERVER_STARTUP.PHASE.FS_CONFIG_ONLY, kwargs={
        'server_config': server_config,
        'pickup_config': pickup_config,
        'sio_config': sio_config,
        'sso_config': sso_config,
    })

    # New in 2.0 - Start monitoring as soon as possible
    if server_config.get('newrelic', {}).get('config'):
        import newrelic.agent
        newrelic.agent.initialize(
            server_config.newrelic.config, server_config.newrelic.environment or None, server_config.newrelic.ignore_errors or None,
            server_config.newrelic.log_file or None, server_config.newrelic.log_level or None)

    # New in 2.0 - override gunicorn-set Server HTTP header
    gunicorn.SERVER_SOFTWARE = server_config.misc.get('http_server_header', 'Zato')

    # Store KVDB config in logs, possibly replacing its password if told to
    kvdb_config = get_kvdb_config_for_log(server_config.kvdb)
    kvdb_logger.info('Main process config `%s`', kvdb_config)

    # New in 2.0 hence optional
    user_locale = server_config.misc.get('locale', None)
    if user_locale:
        locale.setlocale(locale.LC_ALL, user_locale)
        value = 12345
        logger.info('Locale is `%s`, amount of %s -> `%s`', user_locale, value, locale.currency(
            value, grouping=True).decode('utf-8'))

    # Makes queries against Postgres asynchronous
    if asbool(server_config.odb.use_async_driver) and server_config.odb.engine == 'postgresql':
        make_psycopg_green()

    if server_config.misc.http_proxy:
        os.environ['http_proxy'] = server_config.misc.http_proxy

    # Basic components needed for the server to boot up
    kvdb = KVDB()
    odb_manager = ODBManager(well_known_data=ZATO_CRYPTO_WELL_KNOWN_DATA)
    sql_pool_store = PoolStore()

    service_store = ServiceStore()
    service_store.odb = odb_manager
    service_store.services = {}

    server = ParallelServer()
    server.odb = odb_manager
    server.service_store = service_store
    server.service_store.server = server
    server.sql_pool_store = sql_pool_store
    server.service_modules = []
    server.kvdb = kvdb
    server.user_config = Bunch()

    zato_gunicorn_app = ZatoGunicornApplication(server, repo_location, server_config.main, server_config.crypto)

    server.crypto_manager = crypto_manager
    server.odb_data = server_config.odb
    server.host = zato_gunicorn_app.zato_host
    server.port = zato_gunicorn_app.zato_port
    server.repo_location = repo_location
    server.user_conf_location = os.path.join(server.repo_location, 'user-conf')
    server.base_dir = base_dir
    server.logs_dir = os.path.join(server.base_dir, 'logs')
    server.tls_dir = os.path.join(server.base_dir, 'config', 'repo', 'tls')
    server.static_dir = os.path.join(server.base_dir, 'config', 'repo', 'static')
    server.fs_server_config = server_config
    server.fs_sql_config = get_config(repo_location, 'sql.conf', needs_user_config=False)
    server.pickup_config = pickup_config
    server.logging_config = logging_config
    server.logging_conf_path = logging_conf_path
    server.sio_config = sio_config
    server.sso_config = sso_config
    server.user_config.update(server_config.user_config_items)
    server.preferred_address = preferred_address
    server.sync_internal = options['sync_internal']
    server.jwt_secret = server.fs_server_config.misc.jwt_secret.encode('utf8')
    server.startup_callable_tool = startup_callable_tool
    server.is_sso_enabled = server.fs_server_config.component_enabled.sso
    if server.is_sso_enabled:
        server.sso_api = SSOAPI(server, sso_config, None, crypto_manager.encrypt, crypto_manager.decrypt,
            crypto_manager.hash_secret, crypto_manager.verify_hash, new_user_id)

    # Remove all locks possibly left over by previous server instances
    kvdb.component = 'master-proc'
    clear_locks(kvdb, server_config.main.token, server_config.kvdb, crypto_manager.decrypt)

    # New in 2.0.8
    server.return_tracebacks = asbool(server_config.misc.get('return_tracebacks', True))
    server.default_error_message = server_config.misc.get('default_error_message', 'An error has occurred')

    # Turn the repo dir into an actual repository and commit any new/modified files
    RepoManager(repo_location).ensure_repo_consistency()

    # New in 2.0 so it's optional.
    profiler_enabled = server_config.get('profiler', {}).get('enabled', False)

    # New in 2.0 so it's optional.
    sentry_config = server_config.get('sentry')

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
        profiler_dir = os.path.abspath(os.path.join(base_dir, server_config.profiler.profiler_dir))
        server.on_wsgi_request = ProfileMiddleware(
            server.on_wsgi_request,
            log_filename = os.path.join(profiler_dir, server_config.profiler.log_filename),
            cachegrind_filename = os.path.join(profiler_dir, server_config.profiler.cachegrind_filename),
            discard_first_request = server_config.profiler.discard_first_request,
            flush_at_shutdown = server_config.profiler.flush_at_shutdown,
            path = server_config.profiler.url_path,
            unwind = server_config.profiler.unwind)

    # New in 2.0 - set environmet variables for servers to inherit
    os_environ = server_config.get('os_environ', {})
    for key, value in os_environ.items():
        os.environ[key] = value

    # Run the hook right before the Gunicorn-level server actually starts
    startup_callable_tool.invoke(SERVER_STARTUP.PHASE.IMPL_BEFORE_RUN, kwargs={
        'zato_gunicorn_app': zato_gunicorn_app,
    })

    # Run the app at last
    if start_gunicorn_app:
        zato_gunicorn_app.run()
    else:
        return zato_gunicorn_app.zato_wsgi_app

# ################################################################################################################################

if __name__ == '__main__':

    server_base_dir = sys.argv[1]
    cmd_line_options = sys.argv[2]

    if not os.path.isabs(server_base_dir):
        server_base_dir = os.path.abspath(os.path.join(os.getcwd(), server_base_dir))

    run(server_base_dir, options=parse_cmd_line_options(cmd_line_options))

# ################################################################################################################################
