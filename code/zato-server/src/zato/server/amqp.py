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

from __future__ import absolute_import, division, print_function

# Setting the custom logger must come first
import logging
from zato.server.log import ZatoLogger
logging.setLoggerClass(ZatoLogger)

# stdlib
import errno, logging, os, socket, sys, time
from datetime import datetime
from multiprocessing import Process
from subprocess import Popen
from threading import RLock, Thread
from traceback import format_exc

# Pika
from pika import BasicProperties
from pika.adapters import TornadoConnection, SelectConnection
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials

# ZeroMQ
import zmq

# Bunch
from bunch import Bunch

# Zato
from zato.broker.zato_client import BrokerClient
from zato.common import ConnectionException, PORTS, ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.util import get_app_context, get_config, get_crypto_manager, TRACE1
from zato.server.base import BaseWorker

class _AMQPPublisher(object):
    def __init__(self, conn_params, out_name, properties):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.conn_params = conn_params
        self.out_name = out_name
        self.properties = properties
        self.conn = None
        self.channel = None
        self.connection_attempts = 1
        self.first_connection_attempt_time = None
        self.keep_running = True
        self.reconnect_sleep_time = 5 # Seconds
        self.reconnect_error_numbers = (errno.ENETUNREACH, errno.ENETRESET, errno.ECONNABORTED, 
            errno.ECONNRESET, errno.ETIMEDOUT, errno.ECONNREFUSED, errno.EHOSTUNREACH)
        
    def _conn_info(self):
        return '{0}:{1}{2} ({3})'.format(self.conn_params.host, 
            self.conn_params.port, self.conn_params.virtual_host, self.out_name)
        
    def publish(self, msg, exchange, routing_key, properties=None, *args, **kwargs):
        if self.channel:
            if self.conn.is_open:
                properties = properties if properties else self.properties
                self.channel.basic_publish(exchange, routing_key, msg, properties, *args, **kwargs)
                if(self.logger.isEnabledFor(logging.DEBUG)):
                    log_msg = 'AMQP message published [{0}], exchange [{1}], routing key [{2}], publisher ID [{3}]'
                    self.logger.log(logging.DEBUG, log_msg.format(msg, exchange, routing_key, str(hex(id(self)))))
            else:
                msg = "Can't publish, the connection for {0} is not open".format(self._conn_info())
                self.logger.error(msg)
                raise ConnectionException(msg)
        else:
            msg = "Can't publish, don't have a channel for {0}".format(self._conn_info())
            self.logger.error(msg)
            raise ConnectionException(msg)
        
    def _on_connected(self, conn):
        """ Invoked after establishing a successful connection to an AMQP broker.
        Will report a diagnostic message regarding how many attempts there were
        and how long it took if the connection hasn't been established straightaway.
        """
        
        if self.connection_attempts > 1:
            delta = datetime.now() - self.first_connection_attempt_time
            msg = '(Re-)connected to {0} after {1} attempt(s), time spent {2}'.format(
                self._conn_info(), self.connection_attempts, delta)
            self.logger.warn(msg)
            
        self.connection_attempts = 1
        conn.channel(self._on_channel_open)
        
    def _on_channel_open(self, channel):
        self.channel = channel
        msg = 'Got a channel for {0}'.format(self._conn_info())
        self.logger.debug(msg)
        
    def _run(self):
        try:
            self.start()
        except KeyboardInterrupt:
            self.close()
            
    def _start(self):
        self.conn = TornadoConnection(self.conn_params, self._on_connected)
        self.conn.ioloop.start()
        
    def start(self):
        
        # Set right after the publisher has been created
        self.first_connection_attempt_time = datetime.now() 
        
        while self.keep_running:
            try:
                
                # Actually try establishing the connection
                self._start()
                
                # Set only if there was an already established connection 
                # and we're now trying to reconnect to the broker.
                self.first_connection_attempt_time = datetime.now()
            except(TypeError, EnvironmentError), e:
                # We need to catch TypeError because pika will sometimes erroneously raise
                # it in self._start's self.conn.ioloop.start()
                if isinstance(e, TypeError) or e.errno in self.reconnect_error_numbers:
                    if isinstance(e, TypeError):
                        err_info = format_exc(e)
                    else:
                        err_info = '{0} {1}'.format(e.errno, e.strerror)
                    msg = 'Caught [{0}] error, will try to (re-)connect to {1} in {2} seconds, {3} attempt(s) so far, time spent {4}'
                    delta = datetime.now() - self.first_connection_attempt_time
                    self.logger.warn(msg.format(err_info, self._conn_info(), self.reconnect_sleep_time, self.connection_attempts, delta))
                    self.connection_attempts += 1
                    time.sleep(self.reconnect_sleep_time)
                else:
                    msg = 'No connection for {0}, e=[{1}]'.format(self._conn_info(), format_exc(e))
                    self.logger.error(msg)
                    raise
        
    def close(self):
        if(self.logger.isEnabledFor(TRACE1)):
            msg = 'About to close the publisher for {0}'.format(self._conn_info())
            self.logger.log(TRACE1, msg)
            
        self.keep_running = False
        if self.conn:
            self.conn.close()
            
        msg = 'Closed the publisher for {0}'.format(self._conn_info())
        self.logger.debug(msg)

class ConnectorAMQP(BaseWorker):
    """ An AMQP connector started as a subprocess. Each connection to an AMQP
    connector gets its own connector.
    """
    def __init__(self, repo_location=None, out_id=None, def_id=None, init=True):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.repo_location = repo_location
        self.out_id = out_id
        self.def_id = def_id
        self.odb = None
        
        if init:
            self._init()
        
    def _init(self):
        """ Initializes all the run-time data structures, fetches configuration,
        connects to the ODB and the AMQP broker.
        """
        
        # Imported here to avoid circular dependencies
        from zato.server.config.app import ZatoContext

        config = get_config(self.repo_location, 'server.conf')
        app_context = get_app_context(config, ZatoContext)
        crypto_manager = get_crypto_manager(self.repo_location, app_context, config)
        
        self.odb = app_context.get_object('odb_manager')
        self.odb.crypto_manager = crypto_manager
        self.odb.odb_data = config['odb']
        
        self.def_amqp = Bunch()
        self.out_amqp = Bunch()
        
        self.def_amqp_lock = RLock()
        self.out_amqp_lock = RLock()
        
        self._setup_odb()
        self._setup_amqp()
        
        self.worker_data = Bunch()
        self.worker_data.broker_config = Bunch()
        self.worker_data.broker_config.name = 'amqp-connector'
        self.worker_data.broker_config.broker_token = self.server.cluster.broker_token
        self.worker_data.broker_config.zmq_context = zmq.Context()

        broker_push_client_pull = 'tcp://{0}:{1}'.format(self.server.cluster.broker_host, 
            self.server.cluster.broker_start_port + PORTS.BROKER_PUSH_CONNECTOR_AMQP_PULL)
        
        client_push_broker_pull = 'tcp://{0}:{1}'.format(self.server.cluster.broker_host, 
            self.server.cluster.broker_start_port + PORTS.CONNECTOR_AMQP_PUSH_BROKER_PULL)
        
        broker_pub_client_sub = 'tcp://{0}:{1}'.format(self.server.cluster.broker_host, 
            self.server.cluster.broker_start_port + PORTS.BROKER_PUB_CONNECTOR_AMQP_SUB)
        
        self.worker_data.broker_config.broker_push_client_pull = broker_push_client_pull
        self.worker_data.broker_config.client_push_broker_pull = client_push_broker_pull
        self.worker_data.broker_config.broker_pub_client_sub = broker_pub_client_sub

        # Connects to the broker
        super(ConnectorAMQP, self)._init()
        
    def _setup_odb(self):
        
        # First let's see if the server we're running on top of exists in the ODB.
        self.server = self.odb.fetch_server()
        if not self.server:
            raise Exception('Server does not exist in the ODB')

        item = self.odb.get_def_amqp(self.server.cluster.id, self.def_id)
        self.def_amqp = Bunch()
        self.def_amqp.name = item.name
        self.def_amqp.id = item.id
        self.def_amqp.host = str(item.host)
        self.def_amqp.port = item.port
        self.def_amqp.vhost = item.vhost
        self.def_amqp.username = item.username
        self.def_amqp.password = item.password
        self.def_amqp.heartbeat = item.heartbeat
        self.def_amqp.frame_max = item.frame_max
        
        item = self.odb.get_out_amqp(self.server.cluster.id, self.out_id)
        self.out_amqp = Bunch()
        self.out_amqp.id = item.id
        self.out_amqp.name = item.name
        self.out_amqp.is_active = item.is_active
        self.out_amqp.delivery_mode = item.delivery_mode
        self.out_amqp.priority = item.priority
        self.out_amqp.content_type = item.content_type
        self.out_amqp.content_encoding = item.content_encoding
        self.out_amqp.expiration = item.expiration
        self.out_amqp.user_id = item.user_id
        self.out_amqp.app_id = item.app_id
        self.out_amqp.def_name = item.def_name
        self.out_amqp.def_id = item.def_id
        self.out_amqp.publisher = None
            
    def _setup_amqp(self):
        """ Sets up AMQP channels and outgoing connections on startup.
        """
        with self.out_amqp_lock:
            with self.def_amqp_lock:
                self._recreate_amqp_publisher()
                            
    def _stop_amqp_publisher(self):
        """ Stops the given outgoing AMQP connection's publisher. The method must 
        be called from a method that holds onto all AMQP-related RLocks.
        """
        if self.out_amqp.get('publisher') and self.out_amqp.publisher.conn and self.out_amqp.publisher.conn.is_open:
            self.out_amqp.publisher.close()
                            
    def _recreate_amqp_publisher(self):
        """ (Re-)creates an AMQP publisher and updates the related outgoing
        AMQP connection's attributes so that they point to the newly created
        publisher. The method must be called from a method that holds
        onto all AMQP-related RLocks.
        """
        self._stop_amqp_publisher()
            
        vhost = self.def_amqp.virtual_host if 'virtual_host' in self.def_amqp else self.def_amqp.vhost
        if 'credentials' in self.def_amqp:
            username = self.def_amqp.credentials.username
            password = self.def_amqp.credentials.password
        else:
            username = self.def_amqp.username
            password = self.def_amqp.password
        
        conn_params = self._amqp_conn_params(self.def_amqp, vhost, username, password, self.def_amqp.heartbeat)
        
        # Default properties for published messages
        properties = self._amqp_basic_properties(self.out_amqp.content_type, 
            self.out_amqp.content_encoding, self.out_amqp.delivery_mode, self.out_amqp.priority, 
            self.out_amqp.expiration, self.out_amqp.user_id, self.out_amqp.app_id)

        # An actual AMQP publisher
        if self.out_amqp.is_active:
            publisher = self._amqp_publisher(conn_params, self.out_amqp.name, properties)
            self.out_amqp.publisher = publisher
            
    def _amqp_conn_params(self, def_attrs, vhost, username, password, heartbeat):
        params = ConnectionParameters(def_attrs.host, def_attrs.port, vhost, 
            PlainCredentials(username, password),
            frame_max=def_attrs.frame_max)
        
        # heartbeat is an integer but ConnectionParameter.__init__ insists it
        # be a boolean.
        params.heartbeat = heartbeat
        
        return params

    def _amqp_basic_properties(self, content_type, content_encoding, delivery_mode, priority, expiration, user_id, app_id):
        return BasicProperties(content_type=content_type, content_encoding=content_encoding, 
            delivery_mode=delivery_mode, priority=priority, expiration=expiration, 
            user_id=user_id, app_id=app_id)

    def _amqp_basic_properties_from_attrs(self, out_attrs):
        return self._amqp_basic_properties(out_attrs.content_type, out_attrs.content_encoding, 
            out_attrs.delivery_mode, out_attrs.priority, out_attrs.expiration, 
            out_attrs.user_id, out_attrs.app_id)
    
    def _amqp_publisher(self, conn_params, out_name, properties):
        publisher = _AMQPPublisher(conn_params, out_name, properties)
        t = Thread(target=publisher._run)
        t.start()
        
        return publisher
    
    def def_amqp_get(self, id):
        """ Returns the configuration of the AMQP definition of the given name.
        """
        with self.def_amqp_lock:
            return self.def_amqp.get(id)
        
    def on_broker_pull_msg_DEFINITION_AMQP_CREATE(self, msg, *args):
        """ Creates a new AMQP definition.
        """
        with self.def_amqp_lock:
            msg.host = str(msg.host)
            self.def_amqp[msg.id] = msg
        
    def on_broker_pull_msg_DEFINITION_AMQP_EDIT(self, msg, *args):
        """ Updates an existing AMQP definition.
        """
        with self.def_amqp_lock:
            
            password = self.def_amqp.password
            self.def_amqp = msg
            self.def_amqp.password = password
            self.def_amqp.host = str(self.def_amqp.host)
            
            with self.out_amqp_lock:
                self._recreate_amqp_publisher()
                if self.logger.isEnabledFor(TRACE1):
                    log_msg = 'self.def_amqp [{0}]'.format(self.def_amqp)
                    self.logger.log(TRACE1, log_msg)
        
    def on_broker_pull_msg_DEFINITION_AMQP_DELETE(self, msg, *args):
        """ Deletes an AMQP definition.
        """
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                self._stop_amqp_publisher()
        
    def on_broker_pull_msg_DEFINITION_AMQP_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of an AMQP definition and of any existing publishers
        using this definition.
        """
        with self.def_amqp_lock:
            self.def_amqp['password'] = msg.password
            with self.out_amqp_lock:
                self._recreate_amqp_publisher()
        
    def on_broker_pull_msg_DEFINITION_AMQP_RECONNECT(self, msg, *args):
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                for out_name, out_attrs in self.out_amqp.items():
                    if out_attrs.def_id == msg.id:
                        self._recreate_amqp_publisher()
                        
    def _out_amqp_create_edit(self, msg, *args):
        """ Creates or updates an outgoing AMQP connection and its associated
        AMQP publisher.
        """ 
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                publisher = self.out_amqp.get('publisher')
                self.out_amqp = msg
                self.out_amqp.publisher = publisher
                self._recreate_amqp_publisher()

    def out_amqp_get(self, name):
        """ Returns the configuration of an outgoing AMQP connection.
        """
        with self.out_amqp_lock:
            if self.out_amqp.is_active:
                return self.out_amqp

    def on_broker_pull_msg_OUTGOING_AMQP_CREATE(self, msg, *args):
        """ Creates a new outgoing AMQP connection. Note that the implementation
        is the same for both OUTGOING_AMQP_CREATE and OUTGOING_AMQP_EDIT.
        """
        self._out_amqp_create_edit(msg, *args)
        
    def on_broker_pull_msg_OUTGOING_AMQP_EDIT(self, msg, *args):
        """ Updates an outgoing AMQP connection. Note that the implementation
        is the same for both OUTGOING_AMQP_CREATE and OUTGOING_AMQP_EDIT.
        """
        self._out_amqp_create_edit(msg, *args)
        
    def on_broker_pull_msg_OUTGOING_AMQP_DELETE(self, msg, *args):
        """ Deletes an outgoing AMQP connection.
        """
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                self._stop_amqp_publisher()

def run_connector():
    """ Invoked on the process startup.
    """
    logging.addLevelName('TRACE1', TRACE1)
    from logging import config
    config.fileConfig(os.path.join(os.environ['ZATO_REPO_LOCATION'], 'logging.conf'))
    
    repo_location = os.environ['ZATO_REPO_LOCATION']
    out_id = os.environ['ZATO_CONNECTOR_AMQP_OUT_ID']
    def_id = os.environ['ZATO_CONNECTOR_AMQP_DEF_ID']
    
    connector = ConnectorAMQP(repo_location, out_id, def_id)
    
    logger = logging.getLogger(__name__)
    logger.debug('Starting AMQP connector listener, repo_location [{0}], out_id [{1}], def_id [{2}]'.format(
        repo_location, out_id, def_id))
    
def start_connector_listener(repo_location, out_id, def_id):
    """ Starts a new connector process.
    """
    
    # Believe it or not but this is the only sane way to make AMQP subprocesses 
    # work as of now (15 XI 2011).
    
    # Subprocesses spawned in a shell need to use
    # the wrapper which sets up the PYTHONPATH instead of the regular Python
    # executable, because the executable may not have all the dependencies required.
    # Of course, this needs to be squared away before Zato gets into any Linux 
    # distribution but then the situation will be much simpler as we simply won't 
    # have to patch up anything, the distro will take care of any dependencies.
    executable = os.path.join(os.path.dirname(sys.executable), 'py')
    
    amqp_file = __file__
    if amqp_file[-1] in('c', 'o'): # Need to use the source code file
        amqp_file = amqp_file[:-1]
    
    program = '{0} {1}'.format(executable, amqp_file)
    
    zato_env = {}
    zato_env['ZATO_REPO_LOCATION'] = repo_location
    zato_env['ZATO_CONNECTOR_AMQP_OUT_ID'] = str(out_id)
    zato_env['ZATO_CONNECTOR_AMQP_DEF_ID'] = str(def_id)
    
    _env = os.environ
    _env.update(zato_env)
    
    Popen(program, close_fds=True, shell=True, env=_env)
    
if __name__ == '__main__':
    run_connector()