# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager
from functools import partial
from logging import getLogger
from threading import Condition

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.audit_log.bulk_insert import insert_pending_events
from zato.common.db_env.any_of import any_of
from zato.common.db_env.commit_queue import CommitQueue
from zato.common.db_env.engine import call_database
from zato.common.db_env.errors import is_conflict, is_lock_timeout, is_value_error
from zato.common.db_env.outage import OutageTracker
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.ack_deletes import AckDeletes
from zato.common.pubsub.sql.audit_events import collect_audit_events, drop_audit_events, prepare_batch_payloads
from zato.common.pubsub.sql.clock import get_engine_clock
from zato.common.pubsub.sql.config import get_commit_max_messages, get_commits_in_flight, Urgent_Commits_In_Flight
from zato.common.pubsub.sql.dedup import get_existing_fingerprints
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID, PubSubTopicUnavailable
from zato.common.pubsub.sql.fenced_ack import check_fenced, delete_fenced, PubSubAckConflict
from zato.common.pubsub.sql.payloads import update_message_payload
from zato.common.pubsub.sql.pending import PendingAck, PendingAtomic, PendingAttempts, PendingPublication, PendingSync, \
    PendingUpdate, new_pending_sync, reset_item
from zato.common.pubsub.sql.publication_inserts import PublicationInserts
from zato.common.pubsub.sql.pull import claim_messages, lease_messages
from zato.common.pubsub.sql.schema import delivery_table
from zato.common.pubsub.sql.subscription_sync import apply_syncs, set_lock_timeout

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Connection, Engine
    from zato.common.audit_log.api import AuditLog
    from zato.common.pubsub.sql.fast_path import FastPath, FastPathClaims
    from zato.common.pubsub.sql.pending import PendingLease, pending_ack_list, pending_atomic_list, pending_attempts_list, \
        pending_lease_list, pending_publication_list, pending_sync_list, pending_update_list
    from zato.common.pubsub.subscription_list import pairlist
    from zato.common.typing_ import any_, anydict, anylist, strlist, strstrdict
    from zato_common_core.zato_common_core import SubscriptionList

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict
    AuditLog = AuditLog
    Connection = Connection
    Engine = Engine
    PendingLease = PendingLease
    pending_ack_list = pending_ack_list
    pending_atomic_list = pending_atomic_list
    pending_attempts_list = pending_attempts_list
    pending_lease_list = pending_lease_list
    pending_publication_list = pending_publication_list
    strstrdict = strstrdict
    pending_sync_list = pending_sync_list
    pending_update_list = pending_update_list
    pairlist = pairlist
    SubscriptionList = SubscriptionList
    noneiter = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# A publication refers to one message, and so does the replacement of a payload.
_publication_weight = 1
_update_weight      = 1

# The actions on the rows of a topic during which the topic refuses new publications.
Topic_Action_Delete = 'deleted'
Topic_Action_Rename = 'renamed'

# How many times a group commit is run again after PostgreSQL rolled it back on a conflict with concurrent transactions.
_max_conflict_retries = 5

# ################################################################################################################################
# ################################################################################################################################

# What records the next push attempt of each delivery row of a batch and returns the numbers of the rows that remain.
_record_attempts_statement = delivery_table.update()
_record_attempts_statement = _record_attempts_statement.where(
    any_of(delivery_table.c.id, 'attempt_delivery_ids'))
_record_attempts_statement = _record_attempts_statement.values(attempt=delivery_table.c.attempt + 1)
_record_attempts_statement = _record_attempts_statement.returning(delivery_table.c.id, delivery_table.c.attempt)
_record_attempts_statement_plain = PlainStatement(_record_attempts_statement)

# ################################################################################################################################
# ################################################################################################################################

class PubSubWriter(PublicationInserts, AckDeletes):
    """ Writes the publications, acknowledgements and pulls of concurrent callers in shared transactions.
    Each caller waits until the transaction with its item is committed.
    A transaction writes publications first, acknowledgements next and pulls last, and its size is limited
    by the number of messages it refers to. Publications also have a commit reserved for them,
    so that a publisher does not wait for the acknowledgements of deep queues being committed.
    The audit events of the items commit in the transaction of the items.
    """

    def __init__(self, audit_log:'AuditLog', subscription_list:'SubscriptionList', fast_path:'FastPath') -> 'None':

        # The audit log whose events commit in the transactions of the items
        self.audit_log = audit_log

        # The waiting pulls and the idle push greenlets that the publications of a commit claim
        self.fast_path = fast_path

        # The subscriber and topic pairs of the configuration database, which publications read once they hold the lock on the rows of their topics
        self.subscription_list = subscription_list

        commit_max_messages = get_commit_max_messages()
        commits_in_flight = get_commits_in_flight()

        self._commit_queue = CommitQueue(
            write_batch=self._write_batch,
            max_weight=commit_max_messages,
            max_in_flight=commits_in_flight,
            max_urgent_in_flight=Urgent_Commits_In_Flight,
        )

        self._outage = OutageTracker('Pub/sub commit writer')

        # The actions in progress on the rows of each topic, during which the topic refuses new publications ..
        self._topic_changes:'anydict' = {}

        # .. the number of publications of each topic accepted and not yet committed or failed ..
        self._topic_publications:'anydict' = {}

        # .. and what guards both of them.
        self._topic_condition = Condition()

# ################################################################################################################################

    def _get_topic_names(self, publications:'pending_publication_list') -> 'strlist':
        """ Returns the names of the topics the publications go to, each once.
        """
        out:'strlist' = []

        for pending in publications:
            topic_name = pending.message_values['topic_name']

            if topic_name not in out:
                out.append(topic_name)

        return out

# ################################################################################################################################

    def _accept_publications(self, topic_names:'strlist') -> 'None':
        """ Counts the publications of the given topics as accepted, unless the rows of any of the topics
        are being deleted or renamed.
        """
        with self._topic_condition:

            for topic_name in topic_names:
                if topic_name in self._topic_changes:
                    action = self._topic_changes[topic_name][-1]
                    raise PubSubTopicUnavailable(f'Topic `{topic_name}` is being {action}')

            for topic_name in topic_names:
                if topic_name in self._topic_publications:
                    self._topic_publications[topic_name] += 1
                else:
                    self._topic_publications[topic_name] = 1

# ################################################################################################################################

    def _release_publications(self, topic_names:'strlist') -> 'None':
        """ Stops counting the publications of the given topics once they are committed or failed,
        and wakes up the deletes and renames that wait for them.
        """
        with self._topic_condition:

            for topic_name in topic_names:
                self._topic_publications[topic_name] -= 1

                if self._topic_publications[topic_name] == 0:
                    del self._topic_publications[topic_name]

            self._topic_condition.notify_all()

# ################################################################################################################################

    @contextmanager
    def changing_topic(self, topic_name:'str', action:'str') -> 'noneiter':
        """ Refuses new publications of a topic and waits until each one accepted earlier is committed or failed,
        so that the rows the block deletes or renames include those of every publication that will ever commit
        under the topic's name, and new publications are refused until the block ends.
        """
        with self._topic_condition:

            if topic_name in self._topic_changes:
                self._topic_changes[topic_name].append(action)
            else:
                self._topic_changes[topic_name] = [action]

            while topic_name in self._topic_publications:
                _ = self._topic_condition.wait()

        try:
            yield

        finally:
            with self._topic_condition:
                actions = self._topic_changes[topic_name]
                actions.remove(action)

                if not actions:
                    del self._topic_changes[topic_name]

# ################################################################################################################################

    def publish(self, pending:'PendingPublication') -> 'None':
        """ Writes one message together with its delivery rows.
        """
        topic_names = [pending.message_values['topic_name']]
        self._accept_publications(topic_names)

        try:
            self._commit_queue.write(pending, weight=_publication_weight, is_urgent=True)
        finally:
            self._release_publications(topic_names)

        if pending.exception:
            raise pending.exception

# ################################################################################################################################

    def ack(self, pending:'PendingAck') -> 'None':
        """ Removes a subscriber's delivery rows of the given messages and drops the payloads
        of the messages that no subscriber needs anymore.
        """
        weight = len(pending.msg_ids)
        self._commit_queue.write(pending, weight=weight, is_urgent=False)

        if pending.exception:
            raise pending.exception

# ################################################################################################################################

    def ack_atomic(self, pending:'PendingAtomic') -> 'None':
        """ Writes a fenced acknowledgement with its publications, all of them or none, in a commit that may be shared
        with other callers, none of whom shares the outcome of this item.
        """
        weight = len(pending.ack.msg_ids) + len(pending.publications)

        # A claim refers to as many messages as it may claim
        if pending.claim:
            weight += pending.claim.max_messages

        topic_names = self._get_topic_names(pending.publications)
        self._accept_publications(topic_names)

        try:
            self._commit_queue.write(pending, weight=weight, is_urgent=False)
        finally:
            self._release_publications(topic_names)

        if pending.exception:
            raise pending.exception

# ################################################################################################################################

    def lease(self, pending:'PendingLease') -> 'None':
        """ Leases a subscriber's deliverable messages to one pulling client.
        """
        self._commit_queue.write(pending, weight=pending.max_messages, is_urgent=False)

        if pending.exception:
            raise pending.exception

# ################################################################################################################################

    def record_attempts(self, pending:'PendingAttempts') -> 'None':
        """ Records the next push attempt of each delivery of a batch before its requests are sent.
        """
        weight = len(pending.delivery_ids)
        self._commit_queue.write(pending, weight=weight, is_urgent=False)

        if pending.exception:
            raise pending.exception

# ################################################################################################################################

    def sync_pairs(self, added:'pairlist', removed:'pairlist') -> 'None':
        """ Inserts and deletes the governed pairs of the subscription list in one transaction of the commit queue.
        """
        pending = new_pending_sync(added, removed)
        pair_count = len(added) + len(removed)

        if pair_count < 1:
            pair_count = 1

        self._commit_queue.write(pending, weight=pair_count, is_urgent=False)

        if pending.exception:
            raise pending.exception

# ################################################################################################################################

    def update(self, pending:'PendingUpdate') -> 'None':
        """ Replaces the payload of one message, storing the new payload in the payload table of the commit.
        """
        self._commit_queue.write(pending, weight=_update_weight, is_urgent=False)

        if pending.exception:
            raise pending.exception

# ################################################################################################################################

    def _write_batch(self, batch:'anylist') -> 'None':
        """ Writes all the items of one batch.
        """
        engine = get_database_engine()

        # The audit events of the batch commit in its transaction, unless the audit log was turned off after they were built ..
        if not self.audit_log.prepare_commit():
            drop_audit_events(batch)

        # .. with the payloads of those built already prepared before the transaction begins ..
        prepare = partial(prepare_batch_payloads, batch)

        try:
            audit_events = call_database(engine, self._write_items, engine, batch, prepare=prepare)
        except DBAPIError as e:
            self._outage.on_failure(e)
            raise

        self._outage.on_success()

        # .. and what follows their commit runs once the batch is committed.
        if audit_events:
            self.audit_log.complete_commit(audit_events)

# ################################################################################################################################

    def _write_items(self, engine:'Engine', batch:'anylist') -> 'anylist':
        """ Writes the items of a batch in one transaction, which PostgreSQL may roll back as a whole on a conflict
        with concurrent transactions, in which case nothing of it was committed and it runs again.
        Returns the audit events that were committed.
        """
        attempt = 0

        while True:
            try:
                out = self._write_transaction(engine, batch)
                break

            except DBAPIError as e:

                # A value of one item that the database rejects, or a lock that one item waits for past the timeout,
                # fails the whole commit, so each item of the batch is written again in a transaction of its own
                # and only the caller of the item at fault receives the error ..
                if len(batch) > 1:
                    if is_value_error(e) or is_lock_timeout(e):
                        logger.info(
                            'Pub/sub commit split after a rejected value or a lock timeout, writing its %d items one by one -> %s',
                            len(batch), e.orig)
                        out = self._write_items_one_by_one(engine, batch)
                        break

                attempt += 1

                if attempt > _max_conflict_retries or not is_conflict(e):
                    raise

                logger.info('Pub/sub commit rolled back on a conflict, running it again -> attempt:%d, %s', attempt, e.orig)

                for item in batch:
                    reset_item(item)

        return out

# ################################################################################################################################

    def _write_items_one_by_one(self, engine:'Engine', batch:'anylist') -> 'anylist':
        """ Writes each item of a batch in a transaction of its own, storing in an item the error
        of a value that the database rejected in it. Returns the audit events that were committed.
        """
        out:'anylist' = []

        for item in batch:
            reset_item(item)

            try:
                audit_events = self._write_items(engine, [item])
                out.extend(audit_events)
            except DBAPIError as e:
                if is_value_error(e) or is_lock_timeout(e):
                    item.exception = e
                else:
                    raise

        return out

# ################################################################################################################################

    def _write_transaction(self, engine:'Engine', batch:'anylist') -> 'anylist':
        """ Writes the publications of a batch first, its acknowledgements next, its fenced acknowledgements
        with their publications after them, its push attempts, its pulls, its replacements of payloads
        and the audit events of all of them last,
        in one transaction. Returns the audit events written.
        """
        publications:'pending_publication_list' = []
        acks:'pending_ack_list' = []
        atomics:'pending_atomic_list' = []
        attempts_list:'pending_attempts_list' = []
        leases:'pending_lease_list' = []
        syncs:'pending_sync_list' = []
        updates:'pending_update_list' = []

        for item in batch:
            if isinstance(item, PendingPublication):
                publications.append(item)
            elif isinstance(item, PendingAck):
                acks.append(item)
            elif isinstance(item, PendingAtomic):
                atomics.append(item)
            elif isinstance(item, PendingAttempts):
                attempts_list.append(item)
            elif isinstance(item, PendingSync):
                syncs.append(item)
            elif isinstance(item, PendingUpdate):
                updates.append(item)
            else:
                leases.append(item)

        # Each acknowledged message, with the acknowledgement that its full delivery counts towards
        ack_by_message_id:'anydict' = {}

        # The pairs of the subscription list whose rows the publications insert
        added_pairs:'pairlist' = []

        # The waiting pulls and the idle push greenlets that the publications claim, which a transaction
        # that does not commit releases
        claims = self.fast_path.new_claims()

        try:
            out = self._write_transaction_items(
                engine, claims, publications, acks, atomics, attempts_list, leases, syncs, updates,
                ack_by_message_id, added_pairs)

        except BaseException:
            self.fast_path.release(claims)
            raise

        # The pulls and the push greenlets that the publications claimed are handed their messages now that they committed ..
        self.fast_path.mark_committed(claims)

        # .. and the rows that the publications and the syncs wrote count as committed too.
        if added_pairs:
            self.subscription_list.mark_committed(added_pairs)

        for sync in syncs:
            if sync.committed_added or sync.committed_removed:
                self.subscription_list.mark_committed(sync.committed_added, sync.committed_removed)

        return out

# ################################################################################################################################

    def _write_transaction_items(
        self,
        engine:'Engine',
        claims:'FastPathClaims',
        publications:'pending_publication_list',
        acks:'pending_ack_list',
        atomics:'pending_atomic_list',
        attempts_list:'pending_attempts_list',
        leases:'pending_lease_list',
        syncs:'pending_sync_list',
        updates:'pending_update_list',
        ack_by_message_id:'anydict',
        added_pairs:'pairlist',
        ) -> 'anylist':
        """ Writes the items of a batch, grouped by their kinds, in one transaction, and returns the audit events written.
        """
        with engine.begin() as connection:

            # Every pub/sub transaction waits for a lock only up to the lock timeout of pub/sub ..
            set_lock_timeout(connection)

            # .. the pairs of the subscription list are written first so that the publications of the same commit see their rows ..
            if syncs:
                apply_syncs(connection, syncs)

            if publications:
                self._insert_publications(connection, publications, added_pairs, claims)

            if acks:
                self._delete_acks(connection, acks, ack_by_message_id)

            # .. each fenced acknowledgement commits with its publications or not at all, without failing the others ..
            for atomic in atomics:
                self._write_atomic(connection, atomic, ack_by_message_id, added_pairs)

            # .. a push attempt is recorded only for a delivery that this transaction has not acknowledged ..
            for attempts in attempts_list:
                parameters = {'attempt_delivery_ids': attempts.delivery_ids}
                for row in _record_attempts_statement_plain.execute(connection, parameters):
                    attempts.attempts[row.id] = row.attempt

            # .. a pull leases nothing that this transaction has acknowledged already ..
            for lease in leases:
                rows, attempts = lease_messages(
                    connection, self.subscription_list, lease.sub_key, lease.max_messages, lease.max_len, lease.now_ms, lease.leased_until_ms)
                lease.rows = rows
                lease.attempts = attempts
                lease.on_leased(lease)

            # .. a payload is replaced before the drops, so that a message which this transaction leaves without
            # .. a delivery row drops its new payload rather than keeping it ..
            for update in updates:
                update.is_updated = update_message_payload(connection, update)

            # .. the payloads are dropped after all the writes of delivery rows. Dropping one holds the delivery rows
            # of the other subscribers of its message until the commit, so a transaction that locked a delivery row
            # after a drop could wait for one that waits for it in turn ..
            if ack_by_message_id:
                self._drop_payloads(connection, ack_by_message_id)

            # .. and the audit events of what was written commit with it, including the receptions of the pulls
            # .. that the publications claimed.
            all_leases = leases + claims.leases
            out = collect_audit_events(publications, atomics, all_leases)

            if out:
                _ = insert_pending_events(connection, out)

        return out

# ################################################################################################################################

    def _write_atomic(
        self,
        connection:'Connection',
        atomic:'PendingAtomic',
        ack_by_message_id:'anydict',
        added_pairs:'pairlist',
        ) -> 'None':
        """ Writes a fenced acknowledgement with its publications, and the claim of the next batch of its push subscriber,
        if it has one, in the caller's transaction. Each reason for which
        the item fails is checked before anything of it is written, so that an item that fails writes nothing,
        and the item is also enclosed in a savepoint, against a concurrent commit that changes
        what the checks read before the item is written.
        """
        savepoint = connection.begin_nested()

        # The checks write nothing, so an item that fails them is only marked as failed ..
        try:
            has_new_message = self._check_atomic_publications(connection, atomic)
            fenced_rows = check_fenced(connection, atomic.ack, has_new_message)

        except (PubSubAckConflict, PubSubDuplicateMsgID) as e:
            savepoint.rollback()
            atomic.exception = e
            return

        # .. whereas after the first write of an item, only a savepoint can undo it on its own.
        try:
            if atomic.publications:
                self._insert_publications(connection, atomic.publications, added_pairs, None)

            if atomic.is_strict:
                for pending in atomic.publications:
                    if pending.exception:
                        raise pending.exception

            delete_fenced(connection, atomic.ack, fenced_rows)

            # .. the next batch of a push subscriber is claimed only once its acknowledgement is written,
            # .. so that a batch whose acknowledgement failed is claimed again before any message behind it ..
            if claim := atomic.claim:
                clock = get_engine_clock(connection.engine)
                now_ms = clock.now_ms()
                claim.rows = claim_messages(connection, self.subscription_list, claim.sub_key, claim.max_messages,
                    claim.max_len, now_ms)

        except (PubSubAckConflict, PubSubDuplicateMsgID) as e:
            savepoint.rollback()
            reset_item(atomic)
            atomic.exception = e
            return

        savepoint.commit()

        # The full delivery of a message counts towards the last acknowledgement that removed one of its rows
        for message_id in fenced_rows.message_ids:
            ack_by_message_id[message_id] = atomic.ack

# ################################################################################################################################

    def _check_atomic_publications(self, connection:'Connection', atomic:'PendingAtomic') -> 'bool':
        """ Fails a strict item with PubSubDuplicateMsgID if a publication's message ID stands for a different message,
        either one that exists already or one published earlier in the same item. Returns whether any publication
        is to insert a new message, as opposed to only repeating existing ones.
        """
        # What each message ID stands for already, by its dedup record or by its stored message
        existing = get_existing_fingerprints(connection, atomic.publications)

        out = False

        for pending in atomic.publications:

            msg_id = pending.message_values['msg_id']

            # A message ID that nothing stands for yet inserts a new message ..
            if msg_id not in existing:
                existing[msg_id] = pending.fingerprint
                out = True
                continue

            # .. one that stands for the same content repeats it, and one that stands for different content
            # .. fails a strict item, while otherwise the publication alone is not written.
            if existing[msg_id] != pending.fingerprint:
                if atomic.is_strict:
                    message = f'Message ID `{msg_id}` belongs to a different message that exists already'
                    raise PubSubDuplicateMsgID(message)

        return out

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
