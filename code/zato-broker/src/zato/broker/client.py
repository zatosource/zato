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
import logging, time
from threading import Thread
from uuid import uuid4

# anyjson
from anyjson import dumps, loads

# Bunch
from bunch import Bunch

# Mosquitto
from mosquitto import Mosquitto

# Redis
import redis

# Zato
from zato.common import ZATO_NONE
from zato.common.util import new_cid, TRACE1
from zato.common.broker_message import MESSAGE_TYPE, TOPICS

logger = logging.getLogger(__name__)

def _mosq_msg_to_dict(msg):
    """ Converts a Mosquitto message to a Python dictionary.
    """
    out = {}
    for name in('timestamp', 'direction', 'state', 'dup', 'mid', 'topic', 'payload', 'qos', 'retain'):
        out[name] = getattr(msg, name, ZATO_NONE)
    return out

class _ClientThread(Thread):
    """ A background thread that will be used either for publishing or receiving
    of MQTT messages.
    """
    def __init__(self, address, pubsub, name, on_message):
        Thread.__init__(self)
        self.address = address
        self.pubsub = pubsub
        self.name = self.client_id = 'zato-{}-{}-{}'.format(self.pubsub, name, uuid4().hex)
        self.on_message = on_message
        self.keep_running = ZATO_NONE
        
    def publish(self, topic, msg):
        return self._client.publish(topic, msg)
    
    def subscribe(self, topic):
        return self._client.subscribe(topic)
        
    def run(self):
        self._client = Mosquitto(self.client_id)
        self._client.connect(self.address)
        self._client.on_message = self.on_message
        
        msg = 'Client [{}] connected to broker [{}]'.format(self.client_id, self.address)
        logger.info(msg)
        
        self.keep_running = True
        
        try:
            while self.keep_running:
                self._client.loop()
        except KeyboardInterrupt:
            self._client.disconnect()
            
    def stop(self):
        self.keep_running = False
    
class BrokerClient(object):
    """ Zato MQTT broker client. Starts two background threads, one for publishing
    and one for receiving of the messages.
    
    There may be 3 types of messages sent out:
    
    1) to the singleton server
    2) to all the parallel servers
    3) to one of the parallel servers
    
    1) and 2) are straightforward, a message is being published on a topic, off which
    it is read by broker client(s). 
    
    3) needs more work - the actual message is added
    to Redis and what is really being published is a Redis key it's been stored under.
    The first client to read it will be the one to handle it. Yup, it means the messages
    are sent across to all of the clients and the winning one is the one that picked
    up the Redis message; it's not that bad as it may seem, there will be at most as
    many clients as there are servers in the cluster and truth to be told, Zero MQ < 3.x
    also would do client-side PUB/SUB filtering and it did scale nicely.
    """
    def __init__(self, kvdb=None, address=None, name=None, callbacks={}):
        self.kvdb = kvdb
        self.address = address
        self.name = name
        self.callbacks = callbacks
        self._pub_client = _ClientThread(self.address, 'pub', self.name, self.on_message)
        self._sub_client = _ClientThread(self.address, 'sub', self.name, self.on_message)
        self._to_parallel_any_topic = TOPICS[MESSAGE_TYPE.TO_PARALLEL_ANY]
        
    def start(self):
        for client in(self._pub_client, self._sub_client):
            client.start()
            while client.keep_running == ZATO_NONE:
                time.sleep(0.01)
        
    def stop(self):
        self._pub_client.stop()
        self._sub_client.stop()

    def on_message(self, client, obj, msg):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('client [{}], obj [{}], msg [{}]'.format(client, obj, _mosq_msg_to_dict(msg)))
        
        # Replace payload with stuff read off the KVDB in case this is where the actual message happens to reside.
        if msg.topic == self._to_parallel_any_topic:
            tmp_key = '{}.tmp'.format(msg.payload)
            
            try:
                self.kvdb.conn.rename(msg.payload, tmp_key)
            except redis.ResponseError, e:
                if e.message != 'ERR no such key': # Doh, I hope Redis guys don't change it out of a sudden :/
                    raise
                else:
                    payload = None
            else:
                payload = self.kvdb.conn.get(tmp_key)
                self.kvdb.conn.delete(tmp_key) # Note that it would've expired anyway
                if not payload:
                    logger.warning('No KVDB payload for key [{}] (already expired?)'.format(tmp_key))
                else:
                    payload = loads(payload)
        else:
            payload = loads(msg.payload)
            
        if payload:
            payload = Bunch(payload)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('Got broker message payload [{}]'.format(payload))
                
            return self.callbacks[payload['msg_type']](payload)
        
    def publish(self, msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_ALL):
        msg['msg_type'] = msg_type
        topic = TOPICS[msg_type]
        self._pub_client.publish(topic, dumps(msg))
        
    def send(self, msg):
        msg['msg_type'] = MESSAGE_TYPE.TO_PARALLEL_ANY
        msg = dumps(msg)
        
        topic = TOPICS[MESSAGE_TYPE.TO_PARALLEL_ANY]
        key = broker_msg = b'zato:broker:to-parallel:any:{}'.format(new_cid())
        
        self.kvdb.conn.set(key, str(msg))
        self.kvdb.conn.expire(key, 5)
        
        self._pub_client.publish(topic, broker_msg)
        
    def subscribe(self, topic):
        self._sub_client.subscribe(topic)        
