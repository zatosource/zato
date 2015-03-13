# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import locale, logging, os, ssl, sys
from logging.config import dictConfig

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
import cloghandler
cloghandler = cloghandler # For pyflakes

# gunicorn
import gunicorn
from gunicorn.app.base import Application

# Paste
from paste.util.converters import asbool

# psycopg2
import psycopg2

# psycogreen
from psycogreen.gevent import patch_psycopg as make_psycopg_green

# Repoze
from repoze.profile import ProfileMiddleware

# YAML
import yaml

# Zato
from zato.common import TRACE1
from zato.common.repo import RepoManager
from zato.common.util import absolutize_path, clear_locks, get_app_context, get_config, get_crypto_manager, \
     get_kvdb_config_for_log, register_diag_handlers, store_pidfile

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

    def init(self, *ignored_args, **ignored_kwargs):
        self.cfg.set('post_fork', self.zato_wsgi_app.post_fork) # Initializes a worker
        self.cfg.set('on_starting', self.zato_wsgi_app.on_starting) # Generates the deployment key

        for k, v in self.config_main.items():
            if k.startswith('gunicorn') and v:
                k = k.replace('gunicorn_', '')
                if k == 'bind':
                    if not ':' in v:
                        raise ValueError('No port found in main.gunicorn_bind [{v}]; a proper value is, for instance, [{v}:17010]'.format(v=v))
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

        # TLS is new in 2.0 and we need to assume it's not enabled. In Zato 2.1 or later
        # this will be changed to assume that we are always over TLS by default.
        if asbool(self.crypto_config.get('use_tls', False)):
            self.cfg.set('ssl_version', getattr(ssl, 'PROTOCOL_{}'.format(self.crypto_config.tls_protocol)))
            self.cfg.set('ciphers', self.crypto_config.tls_ciphers)
            self.cfg.set('cert_reqs', getattr(ssl, 'CERT_{}'.format(self.crypto_config.tls_client_certs.upper())))
            self.cfg.set('ca_certs', absolutize_path(self.repo_location, self.crypto_config.ca_certs_location))
            self.cfg.set('keyfile', absolutize_path(self.repo_location, self.crypto_config.priv_key_location))
            self.cfg.set('certfile', absolutize_path(self.repo_location, self.crypto_config.cert_location))
            self.cfg.set('do_handshake_on_connect', True)

        self.zato_wsgi_app.has_gevent = 'gevent' in self.cfg.settings['worker_class'].value
        
    def load(self):
        return self.zato_wsgi_app.on_wsgi_request

def run(base_dir, start_gunicorn_app=True):

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

    repo_location = os.path.join(base_dir, 'config', 'repo')

    # Configure the logging first, before configuring the actual server.
    logging.addLevelName('TRACE1', TRACE1)

    with open(os.path.join(repo_location, 'logging.conf')) as f:
        dictConfig(yaml.load(f))

    logger = logging.getLogger(__name__)
    kvdb_logger = logging.getLogger('zato_kvdb')

    config = get_config(repo_location, 'server.conf')

    # New in 2.0 - Start monitoring as soon as possible
    if config.get('newrelic', {}).get('config'):
        import newrelic.agent
        newrelic.agent.initialize(
            config.newrelic.config, config.newrelic.environment or None, config.newrelic.ignore_errors or None,
            config.newrelic.log_file or None, config.newrelic.log_level or None)

    # New in 2.0 - override gunicorn-set Server HTTP header
    gunicorn.SERVER_SOFTWARE = config.misc.get('http_server_header', 'Zato')

    # Store KVDB config in logs, possibly replacing its password if told to
    kvdb_config = get_kvdb_config_for_log(config.kvdb)
    kvdb_logger.info('Master process config `%s`', kvdb_config)

    # New in 2.0 hence optional
    user_locale = config.misc.get('locale', None)
    if user_locale:
        locale.setlocale(locale.LC_ALL, user_locale)
        value = 12345
        logger.info('Locale is `%s`, amount of %s -> `%s`', user_locale, value,
                    locale.currency(value, grouping=True).decode('utf-8'))

    # Spring Python
    app_context = get_app_context(config)

    # Makes queries against Postgres asynchronous
    if asbool(config.odb.use_async_driver) and config.odb.engine == 'postgresql':
        make_psycopg_green()

    # New in 2.0 - Put HTTP_PROXY in os.environ.
    http_proxy = config.misc.get('http_proxy', False)
    if http_proxy:
        os.environ['http_proxy'] = http_proxy

    crypto_manager = get_crypto_manager(repo_location, app_context, config)
    parallel_server = app_context.get_object('parallel_server')

    zato_gunicorn_app = ZatoGunicornApplication(parallel_server, repo_location, config.main, config.crypto)

    parallel_server.crypto_manager = crypto_manager
    parallel_server.odb_data = config.odb
    parallel_server.host = zato_gunicorn_app.zato_host
    parallel_server.port = zato_gunicorn_app.zato_port
    parallel_server.repo_location = repo_location
    parallel_server.base_dir = base_dir
    parallel_server.tls_dir = os.path.join(parallel_server.base_dir, 'config', 'repo', 'tls')
    parallel_server.fs_server_config = config
    parallel_server.user_config.update(config.user_config_items)
    parallel_server.startup_jobs = app_context.get_object('startup_jobs')
    parallel_server.app_context = app_context

    # Remove all locks possibly left over by previous server instances
    kvdb = app_context.get_object('kvdb')
    kvdb.component = 'master-proc'
    clear_locks(kvdb, config.main.token, config.kvdb, crypto_manager.decrypt)

    # Turn the repo dir into an actual repository and commit any new/modified files
    RepoManager(repo_location).ensure_repo_consistency()

    # New in 2.0 so it's optional.
    profiler_enabled = config.get('profiler', {}).get('enabled', False)

    # New in 2.0 so it's optional.
    sentry_config = config.get('sentry')

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
        profiler_dir = os.path.abspath(os.path.join(base_dir, config.profiler.profiler_dir))
        parallel_server.on_wsgi_request = ProfileMiddleware(
            parallel_server.on_wsgi_request,
            log_filename = os.path.join(profiler_dir, config.profiler.log_filename),
            cachegrind_filename = os.path.join(profiler_dir, config.profiler.cachegrind_filename),
            discard_first_request = config.profiler.discard_first_request,
            flush_at_shutdown = config.profiler.flush_at_shutdown,
            path = config.profiler.url_path,
            unwind = config.profiler.unwind)

    # New in 2.0 - set environmet variables for servers to inherit
    os_environ = config.get('os_environ', {})
    for key, value in os_environ.items():
        os.environ[key] = value

    # Run the app at last
    if start_gunicorn_app:
        zato_gunicorn_app.run()
    else:
        return zato_gunicorn_app.zato_wsgi_app

def run_in_foreground(base_dir):
    server = run(base_dir, False)
    server.start_server(server)

    return server

if __name__ == '__main__':
    base_dir = sys.argv[1]
    if not os.path.isabs(base_dir):
        base_dir = os.path.abspath(os.path.join(os.getcwd(), base_dir))
    run(base_dir)
