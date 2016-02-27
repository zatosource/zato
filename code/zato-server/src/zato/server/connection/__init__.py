# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Setting the custom logger must come first
import logging
from zato.server.log import ZatoLogger
logging.setLoggerClass(ZatoLogger)

# stdlib
import errno, os, time
from copy import deepcopy
from datetime import datetime
from subprocess import Popen
from traceback import format_exc

# Bunch
from bunch import Bunch, bunchify

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
import cloghandler
cloghandler = cloghandler # For pyflakes

# psutil
import psutil

# YAML
import yaml

# Zato
from zato.broker.thread_client import BrokerClient
from zato.common import Inactive, SECRET_SHADOW, TRACE1, ZATO_ODB_POOL_NAME
from zato.common.broker_message import DEFINITION
from zato.common.dispatch import dispatcher
from zato.common.kvdb import KVDB
from zato.common.util import get_app_context, get_config, get_crypto_manager, get_executable, new_cid
from zato.server.base import BrokerMessageReceiver

logger = logging.getLogger(__name__)

# ################################################################################################################################

class BaseConnection(object):
    """ A base class for connections to any external resourced accessed through
    connectors. Implements the (re-)connection logic and leaves all the particular
    details related to messaging to subclasses.
    """
    def __init__(self, kvdb=None, delivery_store=None):
        self.kvdb = kvdb
        self.delivery_store = delivery_store
        self.reconnect_error_numbers = (errno.ENETUNREACH, errno.ENETRESET, errno.ECONNABORTED,
            errno.ECONNRESET, errno.ETIMEDOUT, errno.ECONNREFUSED, errno.EHOSTUNREACH)
        self.reconnect_exceptions = ()
        self.connection_attempts = 1
        self.first_connection_attempt_time = None
        self.keep_connecting = True
        self.reconnect_sleep_time = 5 # Seconds
        self.has_valid_connection = False

    def _start(self):
        """ Actually start a specific resource.
        """
        self.has_valid_connection = True

    def _close(self):
        """ Perform a resource-specific close operation.
        """
        raise NotImplementedError('Must be implemented by a subclass')

    def _conn_info(self):
        """ A textual information regarding the connection for logging purposes.
        """
        raise NotImplementedError('Must be implemented by a subclass')

    def _keep_connecting(self, e):
        """ Invoked on an exception being caught during establishing a connection.
        Receives the exception object and has to answer whether to keep on (re-)connecting.
        """
        raise NotImplementedError('Must be implemented by a subclass')

    def _run(self):
        """ Run the main (re-)connecting loop, close on Ctrl-C.
        """
        try:
            self.start()
        except KeyboardInterrupt:
            self.close()

    def close(self):
        """ Attempt to close the connection to an external resource.
        """
        if(logger.isEnabledFor(TRACE1)):
            msg = 'About to close the connection for {0}'.format(self._conn_info())
            logger.log(TRACE1, msg)

        self.keep_connecting = False
        self._close()

        msg = 'Closed the connection for {0}'.format(self._conn_info())
        logger.info(msg)

    def _on_connected(self, *ignored_args, **ignored_kwargs):
        """ Invoked after establishing a successful connection to the resource.
        Will report a diagnostic message regarding how many attempts there were
        and how long it took if the connection hadn't been established straightaway.
        """
        if self.connection_attempts > 1:
            delta = datetime.utcnow() - self.first_connection_attempt_time
            msg = '(Re-)connected to {0} after {1} attempt(s), time spent {2}'.format(
                self._conn_info(), self.connection_attempts, delta)
            logger.warn(msg)

        if self.has_valid_connection:
            self.connection_attempts = 1

        self.first_connection_attempt_time = datetime.utcnow()

    def start(self):
        """ Start the connection, reconnect on any recoverable errors.
        """
        self.first_connection_attempt_time = datetime.utcnow()
        while self.keep_connecting:
            try:
                # Actually try establishing the connection
                self._start()
            except self.reconnect_exceptions, e:
                if self._keep_connecting(e):
                    if isinstance(e, EnvironmentError):
                        err_info = '{0} {1}'.format(e.errno, e.strerror)
                    else:
                        err_info = format_exc(e)
                    msg = u'Caught [{0}] error, will try to (re-)connect to {1} in {2} seconds, {3} attempt(s) so far, time spent {4}'
                    delta = datetime.utcnow() - self.first_connection_attempt_time
                    logger.warn(msg.format(err_info, self._conn_info(), self.reconnect_sleep_time, self.connection_attempts, delta))
                    self.connection_attempts += 1
                    time.sleep(self.reconnect_sleep_time)
                else:
                    msg = u'No connection for {0}, e:[{1}]'.format(self._conn_info(), format_exc(e))
                    logger.error(msg)
                    raise

# ################################################################################################################################

class BaseConnector(BrokerMessageReceiver):
    """ A base class for both channels and outgoing connectors.
    """
    def __init__(self, repo_location, def_id):
        self.repo_location = repo_location
        self.def_id = def_id
        self.odb = None
        self.odb_config = None
        self.sql_pool_store = None

    def _close(self):
        """ Close the process, don't forget about the ODB connection if it exists.
        """
        if self.odb:
            self.odb.close()
        p = psutil.Process(os.getpid())
        p.terminate()

    def _setup_odb(self):
        # First let's see if the server we're running on top of exists in the ODB.
        self.server = self.odb.fetch_server(self.odb_config)
        if not self.server:
            raise Exception('Server does not exist in the ODB')

    def _init(self):
        """ Initializes all the basic run-time data structures and connects
        to the Zato broker.
        """
        fs_server_config = get_config(self.repo_location, 'server.conf')
        app_context = get_app_context(fs_server_config)
        crypto_manager = get_crypto_manager(self.repo_location, app_context, fs_server_config)

        config_odb = fs_server_config.odb
        self.odb = app_context.get_object('odb_manager')
        self.odb.crypto_manager = crypto_manager
        self.odb.token = fs_server_config.main.token

        # Key-value DB
        self.kvdb = KVDB()
        self.kvdb.config = fs_server_config.kvdb
        self.kvdb.decrypt_func = self.odb.crypto_manager.decrypt
        self.kvdb.init()

        # Broker client
        self.broker_client = BrokerClient(self.kvdb, self.broker_client_id, self.broker_callbacks)
        self.broker_client.start()

        # ODB

        #
        # Ticket #35 Don't ignore odb_port when creating an ODB
        # https://github.com/zatosource/zato/issues/35
        #

        engine = config_odb.engine
        port = config_odb['port']

        self.odb_config = Bunch()
        self.odb_config.db_name = config_odb.db_name
        self.odb_config.is_active = True
        self.odb_config.engine = engine
        self.odb_config.extra = config_odb.extra

        if self.odb_config.engine != 'sqlite':
            self.odb_config.password = self.odb.crypto_manager.decrypt(config_odb.password)
            self.odb_config.host = config_odb.host
            self.odb_config.port = port
            self.odb_config.pool_size = config_odb.pool_size
            self.odb_config.username = config_odb.username

        self.odb_config.is_odb = True

        self.sql_pool_store = app_context.get_object('sql_pool_store')
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.odb_config
        self.odb.pool = self.sql_pool_store[ZATO_ODB_POOL_NAME].pool

        self._setup_odb()

# ################################################################################################################################

def setup_logging():
    logging.addLevelName('TRACE1', TRACE1)
    from logging.config import dictConfig

    with open(os.path.join(os.environ['ZATO_REPO_LOCATION'], 'logging.conf')) as f:
        dictConfig(yaml.load(f))

# ################################################################################################################################

def start_connector(repo_location, file_, env_item_name, def_id, item_id):
    """ Starts a new connector process.
    """

    # Believe it or not but this is the only sane way to make connector subprocesses
    # work as of now (15 XI 2011).

    # Subprocesses spawned in a shell need to use
    # the wrapper which sets up the PYTHONPATH instead of the regular Python
    # executable, because the executable may not have all the dependencies required.
    # Of course, this needs to be squared away before Zato gets into any Linux
    # distribution but then the situation will be much simpler as we simply won't
    # have to patch up anything, the distro will take care of any dependencies.
    executable = get_executable()

    if file_[-1] in('c', 'o'): # Need to use the source code file
        file_ = file_[:-1]

    program = '{0} {1}'.format(executable, file_)

    zato_env = {}
    zato_env['ZATO_REPO_LOCATION'] = repo_location
    if def_id:
        zato_env['ZATO_CONNECTOR_DEF_ID'] = str(def_id)
    zato_env[env_item_name] = str(item_id)

    _env = os.environ
    _env.update(zato_env)

    Popen(program, close_fds=True, shell=True, env=_env)

# ################################################################################################################################

class BasePoolAPI(object):
    """ API for pool-based outgoing connections.
    """
    def __init__(self, conn_store):
        self._conn_store = conn_store

    def __getitem__(self, name):
        item = self._conn_store.get(name)
        if not item:
            msg = 'No such connection `{}` in `{}`'.format(name, sorted(self._conn_store.sessions))
            logger.warn(msg)
            raise KeyError(msg)

        if not item.config.is_active:
            msg = 'Connection `{}` is not active'.format(name)
            logger.warn(msg)
            raise Inactive(msg)

        return item

    get = __getitem__

    def create_def(self, name, msg, on_connection_established_callback=None):
        self._conn_store.create(name, msg, on_connection_established_callback)

    create = create_def

    def edit_def(self, name, msg):
        return self._conn_store.edit(name, msg)

    def delete_def(self, name):
        return self._conn_store.delete(name)

    def change_password_def(self, config):
        return self._conn_store.change_password(config)

# ################################################################################################################################

class BaseConnPoolStore(object):
    """ Base connection store for pool-based outgoing connections.
    """
    conn_name = None
    dispatcher_events = []

    def __init__(self):

        # Import gevent here because connectors may not want to use it
        import gevent
        from gevent.lock import RLock

        self._gevent = gevent
        self._RLock = RLock

        self.sessions = {}
        self.lock = self._RLock()
        self.keep_connecting = set() # IDs of connections to keep connecting for

        # Connects us to interesting events the to-be-established connections need to consult
        dispatcher.listen_for_updates(DEFINITION, self.dispatcher_callback)

        # Maps broker message IDs to their accompanying config
        self.dispatcher_backlog = []

    def __getitem__(self, name):
        return self.sessions[name]

    def get(self, name):
        return self.sessions.get(name)

    def create_session(self, name, config):
        """ Actually adds a new definition, must be called with self.lock held.
        """
        raise NotImplementedError('Must be overridden in subclasses')

    def on_dispatcher_events(self, events):
        """ Handles dispatcher events, by default returns True to indicate that connections should still continue.
        """
        return True

    def check_dispatcher_backlog(self, item):
        events = []

        for event_info in self.dispatcher_backlog:
            if event_info.ctx.id == item.config.id and event_info.event in self.dispatcher_events:
                events.append(bunchify({
                    'item': item,
                    'event_info': event_info
                }))

        if events:
            return self.on_dispatcher_events(events)
        else:
            return True, None

    def _log_connection_error(self, name, config_no_sensitive, e, additional=''):
        logger.warn('Could not connect to %s `%s`, config:`%s`, e:`%s`%s', self.conn_name, name, config_no_sensitive,
            format_exc(e), additional)

    def get_config_no_sensitive(self, config):
        config_no_sensitive = deepcopy(config)
        config_no_sensitive['password'] = SECRET_SHADOW

        return config_no_sensitive

    def _create(self, name, config, on_connection_established_callback=None):
        """ Actually establishes a new connection - the method is called in a new greenlet.
        """
        self.keep_connecting.add(config.id)
        session = None
        config_no_sensitive = self.get_config_no_sensitive(config)
        item = Bunch(config=config, config_no_sensitive=config_no_sensitive, is_connected=False, conn=None)

        try:
            logger.debug('Connecting to `%s`', item.config_no_sensitive)

            while item.config.id in self.keep_connecting:

                # It's possible our configuration has been already updated by users
                # even before we first time established any connection. For instance,
                # connection parameters were invalid and the user updated them.
                # We need to learn of the new config or possibly stop connecting
                # at all if we have been deleted.
                with self.lock:
                    keep_connecting, new_config = self.check_dispatcher_backlog(item)

                if keep_connecting:

                    if new_config:
                        item.config = new_config
                        item.config_no_sensitive = self.get_config_no_sensitive(item.config)

                    try:
                        # Will be overridden in a subclass
                        session = self.create_session(name, item.config, item.config_no_sensitive)
                        self.keep_connecting.remove(item.config.id)
                        logger.info('Connected to %s `%r`', self.conn_name, item.config_no_sensitive)

                    except KeyboardInterrupt:
                        return

                    except Exception, e:
                        self._log_connection_error(name, item.config_no_sensitive, e, ', sleeping for 20 s')
                        self._gevent.sleep(20) # TODO: Should be configurable

        except Exception, e:
            self._log_connection_error(name, item.config_no_sensitive, e)
        else:

            # No session, we give up and quit. This may happen if we have been deleted
            # through a dispatcher event before the session could have been established at all.
            if not session:
                return

            item.conn = session
            item.is_connected = True

            if on_connection_established_callback:
                on_connection_established_callback(item.config)

        self.sessions[name] = item

        return item

    def create(self, name, config, on_connection_established_callback=None):
        """ Adds a new connection definition.
        """
        with self.lock:
            self._gevent.spawn(self._create, name, config, on_connection_established_callback)

    def delete_session(self, name):
        """ Actually deletes a definition. Must be called with self.lock held.
        """
        raise NotImplementedError('Must be overridden in subclasses')

    def delete(self, name):
        """ Deletes an existing connection.
        """
        with self.lock:
            try:
                session = self.sessions[name]
                if session and session.is_connected:
                    self.delete_session(name)

            except Exception, e:
                logger.warn('Error while shutting down session `%s`, e:`%s`', name, format_exc(e))
            finally:
                self.sessions.pop(name, None)

    def edit(self, name, config):
        with self.lock:
            try:
                self.delete_session(name)
            except Exception, e:
                logger.warn('Could not delete session `%s`, config:`%s`, e:`%s`', name, config, format_exc(e))
            else:
                return self._create(config.name, config)

    def change_password(self, password_data):
        with self.lock:
            new_config = deepcopy(self.sessions[password_data.name].config_no_sensitive)
            new_config.password = password_data.password
            return self.edit(password_data.name, new_config)

    def dispatcher_callback(self, event, ctx, **opaque):
        self.dispatcher_backlog.append(bunchify({
            'event_id': new_cid(),
            'event': event,
            'ctx': ctx,
            'opaque': opaque
        }))

# ################################################################################################################################
