# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep, spawn
from gevent.event import Event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.redis_backend import RedisPubSubBackend
    from zato.common.typing_ import anydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_idle_sleep = 0.1
_delivery_batch_size = 50

# ################################################################################################################################
# ################################################################################################################################

class RedisPushDelivery:
    """ Polls Redis Streams for push-type subscriptions and delivers
    messages to target services or REST endpoints.
    """

    def __init__(self, server:'ParallelServer', pubsub_redis:'RedisPubSubBackend') -> 'None':
        self.server = server
        self.pubsub_redis = pubsub_redis
        self._stop_event = Event()

    def start(self) -> 'None':
        spawn(self._run)

    def stop(self) -> 'None':
        self._stop_event.set()

    def _run(self) -> 'None':
        logger.info('PubSub push delivery greenlet started')

        while not self._stop_event.is_set():
            try:
                found_any = self._poll_cycle()
            except Exception:
                logger.warning('PubSub push delivery error: %s', format_exc())
                found_any = False

            if not found_any:
                sleep(_idle_sleep)

        logger.info('PubSub push delivery greenlet stopped')

    def _poll_cycle(self) -> 'bool':
        push_subs = self.server._push_subs

        if not push_subs:
            return False

        found_any = False

        for sub_key, sub_config in push_subs.items():
            if self._stop_event.is_set():
                break

            messages = self.pubsub_redis.fetch_messages(sub_key, max_messages=_delivery_batch_size)

            if not messages:
                continue

            found_any = True

            for msg in messages:
                try:
                    self._deliver_message(msg, sub_config)
                except Exception:
                    logger.warning('PubSub push delivery failed for sub_key `%s`: %s', sub_key, format_exc())

        return found_any

    def _deliver_message(self, msg:'anydict', sub_config:'anydict') -> 'None':
        push_type = sub_config['push_type']

        logger.info('PubSub push delivering msg keys=%s, sub_config=%s', list(msg.keys()), sub_config)
        logger.info('PubSub push delivering msg=%s', msg)

        if push_type == 'service':
            from bunch import bunchify
            service_name = sub_config['push_service_name']
            flat = dict(msg.get('meta', {}))
            flat['data'] = msg['data']
            self.server.invoke(service_name, bunchify(flat))

        elif push_type == 'rest':
            self._deliver_to_rest(msg, sub_config)

    def _deliver_to_rest(self, msg:'anydict', sub_config:'anydict') -> 'None':
        from json import dumps
        from requests import post as requests_post

        url = sub_config['rest_push_url']
        requests_post(url, data=dumps(msg), headers={'Content-Type': 'application/json'})

# ################################################################################################################################
# ################################################################################################################################
