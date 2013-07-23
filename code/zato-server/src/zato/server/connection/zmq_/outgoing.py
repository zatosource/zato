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
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING, TOPICS
from zato.common.util import TRACE1
from zato.server.connection import setup_logging, start_connector as _start_connector
from zato.server.connection.zmq_ import BaseZMQConnection, BaseZMQConnector

ENV_ITEM_NAME = 'ZATO_CONNECTOR_ZMQ_OUT_ID'

class ZMQFacade(object):
    """ A ZeroMQ facade for services so they aren't aware that sending ZMQ
    messages actually requires us to use the Zato broker underneath.
    """
    def __init__(self, broker_client, delivery_store):
        self.broker_client = broker_client # A Zato broker client
        self.delivery_store = delivery_store
    
    def send(self, msg, out_name, *args, **kwargs):
        """ Puts a message on a ZeroMQ socket.
        """
        params = {}
        params['action'] = OUTGOING.ZMQ_SEND
        params['name'] = out_name
        params['body'] = msg
        params['args'] = args
        params['kwargs'] = kwargs
        
        self.broker_client.publish(params, msg_type=MESSAGE_TYPE.TO_ZMQ_PUBLISHING_CONNECTOR_ALL)
        
    def conn(self):
        """ Returns self. Added to make the facade look like other outgoing
        connection wrappers.
        """
        return self

class OutgoingConnection(BaseZMQConnection):
    """ An outgoing (PUSH) connection to a ZMQ socket.
    """
    def __init__(self, factory, out_name):
        super(OutgoingConnection, self).__init__(factory, out_name)
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def send(self, msg):
        """ Sends a message to a ZMQ socket.
        """
        self.factory.send(msg)
        if self.logger.isEnabledFor(TRACE1):
            self.logger.log(TRACE1, 'Sent {0} name {1} factory {2}'.format(msg, self.name, self.factory))

class OutgoingConnector(BaseZMQConnector):
    """ An outgoing connector started as a subprocess. Each connection to a queue manager
    gets its own connector.
    """
    def __init__(self, repo_location=None, out_id=None, init=True):
        super(OutgoingConnector, self).__init__(repo_location, None)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.out_id = out_id
        
        self.out_lock = RLock()
        
        self.broker_client_id = 'zmq-outgoing-connector'
        self.broker_callbacks = {
            TOPICS[MESSAGE_TYPE.TO_ZMQ_PUBLISHING_CONNECTOR_ALL]: self.on_broker_msg,
            TOPICS[MESSAGE_TYPE.TO_ZMQ_CONNECTOR_ALL]: self.on_broker_msg
        }
        self.broker_messages = self.broker_callbacks.keys()
        
        if init:
            self._init()
            self._setup_connector()
            
    def _setup_odb(self):
        super(OutgoingConnector, self)._setup_odb()
        
        item = self.odb.get_out_zmq(self.server.cluster.id, self.out_id)
        self.out = Bunch()
        self.out.id = item.id
        self.out.name = item.name
        self.out.is_active = item.is_active
        self.out.address = item.address
        self.out.socket_type = self.socket_type = item.socket_type
        self.out.sender = None
        
    def filter(self, msg):
        """ Can we handle the incoming message?
        """
        if super(OutgoingConnector, self).filter(msg):
            return True

        elif msg.action in(OUTGOING.ZMQ_SEND, OUTGOING.ZMQ_DELETE, OUTGOING.ZMQ_EDIT):
            return self.out.name == msg['name']
        
    def _stop_connection(self):
        """ Stops the given outgoing connection's sender. The method must 
        be called from a method that holds onto all related RLocks.
        """
        if self.out.get('sender'):
            sender = self.out.sender
            sender.close()
        
    def _recreate_sender(self):
        self._stop_connection()
        self.name = self.out.name
        
        if self.out.get('is_active'):
            factory = self._get_factory(None, self.out.address, None)
            sender = self._sender(factory)
            self.out.sender = sender

    def _sender(self, factory):
        """ Starts the outgoing connection in a new thread and returns it.
        """
        sender = OutgoingConnection(factory, self.out.name)
        t = Thread(target=sender._run)
        t.start()
        
        return sender
        
    def _setup_connector(self):
        """ Sets up the connector on startup.
        """
        with self.out_lock:
            self._recreate_sender()
                
    def _close_delete(self):
        """ Stops the connections, exits the process.
        """
        with self.out_lock:
            self._stop_connection()
            self._close()

    def on_broker_msg_OUTGOING_ZMQ_SEND(self, msg, args=None):
        """ Puts a message on a socket.
        """
        if not self.out.get('is_active'):
            log_msg = 'Not sending, the connection is not active [{0}]'.format(self.out.toDict())
            self.logger.info(log_msg)
            return
            
        if self.out.get('sender'):
            self.out.sender.send(msg.body)
        else:
            if self.logger.isEnabledFor(logging.DEBUG):
                log_msg = 'No sender for [{0}]'.format(self.out.toDict())
                self.logger.debug(log_msg)
                
    def on_broker_msg_OUTGOING_ZMQ_DELETE(self, msg, args=None):
        self._close_delete()
        
    def on_broker_msg_OUTGOING_ZMQ_EDIT(self, msg, args=None):
        with self.out_lock:
            sender = self.out.get('sender')
            self.out = msg
            self.out.sender = sender
            self._recreate_sender()

def run_connector():
    """ Invoked on the process startup.
    """
    setup_logging()
    
    repo_location = os.environ['ZATO_REPO_LOCATION']
    item_id = os.environ[ENV_ITEM_NAME]
    
    OutgoingConnector(repo_location, item_id)
    
    logger = logging.getLogger(__name__)
    logger.debug('Starting ZeroMQ outgoing, repo_location [{0}], item_id [{1}]'.format(
        repo_location, item_id))
    
def start_connector(repo_location, item_id):
    _start_connector(repo_location, __file__, ENV_ITEM_NAME, None, item_id)
    
if __name__ == '__main__':
    run_connector()
