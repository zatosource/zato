# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.pubsub.delivery import deliver_with_policy, DeliveryExhausted, DeliveryInterrupted, Interrupt_Database, \
    Interrupt_Expired, Interrupt_Paused, Interrupt_Replaced, Interrupt_Withdrawn, wait_between_rounds
from zato.common.pubsub.sql.fast_path import Attempt_Recorded_Key
from zato.common.pubsub.sql.replaced import PubSubReplaced
from zato.common.util.retry import RetryPolicy
from zato.common.util.time_ import parse_utc
from zato.server.base.parallel.delivery_batch import BatchCommitFailed, deliver_to_service
from zato.server.base.parallel.delivery_rest import deliver_to_rest, get_rest_push_url

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent.lock import BoundedSemaphore
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import anydict, callable_, callnone, strset
    from zato.server.base.parallel import ParallelServer

    BoundedSemaphore = BoundedSemaphore
    ParallelServer = ParallelServer
    SQLPubSubBackend = SQLPubSubBackend
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The default set a published message's own retry settings fall back to
_delivery_defaults = PubSub.Delivery

_outgoing_sub_key_prefix = PubSub.Outgoing.Sub_Key_Prefix

# ################################################################################################################################
# ################################################################################################################################

class MessageDelivery:
    """ The delivery of one message of a subscriber key under its retry policy, with the audit event
    that records how the delivery concluded.
    """
    server: 'ParallelServer'
    backend: 'SQLPubSubBackend'
    _paused: 'strset'
    _database_slots: 'BoundedSemaphore'

    def _deliver_one(
        self,
        message:'anydict',
        sub_config:'anydict',
        sub_key:'str',
        read_epoch:'int',
        before_wait:'callnone',
    ) -> 'bool':
        """ Delivers one message, returning whether it was concluded - delivered, expired or given up on.
        A message of an outgoing connection's queue whose round failed is not concluded, it stays for the next round,
        whereas a push message whose round ran out is concluded as a failed delivery. A before_wait callable
        is called before each wait between two attempts of a push message.
        """
        msg_id = message['msg_id']
        is_outgoing = sub_key.startswith(_outgoing_sub_key_prefix)

        expiration_time = self._get_expiration_time(message)

        # Expirations are measured against the time of the database ..
        clock = self.backend.clock

        # .. an expired message is not attempted at all ..
        if clock.now() > expiration_time:
            self._conclude_expired(message, sub_config, sub_key)
            return True

        def should_continue() -> 'str':

            # .. a queue asked to pause gives up between two attempts rather than in the middle of one,
            # .. leaving the message where it is so that it goes out again once the queue resumes ..
            if sub_key in self._paused:
                return Interrupt_Paused

            # .. and a message that expired between two attempts is not attempted again.
            if clock.now() > expiration_time:
                return Interrupt_Expired

            return ''

        try:
            self._deliver_message(message, sub_config, sub_key, should_continue, read_epoch, before_wait)

        # A commit before a wait that failed is not a failure of the delivery ..
        except BatchCommitFailed:
            raise

        except DeliveryInterrupted as e:

            if e.reason == Interrupt_Paused:
                logger.info('Pausing sub_key `%s` between delivery attempts, msg_id `%s`', sub_key, msg_id)
                return False

            # .. an attempt that could not be recorded was not sent, so the message stays for the next round ..
            if e.reason == Interrupt_Database:
                logger.info('Delivery attempt not recorded for sub_key `%s`, msg_id `%s`: %s', sub_key, msg_id, e.__cause__)
                return False

            # .. a message that left the queue in the meantime has nothing left to deliver ..
            if e.reason == Interrupt_Withdrawn:
                logger.info('Message left the queue before delivery, sub_key `%s`, msg_id `%s`', sub_key, msg_id)
                return True

            # .. and once another server took over the database, this one sends nothing anymore.
            if e.reason == Interrupt_Replaced:
                raise PubSubReplaced(str(e.__cause__)) from e

            self._conclude_expired(message, sub_config, sub_key)
            return True

        except DeliveryExhausted as e:

            # An outgoing connection's message whose round ran out stays for another round ..
            if is_outgoing:
                reason = str(e)
                return self._keep_for_next_round(message, sub_config, sub_key, expiration_time, reason)

            # .. whereas a push message whose round ran out is given up on.
            self._conclude_failed(message, sub_config, sub_key, e.error, e.attempts)
            return True

        except Exception:
            reason = format_exc()
            is_concluded = self._keep_for_next_round(message, sub_config, sub_key, expiration_time, reason)

            # A push message fails here only outside its retry policy, which therefore did not wait before the next read
            if not is_concluded and not is_outgoing:
                if before_wait:
                    before_wait()
                wait_between_rounds()

            return is_concluded

        self._insert_audit_event(message, sub_config, sub_key, True, False)
        return True

# ################################################################################################################################

    def _get_expiration_time(self, message:'anydict') -> 'datetime':
        """ Returns the time at which a message expires.
        """
        expiration_time_iso = message['expiration_time_iso']
        normalized_expiration_iso = expiration_time_iso.replace('Z', '+00:00')

        out = datetime.fromisoformat(normalized_expiration_iso)
        return out

# ################################################################################################################################

    def _conclude_failed(self, message:'anydict', sub_config:'anydict', sub_key:'str', error:'str', attempts:'int') -> 'None':
        """ Records that a push message was given up on once its round ran out of attempts.
        """
        msg = f'PubSub delivery given up for sub_key `{sub_key}`'
        msg += f', msg_id `{message["msg_id"]}` after {attempts} attempts: {error}'
        logger.error(msg)

        self._insert_audit_event(message, sub_config, sub_key, False, False, error, attempts)

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

        clock = self.backend.clock

        if clock.now() > expiration_time:
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

        # .. the publication time arrives from the broker as an ISO 8601 string ..
        pub_time = parse_utc(message['pub_time_iso'])

        # .. now, write out the event.
        self.backend.audit_log.insert(AuditSource.PubSub, event_type, message['topic_name'],
            cid=message_cid,
            msg_id=message['msg_id'],
            correl_id=correl_id,
            pub_time=pub_time,
            endpoint=endpoint,
            sub_key=sub_key,
            size=message['data_size'],
            priority=message['priority'],
            outcome=outcome,
            status=status,
            data=message['data'],
            is_export_payload_active=self.backend.is_topic_payload_exported(message['topic_name']),
            commits_with_batch=True,
        )

# ################################################################################################################################

    def _get_endpoint(self, sub_config:'anydict') -> 'str':
        """ The name of what a subscription pushes to - a service or a REST endpoint.
        """
        if sub_config['push_type'] == PubSub.Push_Type.Service:
            out = sub_config['push_service_name']
        else:
            out = get_rest_push_url(self.server.config_manager.config_store, sub_config)

        return out

# ################################################################################################################################

    def _deliver_message(
        self,
        message:'anydict',
        sub_config:'anydict',
        sub_key:'str',
        should_continue:'callable_',
        read_epoch:'int',
        before_wait:'callnone',
    ) -> 'None':
        """ Delivers one message to its target. An outgoing connection's queue invokes its delivery service once,
        which retries as the connection says, whereas a push message runs one round under its own retry policy
        right here, raising DeliveryExhausted when the round ran out. Each attempt sends the payload of the most recent
        edit of the message, including an edit that took place during the round.
        """
        push_type = sub_config['push_type']

        if push_type == PubSub.Push_Type.Service:
            deliver = self._deliver_to_service
        else:
            deliver = self._deliver_to_rest

        # Outgoing connections have retry policies of their own
        if sub_key.startswith(_outgoing_sub_key_prefix):
            self._record_attempt(message)
            _ = self._use_current_payload(message, read_epoch)
            deliver(message, sub_config)
            return

        policy = RetryPolicy.from_config(message, _delivery_defaults)
        endpoint = self._get_endpoint(sub_config)

        message_cid = message.get('cid')
        if message_cid is None:
            message_cid = ''

        def attempt() -> 'None':
            nonlocal read_epoch
            self._record_attempt(message)
            read_epoch = self._use_current_payload(message, read_epoch)
            deliver(message, sub_config)

        deliver_with_policy(policy, 0, message_cid, endpoint, attempt, should_continue, before_wait)

# ################################################################################################################################

    def _use_current_payload(self, message:'anydict', read_epoch:'int') -> 'int':
        """ Replaces the payload of a message with the one in the database if an edit advanced the payload epoch
        after the payload was read, and returns the epoch under which the payload of the message was read.
        """
        out = self.backend.payload_cache.get_epoch()

        if out != read_epoch:
            message['data'] = self.backend.read_payload(message)

        return out

# ################################################################################################################################

    def _record_attempt(self, message:'anydict') -> 'None':
        """ Records an attempt in the database before it is sent, which on PostgreSQL confirms that this server
        is still the active one. Each outcome other than a recorded attempt stops the round without counting
        as a failed attempt.
        """
        # The first attempt of a message of an atomic batch was recorded by the claim of the batch
        if message.pop(Attempt_Recorded_Key, False):
            return

        try:
            with self._database_slots:
                is_pending = self.backend.record_attempt(message)

        except PubSubReplaced as e:
            raise DeliveryInterrupted(Interrupt_Replaced, 0) from e

        except DBAPIError as e:
            raise DeliveryInterrupted(Interrupt_Database, 0) from e

        if not is_pending:
            raise DeliveryInterrupted(Interrupt_Withdrawn, 0)

# ################################################################################################################################

    def _deliver_to_service(self, message:'anydict', sub_config:'anydict') -> 'None':
        deliver_to_service(self.server, message, sub_config)

# ################################################################################################################################

    def _deliver_to_rest(self, message:'anydict', sub_config:'anydict') -> 'None':
        deliver_to_rest(self.server.config_manager.config_store, self.backend.payload_cache, message, sub_config)

# ################################################################################################################################
# ################################################################################################################################
