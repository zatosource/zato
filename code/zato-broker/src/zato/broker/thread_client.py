# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, time
from threading import Thread
from traceback import format_exc

# anyjson
from anyjson import dumps, loads

# Bunch
from bunch import Bunch

# Redis
import redis

# Zato
from zato.common import BROKER, TRACE1, ZATO_NONE
from zato.common.broker_message import KEYS, MESSAGE_TYPE, TOPICS
from zato.common.util import new_cid

logger = logging.getLogger(__name__)

REMOTE_END_CLOSED_SOCKET = 'Socket closed on remote end'
NEEDS_TMP_KEY = [v for k,v in TOPICS.items() if k in(
    MESSAGE_TYPE.TO_PARALLEL_ANY,
)]

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
                try:
                    while self.keep_running:
                        for msg in self.client.listen():
                            self.on_message(Bunch(msg))
                except redis.ConnectionError as e:
                    if e.message != REMOTE_END_CLOSED_SOCKET:  # Hm, there's no error code, only the message
                        logger.info('Caught `%s`, will quit now', e.message)
                        raise
            except KeyboardInterrupt:
                self.keep_running = False

        else:
            self.client = self.kvdb

    def publish(self, topic, msg):
        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'Publishing [{}] to [{}]'.format(msg, topic))
        return self.client.publish(topic, msg)

    def close(self):
        self.keep_running = False
        self.client.close()

class BrokerClient(Thread):
    """ Zato broker client. Starts two background threads, one for publishing
    and one for receiving of the messages.

    There may be 3 types of messages sent out:

    1) to the singleton server
    2) to all the servers/connectors/all connectors of a certain type (e.g. only AMQP ones)
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

    def run(self):
        logger.info('Starting broker client, host:[{}], port:[{}], name:[{}], topics:[{}]'.format(
            self.kvdb.config.host, self.kvdb.config.port, self.name, sorted(self.topic_callbacks)))

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

    def invoke_async(self, msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_ANY, expiration=BROKER.DEFAULT_EXPIRATION):
        msg['msg_type'] = msg_type

        try:
            msg = dumps(msg)
        except Exception:
            error_msg = 'JSON serialization failed for msg:`%r`, e:`%s`'
            logger.error(error_msg, msg, format_exc())
            raise
        else:
            topic = TOPICS[msg_type]
            key = broker_msg = b'zato:broker{}:{}'.format(KEYS[msg_type], new_cid())

            self.kvdb.conn.set(key, str(msg))
            self.kvdb.conn.expire(key, expiration)  # In seconds

            self.pub_client.publish(topic, broker_msg)

    def on_message(self, msg):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Got broker message:[{}]'.format(msg))

        if msg.type == 'message':

            # Replace payload with stuff read off the KVDB in case this is where the actual message happens to reside.
            if msg.channel in NEEDS_TMP_KEY:
                tmp_key = '{}.tmp'.format(msg.data)

                try:
                    self.kvdb.conn.rename(msg.data, tmp_key)
                except redis.ResponseError as e:
                    if e.message != 'ERR no such key':  # Doh, I hope Redis guys don't change it out of a sudden :/
                        raise
                    else:
                        payload = None
                else:
                    payload = self.kvdb.conn.get(tmp_key)
                    self.kvdb.conn.delete(tmp_key)  # Note that it would've expired anyway
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

            else:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('No payload in msg:[{}]'.format(msg))

    def close(self):
        for client in(self.pub_client, self.sub_client):
            client.keep_running = False
            client.kvdb.close()
