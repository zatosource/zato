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
import errno, logging, os, socket, sys
from multiprocessing import Process
from threading import RLock, Thread

# Pika
from pika import BasicProperties

# Bunch
from bunch import Bunch

# Spring Python
from springpython.jms import JMSException
from springpython.jms.core import JmsTemplate, TextMessage
from springpython.jms.factory import WebSphereMQConnectionFactory

# Zato
from zato.common import ConnectionException, PORTS
from zato.common.broker_message import DEFINITION, JMS_WMQ_CONNECTOR, MESSAGE_TYPE, OUTGOING
from zato.common.util import TRACE1
from zato.server.connection import BaseConnection, BaseConnector
from zato.server.connection import setup_logging, start_connector as _start_connector

ENV_ITEM_NAME = 'ZATO_CONNECTOR_JMS_WMQ_OUT_ID'

class WMQFacade(object):
    """ A WebSphere MQ facade for services so they aren't aware that sending WMQ
    messages actually requires us to use the Zato broker underneath.
    """
    def __init__(self, broker_client):
        self.broker_client = broker_client # A Zato broker client
    
    def put(self, msg, out_name, queue, delivery_mode=None, expiration=None, priority=None, max_chars_printed=None, 
            *args, **kwargs):
        """ Puts a message on a WebSphere MQ queue.
        """
        params = {}
        params['action'] = OUTGOING.JMS_WMQ_SEND
        params['name'] = out_name
        params['body'] = msg
        params['queue'] = queue
        params['delivery_mode'] = delivery_mode
        params['expiration'] = expiration
        params['priority'] = priority
        params['max_chars_printed'] = max_chars_printed
        params['args'] = args
        params['kwargs'] = kwargs
        
        self.broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_JMS_WMQ_PUBLISHING_CONNECTOR_PULL)

class OutgoingConnection(BaseConnection):
    def __init__(self, factory, out_name):
        super(OutgoingConnection, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.factory = factory
        self.jms_template = JmsTemplate(self.factory)
        self.out_name = out_name
        self.reconnect_exceptions = (JMSException, )
        
        # Not everyone uses WebSphere MQ
        from pymqi import MQMIError
        self.MQMIError = MQMIError
        
    def send(self, msg, default_delivery_mode, default_expiration, default_priority, default_max_chars_printed):
        jms_msg = TextMessage()
        jms_msg.text = msg.get('body')
        jms_msg.jms_correlation_id = msg.get('jms_correlation_id')
        jms_msg.jms_delivery_mode = msg.get('jms_delivery_mode') or default_delivery_mode
        jms_msg.jms_destination = msg.get('jms_destination')
        jms_msg.jms_expiration = msg.get('jms_expiration') or default_expiration
        jms_msg.jms_message_id = msg.get('jms_message_id')
        jms_msg.jms_priority = msg.get('jms_priority') or default_priority
        jms_msg.jms_redelivered = msg.get('jms_redelivered')
        jms_msg.jms_timestamp = msg.get('jms_timestamp')
        jms_msg.max_chars_printed = msg.get('max_chars_printed') or default_max_chars_printed
        
        queue = str(msg['queue'])
        
        try:
            self.jms_template.send(jms_msg, queue)
        except Exception, e:
            if self._keep_connecting(e):
                self.close()
                self.keep_connecting = True
                self.factory._disconnecting = False
                self.start()
            else:
                raise
        
    def _start(self):
        self.factory._connect()
        self._on_connected()
        self.keep_connecting = False
        
    def _close(self):
        self.factory.destroy()

    def _keep_connecting(self, exception):
        # Assume we can always deal with JMS exception and network errors
        return isinstance(exception, (JMSException, self.MQMIError)) \
               or (isinstance(exception, EnvironmentError) and exception.errno in self.reconnect_error_numbers)

    def _conn_info(self):
        return '[{0} ({1})]'.format(self.factory.get_connection_info(), self.out_name)

class OutgoingConnector(BaseConnector):
    """ An AMQP publishing connector started as a subprocess. Each connection to an AMQP
    broker gets its own connector.
    """
    def __init__(self, repo_location=None, def_id=None, out_id=None, init=True):
        super(OutgoingConnector, self).__init__(repo_location, def_id)
        self.broker_client_name = 'jms-wmq-outgoing-connector'
        self.logger = logging.getLogger(self.__class__.__name__)
        self.out_id = out_id
        
        self.out_lock = RLock()
        self.def_lock = RLock()
        
        self.broker_push_client_pull_port = PORTS.BROKER_PUSH_PUBLISHING_CONNECTOR_JMS_WMQ_PULL
        self.client_push_broker_pull_port = PORTS.PUBLISHING_CONNECTOR_JMS_WMQ_PUSH_BROKER_PULL
        self.broker_pub_client_sub_port = PORTS.BROKER_PUB_PUBLISHING_CONNECTOR_JMS_WMQ_SUB
        
        if init:
            self._init()
            self._setup_connector()
            
    def _setup_odb(self):
        super(OutgoingConnector, self)._setup_odb()
        
        item = self.odb.get_def_jms_wmq(self.server.cluster.id, self.def_id)
        self.def_ = Bunch()
        self.def_.name = item.name
        self.def_.id = item.id
        self.def_.host = item.host
        self.def_.port = item.port
        self.def_.queue_manager = item.queue_manager
        self.def_.channel = item.channel
        self.def_.cache_open_send_queues = item.cache_open_send_queues
        self.def_.cache_open_receive_queues = item.cache_open_receive_queues
        self.def_.use_shared_connections = item.use_shared_connections
        self.def_.ssl = item.ssl
        self.def_.ssl_cipher_spec = item.ssl_cipher_spec
        self.def_.ssl_key_repository = item.ssl_key_repository
        self.def_.needs_mcd = item.needs_mcd
        self.def_.max_chars_printed = item.max_chars_printed
        
        item = self.odb.get_out_jms_wmq(self.server.cluster.id, self.out_id)
        self.out = Bunch()
        self.out.id = item.id
        self.out.name = item.name
        self.out.is_active = item.is_active
        self.out.delivery_mode = item.delivery_mode
        self.out.priority = item.priority
        self.out.expiration = item.expiration
        self.out.sender = None
        
    def filter(self, msg):
        """ Can we handle the incoming message?
        """
        
        if super(OutgoingConnector, self).filter(msg):
            return True
        
        elif msg.action == JMS_WMQ_CONNECTOR.CLOSE:
            return self.odb.odb_data['token'] == msg['odb_token']
            
        elif msg.action in(OUTGOING.JMS_WMQ_SEND, OUTGOING.JMS_WMQ_DELETE, OUTGOING.JMS_WMQ_EDIT):
            return self.out.name == msg['name']
        
        elif msg.action in(DEFINITION.JMS_WMQ_EDIT, DEFINITION.JMS_WMQ_DELETE):
            return self.def_.id == msg.id
        
    def _stop_connection(self):
        """ Stops the given outgoing connection's publisher. The method must 
        be called from a method that holds onto all related RLocks.
        """
        if self.out.get('sender'):
            sender = self.out.sender
            self.out.clear()
            sender.close()
        
    def _recreate_sender(self):
        self._stop_connection()
        
        if self.out.is_active:
            
            factory = WebSphereMQConnectionFactory(
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
            with self.def_lock:
                self._recreate_sender()
                
    def _close_delete(self):
        """ Stops the connections, exits the process.
        """
        with self.def_lock:
            with self.out_lock:
                self._stop_connection()
                self._close()
                
    def on_broker_pull_msg_JMS_WMQ_CONNECTOR_CLOSE(self, msg, args=None):
        self._close_delete()
                
    def on_broker_pull_msg_DEFINITION_JMS_WMQ_EDIT(self, msg, args=None):
        with self.def_lock:
            with self.out_lock:
                self.def_ = msg
                self._recreate_sender()
                
    def on_broker_pull_msg_DEFINITION_JMS_WMQ_DELETE(self, msg, args=None):
        self._close_delete()

    def on_broker_pull_msg_OUTGOING_JMS_WMQ_SEND(self, msg, args=None):
        """ Puts a message on a queue.
        """
        if not self.out.get('is_active'):
            log_msg = 'Not sending, the connection is not active [{0}]'.format(self.out)
            self.logger.info(log_msg)
            return
            
        if self.out.get('sender'):
            if self.out.get('sender').factory._is_connected:
                self.out.sender.send(msg, self.out.delivery_mode, self.out.expiration, 
                    self.out.priority, self.def_.max_chars_printed)
            else:
                if self.logger.isEnabledFor(logging.DEBUG):
                    log_msg = 'Not sending, the factory for [{0}] is not connected'.format(self.out)
                    self.logger.debug(log_msg)
        else:
            if self.logger.isEnabledFor(TRACE1):
                log_msg = 'No sender for [{0}]'.format(self.out)
                self.logger.log(TRACE1, log_msg)
                
    def on_broker_pull_msg_OUTGOING_JMS_WMQ_DELETE(self, msg, args=None):
        self._close_delete()
        
    def on_broker_pull_msg_OUTGOING_JMS_WMQ_EDIT(self, msg, args=None):
        with self.def_lock:
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
    def_id = os.environ['ZATO_CONNECTOR_DEF_ID']
    item_id = os.environ[ENV_ITEM_NAME]
    
    connector = OutgoingConnector(repo_location, def_id, item_id)
    
    logger = logging.getLogger(__name__)
    logger.debug('Starting JMS WebSphere MQ outgoing, repo_location [{0}], item_id [{1}], def_id [{2}]'.format(
        repo_location, item_id, def_id))
    
def start_connector(repo_location, item_id, def_id):
    _start_connector(repo_location, __file__, ENV_ITEM_NAME, def_id, item_id)
    
if __name__ == '__main__':
    run_connector()
