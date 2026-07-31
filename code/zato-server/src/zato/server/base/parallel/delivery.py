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
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import anydict, intlist, strlist, strset
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_default_delivery_block_ms = 5000
_delivery_batch_size = 50

# How long to wait for a subscriber's delivery greenlet to come back between two batches, which covers
# the batch it may have started just before it was asked to pause.
_pause_join_timeout = 30

_max_retry_time = PubSub.Delivery.Max_Retry_Time
_retry_interval_initial = PubSub.Delivery.Retry_Interval_Initial
_retry_interval_max = PubSub.Delivery.Retry_Interval_Max
_retry_jitter_percent = PubSub.Delivery.Retry_Jitter_Percent

sub_key_greenlet_dict = dict[str, 'Greenlet']

# ################################################################################################################################
# ################################################################################################################################

class PushDelivery:
    """ Delivers messages from the SQL pub/sub backend to target services and REST
    endpoints by maintaining one greenlet per subscriber key. All greenlets share
    one backend - a blocking fetch waits on the backend's per-subscriber event that
    publications set, so no greenlet needs a dedicated database connection.
    """

    def __init__(self, server:'ParallelServer', backend:'SQLPubSubBackend') -> 'None':
        self.server = server
        self.backend = backend
        self._stop_event = Event()
        self._greenlets:'sub_key_greenlet_dict' = {}
        self._paused:'strset' = set()
        self._lock = RLock()

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

    def pause_sub_key(self, sub_key:'str') -> 'None':
        """ Stops the delivery greenlet of one subscriber between two of its batches, rather than
        wherever it happens to be, which is what a queue being moved needs - a message whose delivery
        is cut in half is never acknowledged and goes out a second time when the queue starts again.
        """
        with self._lock:
            self._paused.add(sub_key)
            greenlet = self._greenlets.pop(sub_key, None)

        # A subscriber whose greenlet never ran has nothing to wait for
        if not greenlet:
            return

        # The loop notices the pause only once it is between batches, and a fetch of its own blocks
        # for a while, so waking that fetch up is what makes the pause take effect right away ..
        self.backend.notify_sub_keys([sub_key])

        # .. and this is where whatever is being delivered right now is waited for ..
        _ = greenlet.join(timeout=_pause_join_timeout)

        # .. while a greenlet still busy after all that time is stopped where it stands,
        # .. which is the same at-least-once trade-off that a server shutdown makes.
        if not greenlet.ready():
            logger.info('Delivery greenlet for sub_key `%s` did not pause in time, stopping it now', sub_key)
            greenlet.kill()

# ################################################################################################################################

    def resume_sub_key(self, sub_key:'str') -> 'None':
        """ Starts a paused subscriber's delivery greenlet again, under the sub key it always had.
        """
        with self._lock:
            self._paused.discard(sub_key)

        self.start_sub_key(sub_key)

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
        """ Deliver messages for one subscriber key until stopped. A blocking fetch
        waits on the subscriber's wake-up event, so the loop sleeps while the queue
        is empty and resumes the moment a publication lands.
        """
        logger.info('PubSub delivery greenlet started for sub_key `%s`', sub_key)

        # On startup, drain everything still unacknowledged for this subscriber ..
        while not self._stop_event.is_set():
            if sub_key not in self.server.config_manager._push_subs:
                break
            if sub_key in self._paused:
                break
            pending = self.backend.fetch_pending(sub_key, max_messages=_delivery_batch_size)
            if not pending:
                break
            self._deliver_batch(pending, sub_key)

        # .. then wait for new messages.
        while not self._stop_event.is_set():
            if sub_key not in self.server.config_manager._push_subs:
                break
            if sub_key in self._paused:
                break
            try:
                messages = self.backend.fetch_messages(
                    sub_key, max_messages=_delivery_batch_size, block_ms=_default_delivery_block_ms)
                if messages:
                    self._deliver_batch(messages, sub_key)
            except Exception:
                logger.warning('PubSub delivery error for sub_key `%s`: %s', sub_key, format_exc())

        logger.info('PubSub delivery greenlet stopped for sub_key `%s`', sub_key)

# ################################################################################################################################

    def _deliver_batch(self, messages:'list', sub_key:'str') -> 'None':
        """ Deliver a batch of raw messages, retrying each one individually, then
        acknowledge the whole batch in one transaction. An acknowledgement removes
        this subscriber's delivery rows only - a message expired or undeliverable
        for this subscriber stays behind for every other subscriber that needs it.
        """
        config_list = self.server.config_manager._push_subs[sub_key]

        config_by_topic:'anydict' = {}
        for config in config_list:
            config_by_topic[config['topic_name']] = config

        msg_ids:'strlist' = []
        sequence_ids:'intlist' = []

        for message in messages:

            # A queue asked to pause stops between two of its messages, and what is left of the batch
            # stays in the queue, to go out when the queue starts again.
            if sub_key in self._paused:
                break

            topic_name = message['topic_name']
            sub_config = config_by_topic[topic_name]

            # A message the pause interrupted has not been concluded either way, so it is not acked
            is_concluded = self._deliver_with_retry(message, sub_config, sub_key)

            if not is_concluded:
                break

            msg_ids.append(message['msg_id'])
            sequence_ids.append(message['sequence_id'])

        # Delivered, expired and given-up messages all leave the queue - retrying
        # ran its course above, so nothing here is awaiting another attempt.
        _ = self.backend.ack_messages(sub_key, msg_ids, sequence_ids)

# ################################################################################################################################

    def _deliver_with_retry(
        self,
        message:'anydict',
        sub_config:'anydict',
        sub_key:'str',
    ) -> 'bool':
        """ Attempt to deliver a message, retrying with logarithmic backoff and jitter
        until the delivery deadline is reached or the message expires. Acknowledgement
        is the caller's job - one transaction covers the whole batch. Answers with whether
        the message was concluded, which a queue asked to pause between two attempts was not.
        """
        msg_id = message['msg_id']

        # Parse the expiration time for TTL checks on each retry ..
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

            # .. a queue asked to pause gives up between two attempts rather than in the middle of one,
            # .. leaving the message where it is so that it goes out again once the queue resumes ..
            if sub_key in self._paused:
                logger.info('Pausing sub_key `%s` between delivery attempts, msg_id `%s`', sub_key, msg_id)
                return False

            # .. drop expired messages without delivery ..
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

            # .. record the delivery outcome in the audit log.
        self._insert_audit_event(message, sub_config, sub_key, delivered, expired)

        # The message is out of the queue's hands either way - delivered, expired or given up on.
        return True

# ################################################################################################################################

    def _insert_audit_event(
        self,
        message:'anydict',
        sub_config:'anydict',
        sub_key:'str',
        delivered:'bool',
        expired:'bool'
    ) -> 'None':
        """ Writes one audit event describing the outcome of a push delivery attempt.
        """

        # The backend has no audit log in unit tests only.
        if not self.backend.audit_log:
            return

        # The topic's audit log may have been turned off explicitly.
        if message['topic_name'] in self.backend.audit_disabled_topics:
            return

        # Map the delivery outcome to an event type ..
        if delivered:
            event_type = AuditEvent.Delivered
            outcome = AuditOutcome.OK
        elif expired:
            event_type = AuditEvent.Expired
            outcome = AuditOutcome.Expired
        else:
            event_type = AuditEvent.Delivery_Failed
            outcome = AuditOutcome.Error

        # .. the delivery target is either a service or a REST endpoint ..
        if sub_config['push_type'] == PubSub.Push_Type.Service:
            endpoint = sub_config['push_service_name']
        else:
            endpoint = sub_config['rest_push_url']

        # .. these are optional at publish time so the message dict includes them
        # .. only when they were given ..
        message_cid = message.get('cid')
        if message_cid is None:
            message_cid = ''

        correl_id = message.get('correl_id')
        if correl_id is None:
            correl_id = ''

        # .. now, write out the event.
        self.backend.audit_log.insert(AuditSource.PubSub, event_type, message['topic_name'],
            cid=message_cid,
            msg_id=message['msg_id'],
            correl_id=correl_id,
            pub_time_iso=message['pub_time_iso'],
            endpoint=endpoint,
            sub_key=sub_key,
            size=message['data_size'],
            priority=message['priority'],
            outcome=outcome,
            data=message['data'],
        )

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
        if data_class_name := message['data_class']:
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
