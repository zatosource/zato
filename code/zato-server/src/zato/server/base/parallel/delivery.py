# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep, spawn
from gevent.event import Event
from gevent.lock import RLock

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.pubsub.delivery import deliver_with_policy, DeliveryExhausted, DeliveryInterrupted, Interrupt_Expired, \
    Interrupt_Paused
from zato.common.util.api import utcnow
from zato.common.util.retry import RetryPolicy

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import anydict, callable_, intlist, strlist, strset
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_default_delivery_block_ms = 5000
_delivery_batch_size = 50

# How long to wait for a subscriber's delivery greenlet to come back between two batches, which covers
# the batch it may have started just before it was asked to pause.
_pause_join_timeout = 30

# How long a delivery greenlet waits after a fetch that raised
_fetch_error_sleep = PubSub.Delivery.Fetch_Error_Sleep

# The default set a published message's own retry settings fall back to
_delivery_defaults = PubSub.Delivery

_outgoing_sub_key_prefix = PubSub.Outgoing.Sub_Key_Prefix

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

            # A stopped subscriber is not a paused one either, or the same key would never run again if it came back
            self._paused.discard(sub_key)

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

                sleep(_fetch_error_sleep)

        logger.info('PubSub delivery greenlet stopped for sub_key `%s`', sub_key)

# ################################################################################################################################

    def _deliver_batch(self, messages:'list', sub_key:'str') -> 'None':
        """ Deliver a batch of raw messages, retrying each one individually. An outgoing connection's queue acknowledges
        each message as it is concluded, any other subscriber's batch is acknowledged in one transaction.
        An acknowledgement removes this subscriber's delivery rows only - a message expired or undeliverable
        for this subscriber stays behind for every other subscriber that needs it.
        """
        config_list = self.server.config_manager._push_subs[sub_key]

        config_by_topic:'anydict' = {}
        for config in config_list:
            config_by_topic[config['topic_name']] = config

        msg_ids:'strlist' = []
        sequence_ids:'intlist' = []

        is_outgoing = sub_key.startswith(_outgoing_sub_key_prefix)

        for message in messages:

            # A queue asked to pause stops between two of its messages, and what is left of the batch
            # stays in the queue, to go out when the queue starts again.
            if sub_key in self._paused:
                break

            topic_name = message['topic_name']
            sub_config = config_by_topic[topic_name]

            is_concluded = self._deliver_one(message, sub_config, sub_key)

            # A message that was not concluded is not acked, and nothing behind it is either
            if not is_concluded:
                break

            msg_id = message['msg_id']
            sequence_id = message['sequence_id']

            # An outgoing connection's queue acks each message as soon as it is concluded and counts out only
            # what the ack removed, so a delivery stopped in the middle of a batch leaves no concluded message behind ..
            if is_outgoing:
                fully_delivered_count = self.backend.ack_messages(sub_key, [msg_id], [sequence_id])
                self.server.config_manager.outgoing_queue_depth.lower(sub_key, fully_delivered_count)

            # .. whereas the messages of any other subscriber are acked together once the batch is over.
            else:
                msg_ids.append(msg_id)
                sequence_ids.append(sequence_id)

        # Delivered, expired and given-up messages all leave the queue - retrying
        # ran its course above, so nothing here is awaiting another attempt.
        _ = self.backend.ack_messages(sub_key, msg_ids, sequence_ids)

# ################################################################################################################################

    def _deliver_one(
        self,
        message:'anydict',
        sub_config:'anydict',
        sub_key:'str',
    ) -> 'bool':
        """ Delivers one message, returning whether it was concluded - delivered, expired or given up on.
        A message of an outgoing connection's queue whose round failed is not concluded, it stays for the next round,
        whereas a push message whose round ran out is concluded as a failed delivery.
        """
        msg_id = message['msg_id']
        is_outgoing = sub_key.startswith(_outgoing_sub_key_prefix)

        expiration_time_iso = message['expiration_time_iso']
        normalized_expiration_iso = expiration_time_iso.replace('Z', '+00:00')
        expiration_time = datetime.fromisoformat(normalized_expiration_iso)

        # An expired message is not attempted at all ..
        if utcnow() > expiration_time:
            self._conclude_expired(message, sub_config, sub_key)
            return True

        def should_continue() -> 'str':

            # .. a queue asked to pause gives up between two attempts rather than in the middle of one,
            # .. leaving the message where it is so that it goes out again once the queue resumes ..
            if sub_key in self._paused:
                return Interrupt_Paused

            # .. and a message that expired between two attempts is not attempted again.
            if utcnow() > expiration_time:
                return Interrupt_Expired

            return ''

        try:
            self._deliver_message(message, sub_config, sub_key, should_continue)

        except DeliveryInterrupted as e:

            if e.reason == Interrupt_Paused:
                logger.info('Pausing sub_key `%s` between delivery attempts, msg_id `%s`', sub_key, msg_id)
                return False

            self._conclude_expired(message, sub_config, sub_key)
            return True

        except DeliveryExhausted as e:

            # An outgoing connection's message whose round ran out stays for another round ..
            if is_outgoing:
                reason = str(e)
                return self._keep_for_next_round(message, sub_config, sub_key, expiration_time, reason)

            # .. whereas a push message whose round ran out is given up on.
            msg = f'PubSub delivery given up for sub_key `{sub_key}`'
            msg += f', msg_id `{msg_id}` after {e.attempts} attempts: {e.error}'
            logger.error(msg)

            self._insert_audit_event(message, sub_config, sub_key, False, False, e.error, e.attempts)
            return True

        except Exception:
            reason = format_exc()
            return self._keep_for_next_round(message, sub_config, sub_key, expiration_time, reason)

        self._insert_audit_event(message, sub_config, sub_key, True, False)
        return True

# ################################################################################################################################

    def _keep_for_next_round(
        self,
        message:'anydict',
        sub_config:'anydict',
        sub_key:'str',
        expiration_time:'datetime',
        reason:'str',
    ) -> 'bool':
        """ A failed round of an outgoing connection's message leaves it in the queue for the next round,
        unless it expired while the round was failing - then it is concluded as expired.
        """
        msg_id = message['msg_id']

        msg = f'PubSub outgoing delivery round failed for sub_key `{sub_key}`'
        msg += f', msg_id `{msg_id}`: {reason}'
        logger.debug(msg)

        if utcnow() > expiration_time:
            self._conclude_expired(message, sub_config, sub_key)
            return True

        return False

# ################################################################################################################################

    def _conclude_expired(self, message:'anydict', sub_config:'anydict', sub_key:'str') -> 'None':
        """ Records that a message left the queue because it expired before it could be delivered.
        """
        msg_id = message['msg_id']
        expiration_time_iso = message['expiration_time_iso']

        msg = f'PubSub message expired before delivery for sub_key `{sub_key}`'
        msg += f', msg_id `{msg_id}`, expiration_time_iso `{expiration_time_iso}`'
        logger.info(msg)

        self._insert_audit_event(message, sub_config, sub_key, False, True)

# ################################################################################################################################

    def _insert_audit_event(
        self,
        message:'anydict',
        sub_config:'anydict',
        sub_key:'str',
        delivered:'bool',
        expired:'bool',
        error:'str'='',
        attempts:'int'=0,
    ) -> 'None':
        """ Writes the one audit event describing how a push delivery concluded.
        """

        # The backend has no audit log in unit tests only.
        if not self.backend.audit_log:
            return

        # The topic's audit log may have been turned off explicitly.
        if message['topic_name'] in self.backend.audit_disabled_topics:
            return

        # Map the delivery outcome to an event type ..
        status = ''

        if delivered:
            event_type = AuditEvent.Delivered
            outcome = AuditOutcome.OK
        elif expired:
            event_type = AuditEvent.Expired
            outcome = AuditOutcome.Expired
        else:
            event_type = AuditEvent.Delivery_Failed
            outcome = AuditOutcome.Error
            status = f'Given up after {attempts} attempts: {error}'

        # .. the delivery target is either a service or a REST endpoint ..
        endpoint = self._get_endpoint(sub_config)

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
            status=status,
            data=message['data'],
            is_export_payload_active=self.backend.is_topic_payload_exported(message['topic_name']),
        )

# ################################################################################################################################

    def _get_endpoint(self, sub_config:'anydict') -> 'str':
        """ The name of what a subscription pushes to - a service or a REST endpoint.
        """
        if sub_config['push_type'] == PubSub.Push_Type.Service:
            out = sub_config['push_service_name']
        else:
            out = sub_config['rest_push_url']

        return out

# ################################################################################################################################

    def _deliver_message(
        self,
        message:'anydict',
        sub_config:'anydict',
        sub_key:'str',
        should_continue:'callable_',
    ) -> 'None':
        """ Delivers one message to its target. An outgoing connection's queue invokes its delivery service once,
        which retries as the connection says, whereas a push message runs one round under its own retry policy
        right here, raising DeliveryExhausted when the round ran out.
        """
        push_type = sub_config['push_type']

        if push_type == PubSub.Push_Type.Service:
            deliver = self._deliver_to_service
        else:
            deliver = self._deliver_to_rest

        # Outgoing connections have retry policies of their own
        if sub_key.startswith(_outgoing_sub_key_prefix):
            deliver(message, sub_config)
            return

        policy = RetryPolicy.from_config(message, _delivery_defaults)
        endpoint = self._get_endpoint(sub_config)

        message_cid = message.get('cid')
        if message_cid is None:
            message_cid = ''

        def attempt() -> 'None':
            deliver(message, sub_config)

        deliver_with_policy(policy, 0, message_cid, endpoint, attempt, should_continue)

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
