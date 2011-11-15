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

# stdlib
import errno, logging, socket, time
from datetime import datetime
from multiprocessing import Process
from threading import RLock, Thread

# Pika
from pika import BasicProperties
from pika.adapters import SelectConnection, TornadoConnection
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials

# ZeroMQ
import zmq

# Bunch
from bunch import Bunch

# Zato
from zato.broker.zato_client import BrokerClient
from zato.common import ConnectionException
from zato.common.util import TRACE1
from zato.server.base import BaseWorker

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger(__name__)

class _AMQPPublisher(object):
    def __init__(self, conn_params, def_name, out_name, properties):
        self.conn_params = conn_params
        self.def_name = def_name
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
                if(logger.isEnabledFor(logging.DEBUG)):
                    log_msg = 'AMQP message published [{0}], exchange [{1}], routing key [{2}], publisher ID [{3}]'
                    logger.log(logging.DEBUG, log_msg.format(msg, exchange, routing_key, str(hex(id(self)))))
            else:
                msg = "Can't publish, the connection for {0} is not open".format(self._conn_info())
                logger.error(msg)
                raise ConnectionException(msg)
        else:
            msg = "Can't publish, don't have a channel for {0}".format(self._conn_info())
            logger.error(msg)
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
            logger.warn(msg)
            
        self.connection_attempts = 1
        conn.channel(self._on_channel_open)
        
    def _on_channel_open(self, channel):
        self.channel = channel
        msg = 'Got a channel for {0}'.format(self._conn_info())
        logger.debug(msg)
        
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
                    logger.warn(msg.format(err_info, self._conn_info(), self.reconnect_sleep_time, self.connection_attempts, delta))
                    
                    self.connection_attempts += 1
                    time.sleep(self.reconnect_sleep_time)
                else:
                    msg = 'No connection for {0}, e=[{1}]'.format(self._conn_info(), format_exc(e))
                    logger.error(msg)
                    raise
        
    def close(self):
        if(logger.isEnabledFor(TRACE1)):
            msg = 'About to close the publisher for {0}'.format(self._conn_info())
            logger.log(TRACE1, msg)
            
        self.keep_running = False
        if self.conn:
            self.conn.ioloop.stop()
            self.conn.close()
            
        msg = 'Closed the publisher for {0}'.format(self._conn_info())
        logger.debug(msg)

class AMQPWorker(BaseWorker):
    
    def __init__(self):
        self.def_amqp = {1:Bunch({'name':'zz def', 'id':1, 'host':b'localhost', 'port':5672, 
                                  'vhost':'/zato', 'username':'zato', 'password':'zato', 'heartbeat':10, 
                                  'frame_max':123123})}
        self.out_amqp = {'zz out':Bunch({'def_id':1, 'name': 'zz out', 'publisher':None, 
                                         'content_type':'', 'content_encoding':'',
                                         'delivery_mode':1, 'priority':5, 'expiration':None,
                                         'user_id':None, 'app_id':None, 'is_active':True})}
        self.def_amqp_lock = RLock()
        self.out_amqp_lock = RLock()
        
        self.worker_data = Bunch()
        self.worker_data.broker_config = Bunch()
        self.worker_data.broker_config.broker_token = '4df20cdbc8b142cbb6fc5745ef8e2130'
        self.worker_data.broker_config.zmq_context = zmq.Context()
        self.worker_data.broker_config.broker_push_client_pull = 'tcp://127.0.0.1:5100'
        self.worker_data.broker_config.client_push_broker_pull = 'tcp://127.0.0.1:5101'
        self.worker_data.broker_config.broker_pub_client_sub = 'tcp://127.0.0.1:5102'
        
    def _setup_amqp(self):
        """ Sets up AMQP channels and outgoing connections on startup.
        """
        with self.out_amqp_lock:
            with self.def_amqp_lock:
                for def_id, def_attrs in self.def_amqp.items():
                    for out_name, out_attrs in self.out_amqp.items():
                        if def_id == out_attrs.def_id:
                            logger.error(str(def_id))
                            self._recreate_amqp_publisher(def_id, out_attrs)
                            
    def _stop_amqp_publisher(self, out_name):
        """ Stops the given outgoing AMQP connection's publisher. The method must 
        be called from a method that holds onto all AMQP-related RLocks.
        """
        if self.out_amqp[out_name].publisher:
            self.out_amqp[out_name].publisher.close()
                            
    def _recreate_amqp_publisher(self, def_id, out_attrs):
        """ (Re-)creates an AMQP publisher and updates the related outgoing
        AMQP connection's attributes so that they point to the newly created
        publisher. The method must be called from a method that holds
        onto all AMQP-related RLocks.
        """
        if out_attrs.name in self.out_amqp:
            self._stop_amqp_publisher(out_attrs.name)
            del self.out_amqp[out_attrs.name]
            
        def_attrs = self.def_amqp[def_id]
        
        vhost = def_attrs.virtual_host if 'virtual_host' in def_attrs else def_attrs.vhost
        if 'credentials' in def_attrs:
            username = def_attrs.credentials.username
            password = def_attrs.credentials.password
        else:
            username = def_attrs.username
            password = def_attrs.password
        
        conn_params = self._amqp_conn_params(def_attrs, vhost, username, password, def_attrs.heartbeat)
        
        # Default properties for published messages
        properties = self._amqp_basic_properties(out_attrs.content_type, 
            out_attrs.content_encoding, out_attrs.delivery_mode, out_attrs.priority, 
            out_attrs.expiration, out_attrs.user_id, out_attrs.app_id)

        # An outgoing AMQP connection's properties
        self.out_amqp[out_attrs.name] = out_attrs
        
        # An actual AMQP publisher
        if out_attrs.is_active:
            publisher = self._amqp_publisher(conn_params, def_id, out_attrs.name, properties)
            self.out_amqp[out_attrs.name].publisher = publisher
        
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
    
    def _amqp_publisher(self, conn_params, def_id, out_name, properties):
        publisher = _AMQPPublisher(conn_params, def_id, out_name, properties)
        t = Thread(target=publisher._run)
        #t.daemon = True
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
        self.out_amqp['zz out'].publisher.publish('zzzz', 'zato.direct', '')
        #logger.error(str(333333333333333333333333333333333333333333333333333333333333333333))
        #print(3333333333333333333333333333333333333333333333333333333333333333333333)
        #with self.def_amqp_lock:
        #    msg.host = str(msg.host)
        #    self.def_amqp[msg.id] = msg
        
    def on_broker_pull_msg_DEFINITION_AMQP_EDIT(self, msg, *args):
        """ Updates an existing AMQP definition.
        """
        with self.def_amqp_lock:
            del self.def_amqp[msg.old_name]
            self.def_amqp[msg.id] = msg
        
    def on_broker_pull_msg_DEFINITION_AMQP_DELETE(self, msg, *args):
        """ Deletes an AMQP definition.
        """
        with self.def_amqp_lock:
            del self.def_amqp[msg.id]
            with self.out_amqp_lock:
                for out_name, out_attrs in self.out_amqp.items():
                    if out_attrs.def_id == msg.id:
                        self._stop_amqp_publisher(out_name)
                        del self.out_amqp[out_name]
        
    def on_broker_pull_msg_DEFINITION_AMQP_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of an AMQP definition and of any existing publishers
        using this definition.
        """
        with self.def_amqp_lock:
            self.def_amqp[msg.id]['password'] = msg.password
            with self.out_amqp_lock:
                for out_name, out_attrs in self.out_amqp.items():
                    if out_attrs.def_id == msg.id:
                        self._recreate_amqp_publisher(out_attrs.def_id, out_attrs)
        
    def on_broker_pull_msg_DEFINITION_AMQP_RECONNECT(self, msg, *args):
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                for out_name, out_attrs in self.out_amqp.items():
                    if out_attrs.def_id == msg.id:
                        self._recreate_amqp_publisher(out_attrs.def_id, out_attrs)
                        
    def _out_amqp_create_edit(self, msg, *args):
        """ Creates or updates an outgoing AMQP connection and its associated
        AMQP publisher.
        """ 
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                self._recreate_amqp_publisher(msg.def_id, msg)

    def out_amqp_get(self, name):
        """ Returns the configuration of an outgoing AMQP connection.
        """
        with self.out_amqp_lock:
            item = self.out_amqp.get(name)
            if item and item.is_active:
                return item

    def on_broker_pull_msg_OUTGOING_AMQP_CREATE(self, msg, *args):
        """ Creates a new outgoing AMQP connection. Note that the implementation
        is the same for both OUTGOING_AMQP_CREATE and OUTGOING_AMQP_EDIT.
        """
        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'self.def_amqp is {0}'.format(self.def_amqp))
            
        self._out_amqp_create_edit(msg, *args)
        
    def on_broker_pull_msg_OUTGOING_AMQP_EDIT(self, msg, *args):
        """ Updates an outgoing AMQP connection.
        """
        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'self.def_amqp is {0}'.format(self.def_amqp))
            
        self._out_amqp_create_edit(msg, *args)
        
    def on_broker_pull_msg_OUTGOING_AMQP_DELETE(self, msg, *args):
        """ Deletes an outgoing AMQP connection.
        """
        with self.out_amqp_lock:
            self._stop_amqp_publisher(msg.name)
            del self.out_amqp[msg.name]

def start_amqp_worker():
    worker = AMQPWorker()
    worker._setup_amqp()
    worker._init()
    
if __name__ == '__main__':
    start_amqp_worker()

