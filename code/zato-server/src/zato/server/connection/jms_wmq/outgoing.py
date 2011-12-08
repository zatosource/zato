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
from springpython.jms.core import JmsTemplate
from springpython.jms.factory import WebSphereMQConnectionFactory

# Zato
from zato.common import ConnectionException, PORTS
from zato.common.broker_message import OUTGOING, MESSAGE_TYPE
from zato.common.util import TRACE1
from zato.server.connection import BaseConnector
#from zato.server.connection.amqp import BaseConnection, BaseAMQPConnector
from zato.server.connection import setup_logging, start_connector as _start_connector

ENV_ITEM_NAME = 'ZATO_CONNECTOR_JMS_WMQ_OUT_ID'

'''
class PublishingConnection(BaseConnection):
    """ A connection for publishing of the AMQP messages.
    """
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
        
        self.broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_PULL)
'''

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
        
    def _stop_connection(self):
        """ Stops the given outgoing connection's publisher. The method must 
        be called from a method that holds onto all related RLocks.
        """
        if self.out.get('sender') and self.out.sender.get('factory'):
            self.out.sender.factory.destroy()
        
    def _recreate_connection(self):
        self._stop_connection()
        
        import inspect
        print('aaa', inspect.getsourcefile(WebSphereMQConnectionFactory))
       
        self.sender = Bunch()
        self.sender.factory = WebSphereMQConnectionFactory(
            self.def_.queue_manager,
            str(self.def_.channel),
            str(self.def_.host),
            self.def_.port,
            self.def_.cache_open_send_queues,
            self.def_.cache_open_receive_queues,
            self.def_.use_shared_connections,
            ssl = self.def_.ssl,
            ssl_cipher_spec = self.def_.ssl_cipher_spec,
            ssl_key_repository = self.def_.ssl_key_repository,
            needs_mcd = self.def_.needs_mcd,
        )
        
        #self.def_.max_chars_printed = item.max_chars_printed
        
        jms_template = JmsTemplate(self.sender.factory)
        
        jms_template.send('aazaa', 'TEST.1')
        
    def _setup_connector(self):
        """ Sets up the connector on startup.
        """
        with self.out_lock:
            with self.def_lock:
                self._recreate_connection()
        
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
