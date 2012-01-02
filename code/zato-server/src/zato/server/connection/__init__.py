# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Setting the custom logger must come first
import logging
from zato.server.log import ZatoLogger
logging.setLoggerClass(ZatoLogger)

# stdlib
import errno, os, sys, time
from datetime import datetime
from subprocess import Popen
from threading import RLock
from traceback import format_exc

# psutil
import psutil

# ZeroMQ
import zmq

# Bunch
from bunch import Bunch

# Zato
from zato.broker.zato_client import BrokerClient
from zato.common.util import get_app_context, get_config, get_crypto_manager, TRACE1
from zato.server.base import BaseWorker

class BaseConnection(object):
    """ A base class for connections to any external resourced accessed through
    connectors. Implements the (re-)connection logic and leaves all the particular
    details related to messaging to subclasses.
    """
    def __init__(self):
        self.reconnect_error_numbers = (errno.ENETUNREACH, errno.ENETRESET, errno.ECONNABORTED, 
            errno.ECONNRESET, errno.ETIMEDOUT, errno.ECONNREFUSED, errno.EHOSTUNREACH)
        self.reconnect_exceptions = ()
        self.connection_attempts = 1
        self.first_connection_attempt_time = None
        self.keep_connecting = True
        self.reconnect_sleep_time = 5 # Seconds

    def _start(self):
        """ Actually start a specific resource.
        """ 
        raise NotImplementedError('Must be implemented by a subclass')
    
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
        self.logger.debug(msg)
    
    def _on_connected(self, *ignored_args, **ignored_kwargs):
        """ Invoked after establishing a successful connection to the resource.
        Will report a diagnostic message regarding how many attempts there were
        and how long it took if the connection hadn't been established straightaway.
        """
        if self.connection_attempts > 1:
            delta = datetime.now() - self.first_connection_attempt_time
            msg = '(Re-)connected to {0} after {1} attempt(s), time spent {2}'.format(
                self._conn_info(), self.connection_attempts, delta)
            self.logger.warn(msg)
            
        self.connection_attempts = 1
    
    def start(self):
        """ Start the connection, reconnect on any recoverable errors.
        """ 
        self.first_connection_attempt_time = datetime.now() 
        while self.keep_connecting:
            try:
                
                # Actually try establishing the connection
                self._start()
                
                # Set only if there was an already established connection 
                # and we're now trying to reconnect to the resource.
                self.first_connection_attempt_time = datetime.now()
            except self.reconnect_exceptions, e:
                if self._keep_connecting(e):
                    if isinstance(e, EnvironmentError):
                        err_info = '{0} {1}'.format(e.errno, e.strerror)
                    else:
                        err_info = format_exc(e)
                    msg = 'Caught [{0}] error, will try to (re-)connect to {1} in {2} seconds, {3} attempt(s) so far, time spent {4}'
                    delta = datetime.now() - self.first_connection_attempt_time
                    self.logger.warn(msg.format(err_info, self._conn_info(), self.reconnect_sleep_time, self.connection_attempts, delta))
                    self.connection_attempts += 1
                    time.sleep(self.reconnect_sleep_time)
                else:
                    msg = 'No connection for {0}, e=[{1}]'.format(self._conn_info(), format_exc(e))
                    self.logger.error(msg)
                    raise

class BaseConnector(BaseWorker):
    """ A base class for both channels and outgoing connectors.
    """
    def __init__(self, repo_location, def_id):
        self.repo_location = repo_location
        self.def_id = def_id
        self.odb = None
        self.broker_client_name = None
        
    def _close(self):
        """ Close the process, don't forget about the ODB connection if it exists.
        """
        if self.odb:
            self.odb.close()
        p = psutil.Process(os.getpid())
        p.terminate()
    
    def _setup_odb(self):
        # First let's see if the server we're running on top of exists in the ODB.
        self.server = self.odb.fetch_server()
        if not self.server:
            raise Exception('Server does not exist in the ODB')
        
    def _init(self):
        """ Initializes all the basic run-time data structures and connects
        to the Zato broker.
        """
        
        # Imported here to avoid circular dependencies
        from zato.server.config.app import ZatoContext

        config = get_config(self.repo_location, 'server.conf')
        app_context = get_app_context(config, ZatoContext)
        crypto_manager = get_crypto_manager(self.repo_location, app_context, config)
        
        self.odb = app_context.get_object('odb_manager')
        self.odb.crypto_manager = crypto_manager
        self.odb.odb_data = config['odb']
        
        self._setup_odb()
        
        self.worker_data = Bunch()
        self.worker_data.broker_config = Bunch()
        self.worker_data.broker_config.name = self.broker_client_name
        self.worker_data.broker_config.broker_token = self.server.cluster.broker_token
        self.worker_data.broker_config.zmq_context = zmq.Context()

        broker_push_client_pull = 'tcp://{0}:{1}'.format(self.server.cluster.broker_host, 
            self.server.cluster.broker_start_port + self.broker_push_client_pull_port)
        
        client_push_broker_pull = 'tcp://{0}:{1}'.format(self.server.cluster.broker_host, 
            self.server.cluster.broker_start_port + self.client_push_broker_pull_port)
        
        broker_pub_client_sub = 'tcp://{0}:{1}'.format(self.server.cluster.broker_host, 
            self.server.cluster.broker_start_port + self.broker_pub_client_sub_port)
        
        self.worker_data.broker_config.broker_push_client_pull = broker_push_client_pull
        self.worker_data.broker_config.client_push_broker_pull = client_push_broker_pull
        self.worker_data.broker_config.broker_pub_client_sub = broker_pub_client_sub

        # Connects to the broker
        super(BaseConnector, self)._init()
        
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
    executable = os.path.join(os.path.dirname(sys.executable), 'py')
    
    if file_[-1] in('c', 'o'): # Need to use the source code file
        file_ = file_[:-1]
    
    program = '{0} {1}'.format(executable, file_)
    
    zato_env = {}
    zato_env['ZATO_REPO_LOCATION'] = repo_location
    zato_env['ZATO_CONNECTOR_DEF_ID'] = str(def_id)
    zato_env[env_item_name] = str(item_id)
    
    _env = os.environ
    _env.update(zato_env)
    
    Popen(program, close_fds=True, shell=True, env=_env)