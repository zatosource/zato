# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# ZeroMQ
import zmq

# Zato
from zato.common import ZatoException
from zato.common.broker_message import DEFINITION, ZMQ_CONNECTOR
from zato.common.zmq_ import ZMQClient
from zato.server.connection import BaseConnection, BaseConnector

logger = logging.getLogger(__name__)

class BaseZMQConnection(BaseConnection):
    def __init__(self, factory, name):
        super(BaseZMQConnection, self).__init__()
        self.factory = factory
        self.name = name
        self.reconnect_exceptions = ()

    def _start(self):
        self.factory.init()
        self.factory.start()
        self.keep_connecting = False
        
    def _close(self):
        self.factory.close()

    def _conn_info(self):
        return '[{0} ({1})]'.format(self.factory.get_connection_info(), self.name)    

class BaseZMQConnector(BaseConnector):
    
    def __init__(self, *args, **kwargs):
        super(BaseZMQConnector, self).__init__(*args, **kwargs)
        self.socket_type = None
        self.name = None
    
    def _get_factory(self, msg_handler, address, sub_key):

        zmq_client = ZMQClient()
        zmq_client.name = 'zmq-connector-{}'.format(self.name)
        zmq_client.zmq_context = zmq.Context()
        
        if self.socket_type == 'PUSH':
            zmq_client.client_push_broker_pull = address
        elif self.socket_type == 'PULL':
            zmq_client.on_pull_handler = msg_handler
            zmq_client.broker_push_client_pull = address
        elif self.socket_type == 'SUB':
            zmq_client.on_sub_handler = msg_handler
            zmq_client.broker_pub_client_sub = address
            zmq_client.sub_key = zmq.utils.strtypes.asbytes(sub_key)
        else:
            raise ZatoException('Unrecognized socket_type [{0}]'.format(self.socket_type))
        
        return zmq_client
    
    def filter(self, msg):
        """ Can we handle the incoming message?
        """
        if super(BaseZMQConnector, self).filter(msg):
            return True
        
        elif msg.action == ZMQ_CONNECTOR.CLOSE:
            return self.odb.token == msg['token']
        
        elif msg.action in(DEFINITION.ZMQ_EDIT.value, DEFINITION.ZMQ_DELETE.value):
            return self.def_.id == msg.id

    def on_broker_msg_ZMQ_CONNECTOR_CLOSE(self, msg, args=None):
        self._close_delete()

    def on_broker_msg_DEFINITION_ZMQ_DELETE(self, msg, args=None):
        self._close_delete()
