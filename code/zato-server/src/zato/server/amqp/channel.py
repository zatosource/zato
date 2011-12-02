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
from random import getrandbits
from os import getpid
from socket import getfqdn, gethostbyname, gethostname
from threading import RLock, Thread

# Bunch
from bunch import Bunch

# Zato
from zato.common import ConnectionException, PORTS
from zato.common.broker_message import MESSAGE_TYPE, CHANNEL
from zato.common.util import TRACE1
from zato.server.amqp import BaseConnection, BaseConnector, setup_logging, start_connector as _start_connector

ENV_ITEM_NAME = 'ZATO_CONNECTOR_AMQP_CHANNEL_ID'

class ConsumingConnection(BaseConnection):
    """ A connection for consuming the AMQP messages.
    """
    def __init__(self, conn_params, channel_name, queue, consumer_tag_prefix):
        super(ConsumingConnection, self).__init__(conn_params, channel_name)
        self.queue = queue
        self.consumer_tag_prefix = consumer_tag_prefix
        
    def _on_channel_open(self, channel):
        super(ConsumingConnection, self)._on_channel_open(channel)
        self.consume()
        
    def _on_basic_consume(self, channel, method_frame, header_frame, body):
        print("Basic.Deliver %s delivery-tag %i: %s" % (header_frame.content_type, method_frame.delivery_tag, body))
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        
    def consume(self, queue=None, consumer_tag_prefix=None):
        _queue = queue if queue else self.queue
        _consumer_tag_prefix = consumer_tag_prefix if consumer_tag_prefix else self.consumer_tag_prefix
        
        consumer_tag = '{0}:{1}:{2}:{3}:{4}'.format(
            _consumer_tag_prefix, gethostbyname(gethostname()), getfqdn(),
            getpid(), getrandbits(64)).ljust(72, '0')
        
        self.channel.basic_consume(self._on_basic_consume, queue=_queue, consumer_tag=consumer_tag)
        self.logger.debug('Started a consumer for [{0}], queue [{1}], tag [{2}]'.format(
            self._conn_info(), queue, consumer_tag))
        
        
class ConsumingConnector(BaseConnector):
    """ An AMQP consuming connector started as a subprocess. Each connection to an AMQP
    broker gets its own connector.
    """
    def __init__(self, repo_location=None, def_id=None, channel_id=None, init=True):
        super(ConsumingConnector, self).__init__(repo_location, def_id)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.channel_id = channel_id
        
        self.broker_push_client_pull_port = PORTS.BROKER_PUSH_CONSUMING_CONNECTOR_AMQP_PULL
        self.client_push_broker_pull_port = PORTS.CONSUMING_CONNECTOR_AMQP_PUSH_BROKER_PULL
        self.broker_pub_client_sub_port = PORTS.BROKER_PUB_CONSUMING_CONNECTOR_AMQP_SUB
        
        if init:
            self._init()
            self._setup_amqp()
            
    def _setup_odb(self):
        super(ConsumingConnector, self)._setup_odb()
        
        item = self.odb.get_channel_amqp(self.server.cluster.id, self.channel_id)
        self.channel_amqp = Bunch()
        self.channel_amqp.id = item.id
        self.channel_amqp.name = item.name
        self.channel_amqp.is_active = item.is_active
        self.channel_amqp.queue = item.queue
        self.channel_amqp.consumer_tag_prefix = item.consumer_tag_prefix
        
    def _setup_amqp(self):
        """ Sets up the AMQP listener on startup.
        """
        with self.out_amqp_lock:
            with self.def_amqp_lock:
                self._recreate_amqp_consumer()
                
    def filter(self, msg):
        """ Finds out whether the incoming message actually belongs to the 
        listener. All the listeners receive incoming each of the PUB messages 
        and filtering out is being performed here, on the client side, not in the broker.
        """
        if super(PublishingConnector, self).filter(msg):
            return True
        
        if msg.action == CHANNEL.AMQP_CLOSE:
            if self.odb.odb_data['token'] == msg['odb_token']:
                return True
        elif msg.action in(CHANNEL.AMQP_EDIT, CHANNEL.AMQP_DELETE):
            if self.channel_amqp.id == msg.id:
                return True
        else:
            if self.logger.isEnabledFor(TRACE1):
                self.logger.log(TRACE1, 'Returning False for msg [{0}]'.format(msg))
            return False
        
    def _stop_amqp_consumer(self):
        """ Stops the given AMQP consumer. The method must be called from a method 
        that holds onto all AMQP-related RLocks.
        """
        if self.channel_amqp.get('consumer') and self.channel_amqp.consumer.conn and self.channel_amqp.consumer.conn.is_open:
            self.channel_amqp.consumer.close()
                            
    def _recreate_amqp_consumer(self):
        """ (Re-)creates an AMQP consumer and updates the related attributes so 
        that they point to the newly created consumer. The method must be called 
        from a method that holds onto all AMQP-related RLocks.
        """
        self._stop_amqp_consumer()
        
        # An actual AMQP consumer
        if self.channel_amqp.is_active:
            consumer = self._amqp_consumer()
            self.out_amqp.consumer = consumer
            
    def _amqp_consumer(self):
        consumer = ConsumingConnection(self._amqp_conn_params(), self.channel_amqp.name,
            self.channel_amqp.queue, self.channel_amqp.consumer_tag_prefix)
        t = Thread(target=consumer._run)
        t.start()
        
        return consumer
        
    def _out_amqp_create_edit(self, msg, *args):
        """ Creates or updates an outgoing AMQP connection and its associated
        AMQP consumer.
        """ 
        with self.def_amqp_lock:
            with self.channel_amqp_lock:
                consumer = self.channel_amqp.get('consumer')
                self.channel_amqp = msg
                self.channel_amqp.consumer = consumer
                self._recreate_amqp_consumer()

    def on_broker_pull_msg_CHANNEL_AMQP_CREATE(self, msg, *args):
        """ Creates a new outgoing AMQP connection. Note that the implementation
        is the same for both OUTGOING_AMQP_CREATE and OUTGOING_AMQP_EDIT.
        """
        self._channel_amqp_create_edit(msg, *args)
        
    def on_broker_pull_msg_CHANNEL_AMQP_EDIT(self, msg, *args):
        """ Updates an AMQP consumer. Note that the implementation
        is the same for both CHANNEL_AMQP_CREATE and CHANNEL_AMQP_EDIT.
        """
        self._channel_amqp_create_edit(msg, *args)
        
    def on_broker_pull_msg_CHANNEL_AMQP_DELETE(self, msg, *args):
        """ Deletes an AMQP connection, closes all the other connections
        and stops the process.
        """
        self._close()
        
    def on_broker_pull_msg_CHANNEL_AMQP_CLOSE(self, msg, *args):
        """ Stops the consumer, ODB connection and exits the process.
        """
        self._close()


def run_connector():
    """ Invoked on the process startup.
    """
    setup_logging()
    
    repo_location = os.environ['ZATO_REPO_LOCATION']
    def_id = os.environ['ZATO_CONNECTOR_AMQP_DEF_ID']
    item_id = os.environ[ENV_ITEM_NAME]
    
    connector = ConsumingConnector(repo_location, def_id, item_id)
    
    logger = logging.getLogger(__name__)
    logger.debug('Starting AMQP consuming connector, repo_location [{0}], item_id [{1}], def_id [{2}]'.format(
        repo_location, item_id, def_id))
    
def start_connector(repo_location, item_id, def_id):
    _start_connector(repo_location, __file__, ENV_ITEM_NAME, def_id, item_id)
    
if __name__ == '__main__':
    run_connector()
