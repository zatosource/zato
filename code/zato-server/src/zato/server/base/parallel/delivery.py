# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger
from math import log2
from random import uniform
from time import monotonic
from traceback import format_exc

# gevent
from gevent import sleep, spawn
from gevent.event import Event
from gevent.lock import RLock

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.redis_backend import RedisPubSubBackend
from zato.common.util.api import utcnow

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

_max_retry_time = PubSub.Delivery.Max_Retry_Time
_retry_interval_initial = PubSub.Delivery.Retry_Interval_Initial
_retry_interval_max = PubSub.Delivery.Retry_Interval_Max
_retry_jitter_percent = PubSub.Delivery.Retry_Jitter_Percent

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

        out = RedisPubSubBackend(redis_conn, self.server.pubsub_redis.disk_store, server=self.server)
        return out

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
        backend = self._create_greenlet_backend()

        logger.info('PubSub delivery greenlet started for sub_key `%s`', sub_key)

        # .. on startup, drain any messages that were read but never acknowledged
        # .. before the process stopped (e.g. after a restart) ..
        while not self._stop_event.is_set():
            if sub_key not in self.server._push_subs:
                break
            pending = backend.fetch_pending(sub_key, max_messages=_delivery_batch_size)
            if not pending:
                break
            self._deliver_batch(pending, sub_key, backend)

        # .. then block for new messages ..
        while not self._stop_event.is_set():
            if sub_key not in self.server._push_subs:
                break
            try:
                messages = backend.fetch_messages(
                    sub_key, max_messages=_delivery_batch_size, block_ms=_default_delivery_block_ms)
                if messages:
                    self._deliver_batch(messages, sub_key, backend)
            except Exception:
                logger.warning('PubSub delivery error for sub_key `%s`: %s', sub_key, format_exc())

        logger.info('PubSub delivery greenlet stopped for sub_key `%s`', sub_key)

# ################################################################################################################################

    def _deliver_batch(self, messages:'list', sub_key:'str', backend:'RedisPubSubBackend') -> 'None':
        """ Deliver a batch of raw messages, retrying each one individually.
        """
        config_list = self.server._push_subs[sub_key]

        config_by_topic:'anydict' = {}
        for config in config_list:
            config_by_topic[config['topic_name']] = config

        for message in messages:
            topic_name = message['topic_name']
            sub_config = config_by_topic[topic_name]
            self._deliver_with_retry(message, sub_config, sub_key, backend)

# ################################################################################################################################

    def _deliver_with_retry(
        self,
        message:'anydict',
        sub_config:'anydict',
        sub_key:'str',
        backend:'RedisPubSubBackend'
    ) -> 'None':
        """ Attempt to deliver a message, retrying with logarithmic backoff and jitter
        until the delivery deadline is reached or the message expires.
        Acknowledges the message regardless of outcome so it is removed from the stream.
        """

        # Extract routing metadata from the message ..
        stream_name = message['_stream_name']
        redis_message_id = message['_redis_message_id']
        data_ref = message['_data_ref']
        msg_id = message['msg_id']

        # .. parse the expiration time for TTL checks on each retry ..
        expiration_time_iso = message['expiration_time_iso']
        normalized_expiration_iso = expiration_time_iso.replace('Z', '+00:00')
        expiration_time = datetime.fromisoformat(normalized_expiration_iso)

        # .. set up the retry loop with logarithmic backoff ..
        deadline = monotonic() + _max_retry_time
        interval = _retry_interval_initial
        attempt = 0
        delivered = False
        expired = False

        while monotonic() < deadline:

            # .. check if the message has expired - if so, drop it without delivery
            # .. because there is no point pushing stale data to the endpoint ..
            now = utcnow()
            if now > expiration_time:
                msg = f'PubSub message expired before delivery for sub_key `{sub_key}`'
                msg += f', msg_id `{msg_id}`, expiration_time_iso `{expiration_time_iso}`'
                logger.info(msg)
                expired = True
                break

            # .. attempt the actual delivery ..
            try:
                self._deliver_message(message, sub_config)
                delivered = True
                break
            except Exception:
                attempt += 1
                msg = f'PubSub delivery attempt {attempt} failed for sub_key `{sub_key}`'
                msg += f', msg_id `{msg_id}`: {format_exc()}'
                logger.debug(msg)

                # .. compute jitter as a fraction of the current interval ..
                jitter = interval * _retry_jitter_percent / 100
                sleep_time = interval + uniform(0, jitter)
                sleep(sleep_time)

                # .. grow the interval logarithmically, capped at the configured maximum ..
                interval = min(interval * log2(interval + 1), _retry_interval_max)
        else:
            if not delivered:
                msg = f'PubSub delivery deadline exhausted for sub_key `{sub_key}`'
                msg += f', msg_id `{msg_id}` after {attempt} attempts'
                logger.error(msg)

        # .. if the message expired, only ack the stream entry so it is not re-fetched,
        # .. but leave the disk file and custom pending sets intact - other subscribers
        # .. may still need this message (it only expired for this subscriber's delivery
        # .. attempt). The global expiry sweep in cleanup.py will delete the disk file
        # .. once the message's TTL passes for all subscribers.
        if expired:
            _ = backend.redis.xack(stream_name, sub_key, redis_message_id)
        else:
            # .. otherwise do a full ack which cleans up disk and pending state.
            backend.ack_message(stream_name, sub_key, redis_message_id, data_ref)

# ################################################################################################################################

    def _deliver_message(self, message:'anydict', sub_config:'anydict') -> 'None':
        """ Deliver a single raw message to the configured target.
        """
        push_type = sub_config['push_type']

        if push_type == PubSub.Push_Type.Service:
            self._deliver_to_service(message, sub_config)

        elif push_type == PubSub.Push_Type.REST:
            self._deliver_to_rest(message, sub_config)

# ################################################################################################################################

    def _deliver_to_service(self, message:'anydict', sub_config:'anydict') -> 'None':
        """ Deliver a raw message by invoking a Zato service.
        """

        # stdlib
        import json
        from importlib import import_module

        service_name = sub_config['push_service_name']

        # Extract the user data ..
        data_raw = message['data']

        # .. if a data_class was stored, reconstruct the original Model ..
        if data_class_name := message.get('data_class'):
            data = json.loads(data_raw)
            module_path, _, class_name = data_class_name.rpartition('.')
            module = import_module(module_path)
            model_class = getattr(module, class_name)
            payload = model_class.from_dict(data)

        # .. otherwise, pass the raw data through so the service can parse it itself ..
        else:
            payload = data_raw

        self.server.invoke(service_name, payload)

# ################################################################################################################################

    def _deliver_to_rest(self, message:'anydict', sub_config:'anydict') -> 'None':
        """ Deliver a raw message by posting to a REST endpoint.
        """
        from json import dumps
        from requests import post as requests_post

        url = sub_config['rest_push_url']

        response = requests_post(url, data=dumps(message), headers={'Content-Type': 'application/json'})
        response.raise_for_status()

# ################################################################################################################################
# ################################################################################################################################
