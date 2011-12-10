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

# Spring Python
from springpython.jms import JMSException
from springpython.jms.factory import WebSphereMQConnectionFactory

# Zato
from zato.common.broker_message import DEFINITION, JMS_WMQ_CONNECTOR
from zato.server.connection import BaseConnection, BaseConnector

class BaseJMSWMQConnection(BaseConnection):
    def __init__(self, factory, name):
        super(BaseJMSWMQConnection, self).__init__()
        self.factory = factory
        self.name = name
        self.reconnect_exceptions = (JMSException, )
        
        # Not everyone uses WebSphere MQ
        from pymqi import MQMIError
        self.MQMIError = MQMIError

    def _start(self):
        self.factory._connect()
        self._on_connected()
        self.keep_connecting = False
        
    def _close(self):
        self.factory.destroy()

    def _conn_info(self):
        return '[{0} ({1})]'.format(self.factory.get_connection_info(), self.name)    
    
    def _keep_connecting(self, exception):
        # Assume we can always deal with JMS exception and network errors
        return isinstance(exception, (JMSException, self.MQMIError)) \
               or (isinstance(exception, EnvironmentError) and exception.errno in self.reconnect_error_numbers)

class BaseJMSWMQConnector(BaseConnector):
    
    def _get_factory(self):
        return WebSphereMQConnectionFactory(
            self.def_.queue_manager,
            str(self.def_.channel),
            str(self.def_.host),
            self.def_.port,
            self.def_.cache_open_send_queues,
            self.def_.cache_open_receive_queues,
            self.def_.use_shared_connections,
            ssl = self.def_.ssl,
            ssl_cipher_spec = str(self.def_.ssl_cipher_spec) if self.def_.ssl_cipher_spec else None,
            ssl_key_repository = str(self.def_.ssl_key_repository) if self.def_.ssl_key_repository else None,
            needs_mcd = self.def_.needs_mcd,
        )
    
    def filter(self, msg):
        """ Can we handle the incoming message?
        """
        if super(BaseJMSWMQConnector, self).filter(msg):
            return True
        
        elif msg.action == JMS_WMQ_CONNECTOR.CLOSE:
            return self.odb.odb_data['token'] == msg['odb_token']
        
        elif msg.action in(DEFINITION.JMS_WMQ_EDIT, DEFINITION.JMS_WMQ_DELETE):
            return self.def_.id == msg.id

    def on_broker_pull_msg_JMS_WMQ_CONNECTOR_CLOSE(self, msg, args=None):
        self._close_delete()

    def on_broker_pull_msg_DEFINITION_JMS_WMQ_DELETE(self, msg, args=None):
        self._close_delete()
