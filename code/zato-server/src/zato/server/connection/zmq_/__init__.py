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
            return self.odb.odb_token == msg['odb_token']
        
        elif msg.action in(DEFINITION.ZMQ_EDIT, DEFINITION.ZMQ_DELETE):
            return self.def_.id == msg.id

    def on_broker_msg_ZMQ_CONNECTOR_CLOSE(self, msg, args=None):
        self._close_delete()

    def on_broker_msg_DEFINITION_ZMQ_DELETE(self, msg, args=None):
        self._close_delete()
