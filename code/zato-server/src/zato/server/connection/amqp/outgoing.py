# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function

# stdlib
import logging, os
from datetime import datetime

# Bunch
from bunch import Bunch

# Kombu
from kombu import Connection
from kombu.pools import producers, reset as reset_pools
from kombu.transport.pyamqp import Transport

# Zato
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING, TOPICS
from zato.common.util import get_component_name, TRACE1
from zato.server.connection.amqp import BaseAMQPConnector
from zato.server.connection import setup_logging, start_connector as _start_connector

ENV_ITEM_NAME = 'ZATO_CONNECTOR_AMQP_OUT_ID'
CONN_TEMPLATE = 'amqp://{username}:{password}@{host}:{port}/{vhost}'
COMPONENT_PREFIX = 'out-amqp'
logger = logging.getLogger(__name__)

class _Transport(Transport):
    """ Allows to pass client properties to the broker.
    TODO: This should be made non-Zato specific and turned into a patch
    to Kombu.
    """
    def establish_connection(self):
        
        conninfo = self.client
        for name, default_value in self.default_connection_params.items():
            if not getattr(conninfo, name, None):
                setattr(conninfo, name, default_value)
        if conninfo.hostname == 'localhost':
            conninfo.hostname = '127.0.0.1'
        conn = self.Connection(host=conninfo.host,
                               userid=conninfo.userid,
                               password=conninfo.password,
                               login_method=conninfo.login_method,
                               virtual_host=conninfo.virtual_host,
                               insist=conninfo.insist,
                               ssl=conninfo.ssl,
                               connect_timeout=conninfo.connect_timeout,
                               heartbeat=conninfo.heartbeat,
                               client_properties={'zato-component':get_component_name(COMPONENT_PREFIX)})
        
        conn.client = self.client
        return conn

class _Connection(Connection):
    """ A connection subclass which uses our own transport class.
    """
    def get_transport_cls(self):
        return _Transport

class PublisherFacade(object):
    """ An AMQP facade for services so they aren't aware that publishing AMQP
    messages actually requires us to use the Zato broker underneath.
    """
    def __init__(self, broker_client, delivery_store):
        self.broker_client = broker_client # A Zato broker client, not the AMQP one.
        self.delivery_store = delivery_store
    
    def send(self, msg, out_name, exchange, routing_key, properties={}, headers={}, *args, **kwargs):
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
        params['headers'] = headers
        params['args'] = args
        params['kwargs'] = kwargs
        
        self.broker_client.publish(params, msg_type=MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_ALL)
        
    def conn(self):
        """ Returns self. Added to make the facade look like other outgoing
        connection wrappers.
        """
        return self

class OutgoingConnector(BaseAMQPConnector):
    """ An AMQP publishing connector started as a subprocess.
    """
    def __init__(self, repo_location=None, def_id=None, out_id=None, init=True):
        super(OutgoingConnector, self).__init__(repo_location, def_id)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.out_id = out_id
        
        self.broker_client_id = 'amqp-publishing-connector'
        self.broker_callbacks = {
            TOPICS[MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_ALL]: self.on_broker_msg,
            TOPICS[MESSAGE_TYPE.TO_AMQP_CONNECTOR_ALL]: self.on_broker_msg
        }
        self.broker_messages = self.broker_callbacks.keys()
        self.component_name = get_component_name('out-amqp')
        
        if init:
            self._init()
        
        self.logger.info('Started an AMQP publisher for [{}]'.format(self._conn_info()))
            
    def _setup_odb(self):
        super(OutgoingConnector, self)._setup_odb()
        
        item = self.odb.get_out_amqp(self.server.cluster.id, self.out_id)
        self.out_amqp = Bunch()
        self.out_amqp.id = item.id
        self.out_amqp.name = item.name
        self.out_amqp.is_active = item.is_active
        self.out_amqp.delivery_mode = item.delivery_mode
        self.out_amqp.priority = item.priority
        self.out_amqp.content_type = item.content_type
        self.out_amqp.content_encoding = item.content_encoding
        self.out_amqp.expiration = item.expiration
        self.out_amqp.user_id = item.user_id
        self.out_amqp.app_id = item.app_id
        self.out_amqp.def_name = item.def_name
        self.out_amqp.def_id = item.def_id
                
    def filter(self, msg):
        """ Finds out whether the incoming message actually belongs to the 
        listener. All the listeners receive each of the incoming PUB messages 
        and filtering out is being performed here, on the client side, not in the broker.
        """
        if super(OutgoingConnector, self).filter(msg):
            return True
        
        elif msg.action == OUTGOING.AMQP_PUBLISH:
            if self.out_amqp.name == msg.out_name:
                return True
        elif msg.action in(OUTGOING.AMQP_EDIT, OUTGOING.AMQP_DELETE):
            if self.out_amqp.id == msg.id:
                return True
        else:
            if self.logger.isEnabledFor(TRACE1):
                self.logger.log(TRACE1, 'Returning False for msg [{0}]'.format(msg))
            return False
    
    def def_amqp_get(self, id):
        """ Returns the configuration of the AMQP definition of the given name.
        """
        with self.def_amqp_lock:
            return self.def_amqp.get(id)
        
    def _out_amqp_create_edit(self, msg, *args):
        """ Creates or updates an outgoing AMQP connection details.
        """ 
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                self.out_amqp = msg
                self._recreate_sender()

    def out_amqp_get(self, name):
        """ Returns the configuration of an outgoing AMQP connection.
        """
        with self.out_amqp_lock:
            if self.out_amqp.is_active:
                return self.out_amqp

    def on_broker_msg_OUTGOING_AMQP_CREATE(self, msg, *args):
        """ Creates a new outgoing AMQP connection. Note that the implementation
        is the same for both OUTGOING_AMQP_CREATE and OUTGOING_AMQP_EDIT.
        """
        self._out_amqp_create_edit(msg, *args)
        
    def on_broker_msg_OUTGOING_AMQP_EDIT(self, msg, *args):
        """ Updates an outgoing AMQP connection. Note that the implementation
        is the same for both OUTGOING_AMQP_CREATE and OUTGOING_AMQP_EDIT.
        """
        self._out_amqp_create_edit(msg, *args)
        
    def on_broker_msg_OUTGOING_AMQP_DELETE(self, msg, *args):
        """ Deletes an outgoing AMQP connection, closes all the other connections
        and stops the process.
        """
        self._close()
                
    def on_broker_msg_OUTGOING_AMQP_PUBLISH(self, msg, *args):
        """ Publishes an AMQP message on the broker.
        """
        properties = {}
        msg_properties = msg['properties']
        
        for name in ('content_type', 'content_encoding', 'delivery_mode', 
                     'priority', 'expiration', 'user_id', 'app_id', 'correlation_id', 'cluster_id'):
            if msg_properties:
                value = msg_properties.get(name) if msg_properties.get(name) else getattr(self.out_amqp, name, None)
            else:
                value = getattr(self.out_amqp, name, None)
            properties[name] = value
       
        headers = msg.get('headers') or {}
        
        if not 'X-Zato-Component' in headers:
            headers['X-Zato-Component'] = self.component_name
            
        if not 'X-Zato-Msg-TS' in headers:
            headers['X-Zato-Msg-TS'] = datetime.utcnow().isoformat()
        
        conn = _Connection(CONN_TEMPLATE.format(**self.def_amqp), heartbeat=self.def_amqp.heartbeat)
        
        with producers[conn].acquire(block=True) as producer:
            producer.publish(msg.body, exchange=msg.exchange, headers=headers, **properties)
        
    def _stop_amqp_connection(self):
        """ Stops any underlying connections.
        """
        reset_pools()
        
    def _recreate_sender(self):
        return self._stop_amqp_connection()

def run_connector():
    """ Invoked on the process startup.
    """
    setup_logging()
    
    repo_location = os.environ['ZATO_REPO_LOCATION']
    def_id = os.environ['ZATO_CONNECTOR_DEF_ID']
    item_id = os.environ[ENV_ITEM_NAME]
    
    OutgoingConnector(repo_location, def_id, item_id)
    
    logger = logging.getLogger(__name__)
    logger.info('Starting AMQP connector, repo_location [{0}], item_id [{1}], def_id [{2}]'.format(
        repo_location, item_id, def_id))
    
def start_connector(repo_location, item_id, def_id):
    _start_connector(repo_location, __file__, ENV_ITEM_NAME, def_id, item_id)
    
if __name__ == '__main__':
    run_connector()
