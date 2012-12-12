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
import logging, os, time
from threading import Thread

# anyjson
from anyjson import dumps, loads

# Bunch
from bunch import Bunch

# Redis
import redis

# Zato
from zato.common import ZATO_NONE
from zato.common.util import new_cid
from zato.common.broker_message import MESSAGE_TYPE, TOPICS

logger = logging.getLogger(__name__)

REMOTE_END_CLOSED_SOCKET = 'Socket closed on remote end'

class _ClientThread(Thread):
    def __init__(self, kvdb, pubsub, name, topic_callbacks=None, on_message=None):
        Thread.__init__(self)
        self.kvdb = kvdb
        self.pubsub = pubsub
        self.topic_callbacks = topic_callbacks
        self.on_message = on_message
        self.client = None
        self.keep_running = ZATO_NONE
        
    def run(self):
        
        # We're in a new thread and we can initialize the KVDB connection now.
        self.kvdb.init()
        self.keep_running = True

        if self.pubsub == 'sub':
            self.client = self.kvdb.pubsub()
            self.client.subscribe(self.topic_callbacks.keys())
            try:
                while self.keep_running:
                    for msg in self.client.listen():
                        self.on_message(Bunch(msg))
            except KeyboardInterrupt:
                self.keep_running = False
            except redis.ConnectionError, e:
                if e.message != REMOTE_END_CLOSED_SOCKET: # Hm, there's no error code, only the message
                    raise
                msg = 'Caught [{}], will quit now'.format(REMOTE_END_CLOSED_SOCKET)
                logger.info(msg)
        else:
            self.client = self.kvdb
            
    def publish(self, topic, msg):
        return self.client.publish(topic, msg)
    
    def close(self):
        self.keep_running = False
        self.client.close()

class BrokerClient(Thread):
    """ Zato broker client. Starts two background threads, one for publishing
    and one for receiving of the messages.
    
    There may be 3 types of messages sent out:
    
    1) to the singleton server
    2) to all the parallel servers
    3) to one of the parallel servers
    
    1) and 2) are straightforward, a message is being published on a topic, 
       off which it is read by broker client(s). 
    
    3) needs more work - the actual message is added to Redis and what is really
       being published is a Redis key it's been stored under. The first client
       to read it will be the one to handle it. 
       
       Yup, it means the messages are sent across to all of the clients
       and the winning one is the one that picked up the Redis message; it's not
       that bad as it may seem, there will be at most as many clients as there 
       are servers in the cluster and truth to be told, Zero MQ < 3.x also would
       do client-side PUB/SUB filtering and it did scale nicely.
    """
    def __init__(self, kvdb, client_type, topic_callbacks):
        Thread.__init__(self)
        self.kvdb = kvdb
        self.decrypt_func = kvdb.decrypt_func
        self.name = '{}-{}'.format(client_type, new_cid())
        self.topic_callbacks = topic_callbacks
        self._to_parallel_any_topic = TOPICS[MESSAGE_TYPE.TO_PARALLEL_ANY]
        
    def run(self):
        logger.info('Starting broker client, host:[{}], port:[{}], name:[{}]'.format(
            self.kvdb.config.host, self.kvdb.config.port, self.name))
        
        self.pub_client = _ClientThread(self.kvdb.copy(), 'pub', self.name)
        self.sub_client = _ClientThread(self.kvdb.copy(), 'sub', self.name, self.topic_callbacks, self.on_message)
        
        self.pub_client.start()
        self.sub_client.start()
        
        for client in(self.pub_client, self.sub_client):
            while client.keep_running == ZATO_NONE:
                time.sleep(0.01)
        
    def publish(self, msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_ALL):
        msg['msg_type'] = msg_type
        topic = TOPICS[msg_type]
        self.pub_client.publish(topic, dumps(msg))
        
    def send(self, msg):
        msg['msg_type'] = MESSAGE_TYPE.TO_PARALLEL_ANY
        msg = dumps(msg)
        
        topic = TOPICS[MESSAGE_TYPE.TO_PARALLEL_ANY]
        key = broker_msg = b'zato:broker:to-parallel:any:{}'.format(new_cid())
        
        self.kvdb.conn.set(key, str(msg))
        self.kvdb.conn.expire(key, 15) # In seconds, TODO: Document it and make configurable
        
        self.pub_client.publish(topic, broker_msg)
        
    def on_message(self, msg):
        if logger.isEnabledFor(logging.DEBUG):
            logger.info('Got broker message:[{}]'.format(msg))
        
        if msg.type == 'message':
    
            # Replace payload with stuff read off the KVDB in case this is where the actual message happens to reside.
            if msg.channel == self._to_parallel_any_topic:
                tmp_key = '{}.tmp'.format(msg.data)
                
                try:
                    self.kvdb.conn.rename(msg.data, tmp_key)
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
                payload = loads(msg.data)
                
            if payload:
                payload = Bunch(payload)
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('Got broker message payload [{}]'.format(payload))
                    
                return self.topic_callbacks[msg.channel](payload)

    def close(self):
        for client in(self.pub_client, self.sub_client):
            client.keep_running = False
            client.kvdb.close()
