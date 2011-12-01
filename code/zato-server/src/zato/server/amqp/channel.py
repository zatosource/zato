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

# Bunch
from bunch import Bunch

# Zato
from zato.common import ConnectionException
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING
from zato.common.util import TRACE1
from zato.server.amqp import BaseConnection, BaseConnector, setup_logging, start_connector as _start_connector

ENV_ITEM_NAME = 'ZATO_CONNECTOR_AMQP_CHANNEL_ID'

class ConsumingConnection(BaseConnection):
    """ A connection for consuming the AMQP messages.
    """
    def consume(self, queue, consumer_tag_prefix):
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
        
class ConsumingConnector(BaseConnector):
    """ An AMQP consuming connector started as a subprocess. Each connection to an AMQP
    broker gets its own connector.
    """
    def __init__(self, repo_location=None, def_id=None, channel_id=None, init=True):
        super(ConsumingConnector, self).__init__(repo_location, def_id)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.channel_id = channel_id
        
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
        return True
    
        '''
        if super(PublishingConnector, self).filter(msg):
            return True
        
        if msg.action == OUTGOING.AMQP_CLOSE:
            if self.odb.odb_data['token'] == msg['odb_token']:
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
            '''
        
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
        conn_params = self._amqp_conn_params()
        
        # An actual AMQP consumer
        if self.channel_amqp.is_active:
            consumer = self._amqp_consumer(conn_params, self.channel_amqp.name)
            self.out_amqp.publisher = publisher
            
    def _amqp_consumer(self, conn_params, out_name):
        consumer = ConsumingConnection(conn_params, out_name)
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
