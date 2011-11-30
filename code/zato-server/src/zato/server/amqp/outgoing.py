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
import errno, logging, os, socket, sys, time
from datetime import datetime
from multiprocessing import Process
from threading import RLock, Thread
from traceback import format_exc

# Pika
from pika.adapters import TornadoConnection

# Bunch
from bunch import Bunch

# Zato
from zato.common.broker_message import DEFINITION, MESSAGE_TYPE, OUTGOING
from zato.common.util import TRACE1
from zato.server.amqp import BaseConnector, start_connector as _start_connector

class _AMQPPublisher(object):
    """ An object which does an actual job of publishing the AMQP message on the broker.
    """
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
        
class PublisherFacade(object):
    """ An AMQP facade for services so they aren't aware that publishing AMQP
    messages actually requires us to use the Zato broker underneath.
    """
    def __init__(self, broker_client):
        self.broker_client = broker_client # A Zato broker client, not the AMQP one.
    
    def publish(self, msg, out_name, exchange, routing_key, properties={}, *args, **kwargs):
        """ Publishes the message on the Zato broker which forwards it to one of the
        AMQP connectors.
        """
        params = {}
        params['action'] = OUTGOING.AMQP_PUBLISH
        params['out_name'] = out_name
        params['body'] = msg
        params['exchange'] = bytes(exchange)
        params['routing_key'] = bytes(routing_key)
        params['properties'] = properties
        params['args'] = args
        params['kwargs'] = kwargs
        
        self.broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_AMQP_CONNECTOR_PULL)

class PublishingConnector(BaseConnector):
    """ An AMQP connector started as a subprocess. Each connection to an AMQP
    broker gets its own connector.
    """
    def __init__(self, repo_location=None, out_id=None, def_id=None, init=True):
        super(PublishingConnector, self).__init__(repo_location, def_id)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.out_id = out_id
        
        if init:
            self._init()
            self._setup_amqp()
        
    def _setup_amqp(self):
        """ Sets up the AMQP publisher on startup.
        """
        with self.out_amqp_lock:
            with self.def_amqp_lock:
                self._recreate_amqp_publisher()
                
    def filter(self, msg):
        """ Finds out whether the incoming message actually belongs to the 
        listener. All the listeners receive incoming each of the PUB messages 
        and filtering out is being performed here, on the client side, not in the broker.
        """
        if msg.action == OUTGOING.AMQP_CLOSE:
            if self.odb.odb_data['token'] == msg['odb_token']:
                return True
        elif msg.action == OUTGOING.AMQP_PUBLISH:
            if self.out_amqp.name == msg.out_name:
                return True
        elif msg.action in(OUTGOING.AMQP_EDIT, OUTGOING.AMQP_DELETE):
            if self.out_amqp.id == msg.id:
                return True
        elif msg.action in(DEFINITION.AMQP_EDIT, DEFINITION.AMQP_DELETE, DEFINITION.AMQP_CHANGE_PASSWORD):
            if self.def_amqp.id == msg.id:
                return True
        else:
            if self.logger.isEnabledFor(TRACE1):
                self.logger.log(TRACE1, 'Returning False for msg [{0}]'.format(msg))
            return False
        
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
        """ Deletes an outgoing AMQP connection, closes all the other connections
        and stops the process.
        """
        self._close()
                
    def on_broker_pull_msg_OUTGOING_AMQP_PUBLISH(self, msg, *args):
        """ Publishes an AMQP message on the broker.
        """
        properties = {}
        msg_properties = msg['properties']
        property_names = ('content_type', 'content_encoding', 'delivery_mode', 
                          'priority', 'expiration', 'user_id', 'app_id', 
                          'correlation_id', 'cluster_id')

        for name in property_names:
            if msg['properties']:
                value = msg_properties.get(name) if msg_properties.get(name) else getattr(self.out_amqp, name, None)
            else:
                value = getattr(self.out_amqp, name, None)
            properties[name] = value
                
        # Now that we've collected all the properties we need to build a pika-specific
        # structure out of them.
        
        pika_properties = BasicProperties()
        for name, value in properties.items():
            setattr(pika_properties, name, value)
            
        self.out_amqp.publisher.publish(msg['body'], msg['exchange'], 
                    msg['routing_key'], pika_properties, *msg['args'], **msg['kwargs'])
        
    def on_broker_pull_msg_OUTGOING_AMQP_CLOSE(self, msg, *args):
        """ Stops the publisher, ODB connection and exits the process.
        """
        self._close()


def run_connector():
    """ Invoked on the process startup.
    """
    logging.addLevelName('TRACE1', TRACE1)
    from logging import config
    config.fileConfig(os.path.join(os.environ['ZATO_REPO_LOCATION'], 'logging.conf'))
    
    repo_location = os.environ['ZATO_REPO_LOCATION']
    out_id = os.environ['ZATO_CONNECTOR_AMQP_OUT_ID']
    def_id = os.environ['ZATO_CONNECTOR_AMQP_DEF_ID']
    
    connector = PublishingConnector(repo_location, out_id, def_id)
    
    logger = logging.getLogger(__name__)
    logger.debug('Starting AMQP connector listener, repo_location [{0}], out_id [{1}], def_id [{2}]'.format(
        repo_location, out_id, def_id))
    
def start_connector(repo_location, out_id, def_id):
    _start_connector(repo_location, __file__, out_id, def_id)
    
if __name__ == '__main__':
    run_connector()
