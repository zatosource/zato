# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, os
from threading import RLock, Thread

# Bunch
from bunch import Bunch

# Zato
from zato.common.broker_message import CHANNEL, MESSAGE_TYPE, TOPICS
from zato.common.util import new_cid
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
        self.logger = logging.getLogger(self.__class__.__name__)
        self.channel_id = channel_id
        self.name = None
        
        self.channel_lock = RLock()
        self.channel = Bunch()
        
        self.broker_client_id = 'zmq-consuming-connector'
        self.broker_callbacks = {
            TOPICS[MESSAGE_TYPE.TO_ZMQ_CONSUMING_CONNECTOR_ALL]: self.on_broker_msg,
            TOPICS[MESSAGE_TYPE.TO_ZMQ_CONNECTOR_ALL]: self.on_broker_msg
        }
        self.broker_messages = self.broker_callbacks.keys()
        
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
        self.channel.sub_key = item.sub_key or ''
        self.channel.data_format = item.data_format
        self.channel.listener = None
        
    def _recreate_listener(self):
        self._stop_connection()
        self.name = self.channel.name
        
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
            params['cid'] = new_cid()
            params['payload'] = msg
            params['data_format'] = self.channel.data_format
            
            self.broker_client.invoke_async(params)
                
    def on_broker_msg_CHANNEL_ZMQ_DELETE(self, msg, args=None):
        self._close_delete()
        
    def on_broker_msg_CHANNEL_ZMQ_EDIT(self, msg, args=None):
        with self.channel_lock:
            listener = self.channel.listener
            
            service_name = self.channel.service
            self.channel = msg
            self.channel.service = service_name
            
            self.socket_type = self.channel.socket_type
            self.channel.sub_key = msg.sub_key or ''
            self.channel.listener = listener
            self._recreate_listener()

def run_connector():
    """ Invoked on the process startup.
    """
    setup_logging()
    
    repo_location = os.environ['ZATO_REPO_LOCATION']
    item_id = os.environ[ENV_ITEM_NAME]
    
    ConsumingConnector(repo_location, item_id)
    
    logger = logging.getLogger(__name__)
    logger.debug('Starting ZMQ outgoing, repo_location [{0}], item_id [{1}]'.format(
        repo_location, item_id))
    
def start_connector(repo_location, item_id):
    _start_connector(repo_location, __file__, ENV_ITEM_NAME, None, item_id)
    
if __name__ == '__main__':
    run_connector()
