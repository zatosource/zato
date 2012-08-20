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
import logging, os
from threading import Thread

# Pika
from pika import BasicProperties

# Bunch
from bunch import Bunch

# Zato
from zato.common import ConnectionException, PORTS
from zato.common.broker_message import OUTGOING, MESSAGE_TYPE
from zato.common.util import TRACE1
from zato.server.connection.amqp import BaseAMQPConnection, BaseAMQPConnector
from zato.server.connection import setup_logging, start_connector as _start_connector

ENV_ITEM_NAME = 'ZATO_CONNECTOR_AMQP_OUT_ID'

class PublishingConnection(BaseAMQPConnection):
    """ A connection for publishing of the AMQP messages.
    """
    def __init__(self, *args, **kwargs):
        super(PublishingConnection, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        
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
    
    def send(self, msg, out_name, exchange, routing_key, properties={}, *args, **kwargs):
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
        
        self.broker_client.publish(params, msg_type=MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_ALL)
        
    def conn(self):
        """ Returns self. Added to make the facade look like other outgoing
        connection wrappers.
        """
        return self

class OutgoingConnector(BaseAMQPConnector):
    """ An AMQP publishing connector started as a subprocess. Each connection to an AMQP
    broker gets its own connector.
    """
    def __init__(self, repo_location=None, def_id=None, out_id=None, init=True):
        super(OutgoingConnector, self).__init__(repo_location, def_id)
        self.broker_client_id = 'amqp-publishing-connector'
        self.logger = logging.getLogger(self.__class__.__name__)
        self.out_id = out_id
        
        self.broker_callbacks = {
            MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_ANY: self.on_broker_msg,
            MESSAGE_TYPE.TO_AMQP_CONNECTOR_ALL: self.on_broker_msg
        }
        self.broker_messages = (MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_ANY, MESSAGE_TYPE.TO_AMQP_CONNECTOR_ALL)
        
        if init:
            self._init()
            self._setup_amqp()
            
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
        self.out_amqp.sender = None
        
    def _setup_amqp(self):
        """ Sets up the AMQP sender on startup.
        """
        with self.out_amqp_lock:
            with self.def_amqp_lock:
                self._recreate_sender()
                
    def filter(self, msg):
        """ Finds out whether the incoming message actually belongs to the 
        listener. All the listeners receive incoming each of the PUB messages 
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
        
    def _stop_connection(self):
        """ Stops the given outgoing AMQP connection's sender. The method must 
        be called from a method that holds onto all AMQP-related RLocks.
        """
        if self.out_amqp.get('sender') and self.out_amqp.sender.conn and self.out_amqp.sender.conn.is_open:
            self.out_amqp.sender.close()
                            
    def _recreate_sender(self):
        """ (Re-)creates an AMQP sender and updates the related outgoing
        AMQP connection's attributes so that they point to the newly created
        sender. The method must be called from a method that holds
        onto all AMQP-related RLocks.
        """
        self._stop_connection()
            
        vhost = self.def_amqp.virtual_host if 'virtual_host' in self.def_amqp else self.def_amqp.vhost
        if 'credentials' in self.def_amqp:
            username = self.def_amqp.credentials.username
            password = self.def_amqp.credentials.password
        else:
            username = self.def_amqp.username
            password = self.def_amqp.password
        
        conn_params = self._amqp_conn_params()
        
        # Default properties for published messages
        properties = self._amqp_basic_properties(self.out_amqp.content_type, 
            self.out_amqp.content_encoding, self.out_amqp.delivery_mode, self.out_amqp.priority, 
            self.out_amqp.expiration, self.out_amqp.user_id, self.out_amqp.app_id)

        # An actual AMQP sender
        if self.out_amqp.is_active:
            sender = self._sender(conn_params, self.out_amqp.name, properties)
            self.out_amqp.sender = sender
            
    def _sender(self, conn_params, out_name, properties):
        sender = PublishingConnection(conn_params, out_name, properties)
        t = Thread(target=sender._run)
        t.start()
        
        return sender
    
    def _stop_amqp_connection(self):
        """ Stops the AMQP connection.
        """
        if self.out_amqp.sender:
            self.out_amqp.sender.close()
    
    def def_amqp_get(self, id):
        """ Returns the configuration of the AMQP definition of the given name.
        """
        with self.def_amqp_lock:
            return self.def_amqp.get(id)
        
    def _out_amqp_create_edit(self, msg, *args):
        """ Creates or updates an outgoing AMQP connection and its associated
        AMQP sender.
        """ 
        with self.def_amqp_lock:
            with self.out_amqp_lock:
                sender = self.out_amqp.get('sender')
                self.out_amqp = msg
                self.out_amqp.sender = sender
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
            
        self.out_amqp.sender.publish(msg['body'], msg['exchange'], 
                    msg['routing_key'], pika_properties, *msg['args'], **msg['kwargs'])
        

def run_connector():
    """ Invoked on the process startup.
    """
    setup_logging()
    
    repo_location = os.environ['ZATO_REPO_LOCATION']
    def_id = os.environ['ZATO_CONNECTOR_DEF_ID']
    item_id = os.environ[ENV_ITEM_NAME]
    
    connector = OutgoingConnector(repo_location, def_id, item_id)
    
    logger = logging.getLogger(__name__)
    logger.debug('Starting AMQP connector listener, repo_location [{0}], item_id [{1}], def_id [{2}]'.format(
        repo_location, item_id, def_id))
    
def start_connector(repo_location, item_id, def_id):
    _start_connector(repo_location, __file__, ENV_ITEM_NAME, def_id, item_id)
    
if __name__ == '__main__':
    run_connector()
