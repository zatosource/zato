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
from datetime import datetime
from subprocess import Popen
from traceback import format_exc

# psutil
import psutil

# Bunch
from bunch import Bunch

# Zato
from zato.broker.thread_client import BrokerClient
from zato.common import ZATO_ODB_POOL_NAME
from zato.common.delivery import DeliveryStore
from zato.common.kvdb import KVDB
from zato.common.util import get_app_context, get_config, get_crypto_manager, get_executable, TRACE1
from zato.server.base import BrokerMessageReceiver

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
        if(self.logger.isEnabledFor(TRACE1)):
            msg = 'About to close the connection for {0}'.format(self._conn_info())
            self.logger.log(TRACE1, msg)
            
        self.keep_connecting = False
        self._close()
            
        msg = 'Closed the connection for {0}'.format(self._conn_info())
        self.logger.info(msg)
    
    def _on_connected(self, *ignored_args, **ignored_kwargs):
        """ Invoked after establishing a successful connection to the resource.
        Will report a diagnostic message regarding how many attempts there were
        and how long it took if the connection hadn't been established straightaway.
        """
        if self.connection_attempts > 1:
            delta = datetime.utcnow() - self.first_connection_attempt_time
            msg = '(Re-)connected to {0} after {1} attempt(s), time spent {2}'.format(
                self._conn_info(), self.connection_attempts, delta)
            self.logger.warn(msg)
            
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
                    self.logger.warn(msg.format(err_info, self._conn_info(), self.reconnect_sleep_time, self.connection_attempts, delta))
                    self.connection_attempts += 1
                    time.sleep(self.reconnect_sleep_time)
                else:
                    msg = u'No connection for {0}, e:[{1}]'.format(self._conn_info(), format_exc(e))
                    self.logger.error(msg)
                    raise

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
        port = config_odb.get('port')
        
        if not port:
            port = 5432 if engine == 'postgresql' else 1521
        
        self.odb_config = Bunch()
        self.odb_config.db_name = config_odb.db_name
        self.odb_config.is_active = True
        self.odb_config.engine = engine
        self.odb_config.extra = config_odb.extra
        self.odb_config.host = config_odb.host
        self.odb_config.port = port
        self.odb_config.password = self.odb.crypto_manager.decrypt(config_odb.password)
        self.odb_config.pool_size = config_odb.pool_size
        self.odb_config.username = config_odb.username
        
        self.odb_config.is_odb = True
        
        self.sql_pool_store = app_context.get_object('sql_pool_store')
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.odb_config
        self.odb.pool = self.sql_pool_store[ZATO_ODB_POOL_NAME].pool
        
        self._setup_odb()
        
        # Delivery store
        self.delivery_store = DeliveryStore(self.kvdb, self.broker_client, self.odb, float(fs_server_config.misc.delivery_lock_timeout))
        
def setup_logging():
    logging.addLevelName('TRACE1', TRACE1)
    from logging import config
    config.fileConfig(os.path.join(os.environ['ZATO_REPO_LOCATION'], 'logging.conf'))

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
