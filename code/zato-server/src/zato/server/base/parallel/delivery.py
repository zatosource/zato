# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import spawn
from gevent.event import Event
from gevent.lock import RLock

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.redis_backend import RedisPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from redis import Redis
    from zato.common.typing_ import anydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_default_delivery_block_ms = 5000
_delivery_batch_size = 50

sub_key_greenlet_dict = dict[str, 'Greenlet']

# ################################################################################################################################
# ################################################################################################################################

class RedisPushDelivery:
    """ Delivers messages from Redis Streams to target services by maintaining
    one blocking greenlet per subscriber key. Each greenlet gets its own dedicated
    Redis connection to avoid connection pool races with BLOCK.
    """

    def __init__(self, server:'ParallelServer', redis_conn_params:'anydict') -> 'None':
        self.server = server
        self._redis_conn_params = redis_conn_params
        self._stop_event = Event()
        self._greenlets:'sub_key_greenlet_dict' = {}
        self._lock = RLock()

# ################################################################################################################################

    def _create_greenlet_backend(self) -> 'RedisPubSubBackend':
        """ Create a dedicated single-connection Redis backend for one greenlet.
        Uses a SingleConnectionPool to guarantee exactly one TCP socket is used,
        preventing BLOCK races with gevent cooperative scheduling.
        """
        from redis import Redis
        from redis.connection import Connection
        from redis.connection import ConnectionPool

        class _SingleConnPool(ConnectionPool):
            """ A connection pool that reuses exactly one connection. """
            def __init__(self, **kwargs):
                super().__init__(max_connections=1, **kwargs)
                self._sole_conn = None
                self._get_count = 0

            def get_connection(self, *args, **kwargs):
                self._get_count += 1
                if self._sole_conn is None:
                    self._sole_conn = super().get_connection(*args, **kwargs)

                return self._sole_conn

            def release(self, connection):
                pass

        pool = _SingleConnPool(**self._redis_conn_params)
        redis_conn = Redis(connection_pool=pool)
        return RedisPubSubBackend(redis_conn)

# ################################################################################################################################

    def start_sub_key(self, sub_key:'str') -> 'None':
        """ Spawn a delivery greenlet for the given subscriber key.
        """
        with self._lock:
            if sub_key not in self._greenlets:
                self._greenlets[sub_key] = spawn(self._delivery_loop, sub_key)

# ################################################################################################################################

    def stop_sub_key(self, sub_key:'str') -> 'None':
        """ Kill the delivery greenlet for the given subscriber key.
        """
        with self._lock:
            if greenlet := self._greenlets.pop(sub_key, None):
                greenlet.kill()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stop all delivery greenlets on server shutdown.
        """
        self._stop_event.set()

        with self._lock:
            for greenlet in self._greenlets.values():
                greenlet.kill()
            self._greenlets.clear()

# ################################################################################################################################

    def _delivery_loop(self, sub_key:'str') -> 'None':
        """ Block on XREADGROUP for one subscriber key until messages arrive
        or the stop event is set. Each greenlet has its own dedicated Redis
        connection to prevent connection pool races with BLOCK.
        """
        # .. create a dedicated backend for this greenlet ..
        backend = self._create_greenlet_backend()

        logger.info('PubSub delivery greenlet started for sub_key `%s`', sub_key)

        while not self._stop_event.is_set():

            # .. exit if this sub_key was removed ..
            if sub_key not in self.server._push_subs:
                break

            try:

                # .. block on Redis until a message arrives (up to configured timeout) ..
                messages = backend.fetch_messages(
                    sub_key, max_messages=_delivery_batch_size, block_ms=_default_delivery_block_ms)

                if not messages:
                    continue

                # .. get the config for this sub_key ..
                config_list = self.server._push_subs[sub_key]

                # .. build a topic_name -> config lookup for routing ..
                config_by_topic:'anydict' = {}

                for config in config_list:
                    topic_name = config['topic_name']
                    config_by_topic[topic_name] = config

                # .. deliver each message to the target service ..
                for message in messages:
                    meta = message['meta']
                    topic_name = meta['topic_name']
                    sub_config = config_by_topic[topic_name]

                    self._deliver_message(message, sub_config)

            except Exception:
                logger.warning('PubSub delivery error for sub_key `%s`: %s', sub_key, format_exc())

        logger.info('PubSub delivery greenlet stopped for sub_key `%s`', sub_key)

# ################################################################################################################################

    def _deliver_message(self, message:'anydict', sub_config:'anydict') -> 'None':
        """ Deliver a single message to the configured target.
        """
        push_type = sub_config['push_type']

        if push_type == PubSub.Push_Type.Service:
            self._deliver_to_service(message, sub_config)

        elif push_type == PubSub.Push_Type.REST:
            self._deliver_to_rest(message, sub_config)

# ################################################################################################################################

    def _deliver_to_service(self, message:'anydict', sub_config:'anydict') -> 'None':
        """ Deliver a message by invoking a Zato service.
        """
        # Zato
        from zato.common.ext.bunch import bunchify

        service_name = sub_config['push_service_name']
        meta = message['meta']

        # .. build a flat dict with meta + data ..
        flat = dict(meta)
        flat['data'] = message['data']

        payload = bunchify(flat)

        self.server.invoke(service_name, payload)

# ################################################################################################################################

    def _deliver_to_rest(self, message:'anydict', sub_config:'anydict') -> 'None':
        """ Deliver a message by posting to a REST endpoint.
        """
        # stdlib
        from json import dumps

        # requests
        from requests import post as requests_post

        url = sub_config['rest_push_url']

        serialized_message = dumps(message)
        _ = requests_post(url, data=serialized_message, headers={'Content-Type': 'application/json'})

# ################################################################################################################################
# ################################################################################################################################
