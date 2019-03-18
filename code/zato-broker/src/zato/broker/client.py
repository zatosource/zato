# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, time
from traceback import format_exc

# anyjson
from anyjson import dumps, loads

# Bunch
from bunch import Bunch

# gevent
from gevent import sleep

# Redis
import redis

# Python 2/3 compatibility
from builtins import bytes

# Zato
from zato.common import BROKER, ZATO_NONE
from zato.common.broker_message import KEYS, MESSAGE_TYPE, TOPICS
from zato.common.kvdb import LuaContainer
from zato.common.util import new_cid, spawn_greenlet

logger = logging.getLogger(__name__)
has_debug = logger.isEnabledFor(logging.DEBUG)

REMOTE_END_CLOSED_SOCKET = 'Socket closed on remote end'
FILE_DESCR_CLOSED_IN_ANOTHER_GREENLET = "Error while reading from socket: (9, 'File descriptor was closed in another greenlet')"

# We use textual messages because some error may have codes whereas different won't.
EXPECTED_CONNECTION_ERRORS = [REMOTE_END_CLOSED_SOCKET, FILE_DESCR_CLOSED_IN_ANOTHER_GREENLET]

NEEDS_TMP_KEY = [v for k,v in TOPICS.items() if k in(
    MESSAGE_TYPE.TO_PARALLEL_ANY,
)]

CODE_RENAMED = 10
CODE_NO_SUCH_FROM_KEY = 11

def BrokerClient(kvdb, client_type, topic_callbacks, _initial_lua_programs):

    # Imported here so it's guaranteed to be monkey-patched using gevent.monkey.patch_all by whoever called us
    from zato.common.py23_ import start_new_thread

    class _ClientThread(object):
        def __init__(self, kvdb, pubsub, name, topic_callbacks=None, on_message=None):
            self.kvdb = kvdb.copy()
            self.kvdb.init()
            self.pubsub = pubsub
            self.topic_callbacks = topic_callbacks
            self.on_message = on_message
            self.client = None
            self.keep_running = ZATO_NONE
            self.connect_sleep_time = 1

        def set_up_pub_sub_client(self):
            try:
                self.kvdb = self.kvdb.copy()
                self.kvdb.init()
                self.kvdb.conn.ping()
                self.client = self.kvdb.pubsub()
                self.client.subscribe(self.topic_callbacks.keys())
            except Exception:
                logger.warn('Redis connection error, will retry after %ss.\n%s', self.connect_sleep_time, format_exc())
                sleep(self.connect_sleep_time)

        def run(self):

            # We're in a new thread and we can initialize the KVDB connection now.
            self.kvdb.init()

            if self.pubsub == 'sub':

                self.set_up_pub_sub_client()
                self.keep_running = True

                try:
                    while self.keep_running:
                        try:
                            for msg in self.client.listen():
                                try:
                                    msg = Bunch(msg)
                                    msg.channel = msg.channel
                                    if isinstance(msg.data, bytes):
                                        msg.data = msg.data
                                    self.on_message(msg)
                                except Exception:
                                    logger.warn('Could not handle broker message `%s`, e:`%s`', msg, format_exc())
                        except redis.ConnectionError as e:
                            if e.message not in EXPECTED_CONNECTION_ERRORS:  # Hm, there's no error code, only the message
                                logger.warn('Caught Redis exception `%s`', e.message)
                                self.set_up_pub_sub_client()
                except KeyboardInterrupt:
                    self.keep_running = False

            else:
                self.client = self.kvdb
                self.keep_running = True

        def publish(self, topic, msg):
            if has_debug:
                logger.debug('Publishing `%r` (%s) to `%s` (%s)', msg, type(msg), topic, self.client)
            return self.client.publish(topic, msg)

        def close(self):
            self.keep_running = False
            self.client.close()

    class _BrokerClient(object):
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
        def __init__(self, kvdb, client_type, topic_callbacks, initial_lua_programs):
            self.kvdb = kvdb
            self.decrypt_func = kvdb.decrypt_func
            self.name = '{}-{}'.format(client_type, new_cid())
            self.topic_callbacks = topic_callbacks
            self.lua_container = LuaContainer(self.kvdb.conn, initial_lua_programs)
            self.ready = False

        def run(self):
            logger.debug('Starting broker client, host:`%s`, port:`%s`, name:`%s`, topics:`%s`',
                self.kvdb.config.host, self.kvdb.config.port, self.name, sorted(self.topic_callbacks))

            self.pub_client = _ClientThread(self.kvdb.copy(), 'pub', self.name)
            self.sub_client = _ClientThread(self.kvdb.copy(), 'sub', self.name, self.topic_callbacks, self.on_message)

            start_new_thread(self.pub_client.run, ())
            start_new_thread(self.sub_client.run, ())

            for client in(self.pub_client, self.sub_client):
                while client.keep_running == ZATO_NONE:
                    time.sleep(0.01)
                self.ready = True

        def publish(self, msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_ALL, *ignored_args, **ignored_kwargs):
            msg['msg_type'] = msg_type
            topic = TOPICS[msg_type]
            msg = dumps(msg)
            self.pub_client.publish(topic, msg)

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
                key = broker_msg = 'zato:broker{}:{}'.format(KEYS[msg_type], new_cid())

                self.kvdb.conn.set(key, str(msg))
                self.kvdb.conn.expire(key, expiration)  # In seconds

                self.pub_client.publish(topic, broker_msg)

        def on_message(self, msg):
            if has_debug:
                logger.warn('Got broker message `%s`', msg)

            if msg.type == 'message':

                # Replace payload with stuff read off the KVDB in case this is where the actual message happens to reside.
                if msg.channel in NEEDS_TMP_KEY:
                    tmp_key = '{}.tmp'.format(msg.data)

                    if self.lua_container.run_lua('zato.rename_if_exists', [msg.data, tmp_key]) == CODE_NO_SUCH_FROM_KEY:
                        payload = None
                    else:
                        payload = self.kvdb.conn.get(tmp_key)
                        self.kvdb.conn.delete(tmp_key)  # Note that it would've expired anyway
                        if not payload:
                            logger.info('No KVDB payload for key `%s` (already expired?)', tmp_key)
                        else:
                            if isinstance(payload, bytes):
                                payload = payload
                            payload = loads(payload)
                else:
                    if isinstance(msg.data, bytes):
                        msg.data = msg.data
                    payload = loads(msg.data)

                if payload:
                    payload = Bunch(payload)
                    if has_debug:
                        logger.debug('Got broker message payload `%s`', payload)

                    callback = self.topic_callbacks[msg.channel]
                    spawn_greenlet(callback, payload)

                else:
                    if has_debug:
                        logger.debug('No payload in msg: `%s`', msg)

        def close(self):
            for client in(self.pub_client, self.sub_client):
                client.keep_running = False
                client.kvdb.close()

    client = _BrokerClient(kvdb, client_type, topic_callbacks, _initial_lua_programs)
    start_new_thread(client.run, ())

    return client
