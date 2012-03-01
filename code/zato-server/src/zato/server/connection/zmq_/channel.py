# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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

# stdlib
import logging, os
from threading import RLock, Thread

# Bunch
from bunch import Bunch

# Zato
from zato.common import PORTS
from zato.common.broker_message import CHANNEL, MESSAGE_TYPE
from zato.common.util import new_rid
from zato.server.connection import setup_logging, start_connector as _start_connector
from zato.server.connection.zmq_ import BaseZMQConnection, BaseZMQConnector

ENV_ITEM_NAME = 'ZATO_CONNECTOR_ZMQ_CHANNEL_ID'

class ConsumingConnection(BaseZMQConnection):
    def __init__(self, factory, name):
        super(ConsumingConnection, self).__init__(factory, name)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.keep_listening = False
        
    def _close(self):
        self.keep_listening = False
        super(ConsumingConnection, self)._close()
        
    def _on_connected(self):
        super(ConsumingConnection, self)._on_connected()
        
        self.keep_listening = True
        self.logger.debug('Starting listener for [{0}]'.format(self._conn_info()))

class ConsumingConnector(BaseZMQConnector):
    """ An AMQP consuming connector started as a subprocess. Each connection to an AMQP
    broker gets its own connector.
    """
    def __init__(self, repo_location=None, channel_id=None, init=True):
        super(ConsumingConnector, self).__init__(repo_location, None)
        self.broker_client_name = 'zmq-consuming-connector'
        self.logger = logging.getLogger(self.__class__.__name__)
        self.channel_id = channel_id
        
        self.channel_lock = RLock()
        self.channel = Bunch()
        
        self.broker_push_client_pull_port = PORTS.BROKER_PUSH_CONSUMING_CONNECTOR_ZMQ_PULL
        self.client_push_broker_pull_port = PORTS.CONSUMING_CONNECTOR_ZMQ_PUSH_BROKER_PULL
        self.broker_pub_client_sub_port = PORTS.BROKER_PUB_CONSUMING_CONNECTOR_ZMQ_SUB
        
        if init:
            self._init()
            self._setup_connector()
            
    def filter(self, msg):
        """ Can we handle the incoming message?
        """
        if super(ConsumingConnector, self).filter(msg):
            return True
            
        elif msg.action in(CHANNEL.ZMQ_DELETE, CHANNEL.ZMQ_EDIT):
            return self.channel.id == msg['id']
        
    def _setup_odb(self):
        super(ConsumingConnector, self)._setup_odb()
        
        item = self.odb.get_channel_zmq(self.server.cluster.id, self.channel_id)
        self.channel.id = item.id
        self.channel.name = item.name
        self.channel.is_active = item.is_active
        self.channel.address = str(item.address)
        self.channel.socket_type = self.socket_type = item.socket_type
        self.channel.service = item.service_name
        self.channel.sub_key = item.sub_key
        self.channel.listener = None
        
    def _recreate_listener(self):
        self._stop_connection()
        
        if self.channel.is_active:
            factory = self._get_factory(self._on_message, self.channel.address, self.channel.sub_key)
            listener = self._listener(factory)
            self.channel.listener = listener

    def _listener(self, factory):
        """ Starts the listener in a new thread and returns it.
        """
        listener = ConsumingConnection(factory, self.channel.name)
        t = Thread(target=listener._run)
        t.start()
        
        return listener
        
    def _setup_connector(self):
        """ Sets up the connector on startup.
        """
        with self.channel_lock:
            self._recreate_listener()
            
    def _stop_connection(self):
        """ Stops the given channel's listener. The method must be called from 
        a method that holds onto all related RLocks.
        """
        if self.channel.get('listener'):
            listener = self.channel.listener
            listener.close()
            
    def _close_delete(self):
        """ Stops the connections, exits the process.
        """
        with self.channel_lock:
            self._stop_connection()
            self._close()
                
    def _on_message(self, msg, args):
        """ Invoked for each message taken off a ZMQ socket.
        """
        with self.channel_lock:
            params = {}
            params['action'] = CHANNEL.ZMQ_MESSAGE_RECEIVED
            params['service'] = self.channel.service
            params['rid'] = new_rid()
            params['payload'] = msg
            
            self.broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_PARALLEL_PULL)
                
    def on_broker_pull_msg_CHANNEL_ZMQ_DELETE(self, msg, args=None):
        self._close_delete()
        
    def on_broker_pull_msg_CHANNEL_ZMQ_EDIT(self, msg, args=None):
        with self.channel_lock:
            listener = self.channel.listener
            self.channel = msg
            self.channel.listener = listener
            self._recreate_listener()

def run_connector():
    """ Invoked on the process startup.
    """
    setup_logging()
    
    repo_location = os.environ['ZATO_REPO_LOCATION']
    item_id = os.environ[ENV_ITEM_NAME]
    
    connector = ConsumingConnector(repo_location, item_id)
    
    logger = logging.getLogger(__name__)
    logger.debug('Starting ZMQ outgoing, repo_location [{0}], item_id [{1}]'.format(
        repo_location, item_id))
    
def start_connector(repo_location, item_id):
    _start_connector(repo_location, __file__, ENV_ITEM_NAME, None, item_id)
    
if __name__ == '__main__':
    run_connector()
