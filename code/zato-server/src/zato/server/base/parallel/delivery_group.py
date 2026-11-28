# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from functools import partial
from logging import getLogger

# gevent
from gevent import GreenletExit, sleep

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.delivery import get_jittered_sleep_time
from zato.common.pubsub.delivery_scope import close_delivery_scope, open_delivery_scope
from zato.common.pubsub.sql.fast_path import Attempt_Recorded_Key
from zato.common.pubsub.sql.replaced import PubSubReplaced
from zato.common.util.retry import get_first_sleep_time, get_next_sleep_time, RetryPolicy
from zato.server.base.parallel.delivery_batch import BatchCommitFailed, _commit_before_wait, _commit_on_exit
from zato.server.base.parallel.delivery_message import MessageDelivery
from zato.server.base.parallel.delivery_rest import deliver_group_to_rest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.delivery_scope import DeliveryScope
    from zato.common.typing_ import anydict, anylist, callable_, strset

    DeliveryScope = DeliveryScope

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The default set a published message's own retry settings fall back to
_delivery_defaults = PubSub.Delivery

# ################################################################################################################################
# ################################################################################################################################

class GroupDelivery(MessageDelivery):
    """ The delivery of the messages of a push subscriber to a REST endpoint in groups, each group posted
    as one request whose response names the messages it accepted.
    """

    def _deliver_group_batch(
        self,
        messages:'anylist',
        config_by_topic:'anydict',
        sub_key:'str',
        read_epoch:'int',
        push_batch_size:'int',
    ) -> 'DeliveryScope':
        """ Delivers a claimed batch in groups of up to push_batch_size messages, in order, and returns what the batch
        concluded and has not committed yet, which the caller commits. A group that was not fully concluded
        stops the batch, and the rest of the batch goes out again with the next claim.
        """
        # What is concluded is acknowledged in one commit with the claim of the next batch ..
        scope = open_delivery_scope()

        # .. or before each wait of a retry of a group ..
        before_wait = partial(_commit_before_wait, self.backend, scope, sub_key)

        try:
            for start in range(0, len(messages), push_batch_size):

                # .. a queue asked to pause stops between two groups and keeps the rest of the batch ..
                if sub_key in self._paused:
                    break

                group = messages[start:start + push_batch_size]

                if not self._deliver_group(group, config_by_topic, sub_key, read_epoch, scope, before_wait):
                    break

        # .. a commit that failed before a wait is handled as a failed commit of the batch ..
        except BatchCommitFailed as e:
            raise e.error from e

        # .. a delivery that is stopped commits what it concluded before it ends ..
        except GreenletExit:
            _commit_on_exit(self.backend, scope, sub_key)
            raise

        finally:
            close_delivery_scope()

        # .. and the rest of the batch is committed by the caller.
        return scope

# ################################################################################################################################

    def _deliver_group(
        self,
        group:'anylist',
        config_by_topic:'anydict',
        sub_key:'str',
        read_epoch:'int',
        scope:'DeliveryScope',
        before_wait:'callable_',
    ) -> 'bool':
        """ Delivers one group until each of its messages is concluded - accepted, expired, withdrawn or given up on -
        and returns True, or returns False if the delivery stopped with messages of the group not concluded.
        The messages not accepted form the next request, in their order, after the wait of the policy of the first of them.
        """
        # The first attempt of each message was recorded by the claim of the batch ..
        for message in group:
            _ = message.pop(Attempt_Recorded_Key, False)

        # .. and each attempt after it is made by every message still pending, so they all have the same count.
        pending = group
        attempts_made = 0
        total_sleep_time = 0

        first_policy = RetryPolicy.from_config(pending[0], _delivery_defaults)
        current_sleep_time = get_first_sleep_time(first_policy)

        while True:

            # An expired message is not attempted again ..
            pending = self._conclude_expired_in_group(pending, config_by_topic, sub_key, scope)

            if not pending:
                return True

            # .. every attempt after a failed one is preceded by a wait ..
            if attempts_made:

                if sub_key in self._paused:
                    logger.info('Pausing sub_key `%s` between attempts of a group of %d messages', sub_key, len(pending))
                    return False

                before_wait()

                first_policy = RetryPolicy.from_config(pending[0], _delivery_defaults)
                sleep(get_jittered_sleep_time(first_policy, current_sleep_time))

                total_sleep_time += current_sleep_time
                current_sleep_time = get_next_sleep_time(first_policy, current_sleep_time, total_sleep_time)

                if sub_key in self._paused:
                    logger.info('Pausing sub_key `%s` between attempts of a group of %d messages', sub_key, len(pending))
                    return False

                pending = self._conclude_expired_in_group(pending, config_by_topic, sub_key, scope)

                if not pending:
                    return True

                # .. and records the attempt of each message, while a message that left the queue is concluded ..
                recorded = self._record_group_attempts(pending, sub_key)

                if recorded is None:
                    return False

                pending = self._conclude_withdrawn_in_group(pending, recorded, sub_key, scope)

                if not pending:
                    return True

                # .. each attempt sends the payload of the most recent edit of each message.
                read_epoch = self._use_current_payloads(pending, read_epoch)

            # The request is sent ..
            sub_config = config_by_topic[pending[0]['topic_name']]
            accepted:'strset' = set()
            error = ''

            try:
                accepted = deliver_group_to_rest(self.server.config_manager.config_store, self.backend.payload_cache,
                    pending, sub_config)

            except Exception as e:
                error = str(e)

            # .. what it accepted is concluded as delivered ..
            remaining:'anylist' = []

            for message in pending:
                if message['msg_id'] in accepted:
                    message_config = config_by_topic[message['topic_name']]
                    self._insert_audit_event(message, message_config, sub_key, True, False)
                    scope.msg_ids.append(message['msg_id'])
                else:
                    remaining.append(message)

            pending = remaining

            if not pending:
                return True

            attempts_made += 1

            if not error:
                error = f'Accepted {len(accepted)} of {len(accepted) + len(pending)} messages'

            # .. and a message whose policy allows no more attempts is given up on.
            pending = self._conclude_exhausted_in_group(pending, config_by_topic, sub_key, scope, attempts_made,
                total_sleep_time, error)

            if not pending:
                return True

            logger.info('Push group retry sub_key=%s, attempt=%s, pending=%s, reason=%s',
                sub_key, attempts_made, len(pending), error)

# ################################################################################################################################

    def _conclude_expired_in_group(
        self,
        pending:'anylist',
        config_by_topic:'anydict',
        sub_key:'str',
        scope:'DeliveryScope',
    ) -> 'anylist':
        """ Concludes each expired message of a group and returns the messages that remain.
        """
        now = self.backend.clock.now()
        out:'anylist' = []

        for message in pending:
            if now > self._get_expiration_time(message):
                self._conclude_expired(message, config_by_topic[message['topic_name']], sub_key)
                scope.msg_ids.append(message['msg_id'])
            else:
                out.append(message)

        return out

# ################################################################################################################################

    def _conclude_withdrawn_in_group(
        self,
        pending:'anylist',
        recorded:'set[int]',
        sub_key:'str',
        scope:'DeliveryScope',
    ) -> 'anylist':
        """ Concludes each message of a group that left the queue before its attempt was recorded
        and returns the messages that remain.
        """
        out:'anylist' = []

        for message in pending:
            if message['delivery_id'] in recorded:
                out.append(message)
            else:
                logger.info('Message left the queue before delivery, sub_key `%s`, msg_id `%s`', sub_key, message['msg_id'])
                scope.msg_ids.append(message['msg_id'])

        return out

# ################################################################################################################################

    def _conclude_exhausted_in_group(
        self,
        pending:'anylist',
        config_by_topic:'anydict',
        sub_key:'str',
        scope:'DeliveryScope',
        attempts_made:'int',
        total_sleep_time:'int',
        error:'str',
    ) -> 'anylist':
        """ Concludes as a failed delivery each message of a group whose policy allows no more attempts
        and returns the messages that remain.
        """
        out:'anylist' = []

        for message in pending:

            policy = RetryPolicy.from_config(message, _delivery_defaults)

            has_attempts_left = attempts_made < 1 + policy.max_retries
            has_time_left = total_sleep_time < policy.backoff_threshold

            if has_attempts_left and has_time_left:
                out.append(message)
            else:
                self._conclude_failed(message, config_by_topic[message['topic_name']], sub_key, error, attempts_made)
                scope.msg_ids.append(message['msg_id'])

        return out

# ################################################################################################################################

    def _record_group_attempts(self, pending:'anylist', sub_key:'str') -> 'set[int] | None':
        """ Records the next attempt of each message of a group in one commit and returns the delivery IDs
        of the messages still in the queue, or None if the attempts could not be recorded.
        """
        try:
            with self._database_slots:
                out = self.backend.record_attempts(pending)

        except PubSubReplaced:
            raise

        except DBAPIError as e:
            logger.info('Delivery attempts of a group not recorded for sub_key `%s`: %s', sub_key, e)
            return None

        return out

# ################################################################################################################################

    def _use_current_payloads(self, pending:'anylist', read_epoch:'int') -> 'int':
        """ Replaces the payloads of a group with those in the database if an edit advanced the payload epoch
        after they were read, and returns the epoch under which they were read.
        """
        out = self.backend.payload_cache.get_epoch()

        if out != read_epoch:
            for message in pending:
                message['data'] = self.backend.read_payload(message)

        return out

# ################################################################################################################################
# ################################################################################################################################
