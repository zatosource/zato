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
from sqlalchemy import and_, bindparam, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.audit_log.bulk_insert import insert_pending_events
from zato.common.db_env.commit_queue import CommitQueue
from zato.common.db_env.engine import call_database
from zato.common.db_env.errors import is_conflict, is_lock_timeout, is_value_error
from zato.common.db_env.outage import OutageTracker
from zato.common.db_env.pg8000_copy import copy_rows
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.audit_events import collect_audit_events, drop_audit_events, prepare_audit_payloads
from zato.common.pubsub.sql.config import get_commit_max_messages, get_commits_in_flight, Urgent_Commits_In_Flight
from zato.common.pubsub.sql.dedup import get_existing_fingerprints, rewrite_fingerprints, write_dedup_records
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID, PubSubTopicUnavailable
from zato.common.pubsub.sql.fenced_ack import check_fenced, delete_fenced, PubSubAckConflict
from zato.common.pubsub.sql.payloads import drop_payloads, get_chunks, get_message_ids
from zato.common.pubsub.sql.pending import PendingAck, PendingAtomic, PendingAttempts, PendingPublication, PendingSync, \
    new_pending_sync, reset_item
from zato.common.pubsub.sql.pull import lease_messages
from zato.common.pubsub.sql.schema import delivery_table, message_table, topic_sub_table
from zato.common.pubsub.sql.subscription_sync import apply_syncs, set_lock_timeout

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Connection, Engine
    from zato.common.audit_log.api import AuditLog
    from zato.common.pubsub.sql.pending import PendingLease, pending_ack_list, pending_atomic_list, pending_attempts_list, \
        pending_lease_list, pending_publication_list, pending_sync_list
    from zato.common.pubsub.subscription_list import pairlist
    from zato.common.typing_ import any_, anydict, anylist, intlist, strlist
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
    pending_sync_list = pending_sync_list
    pairlist = pairlist
    SubscriptionList = SubscriptionList
    noneiter = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# A publication refers to one message.
_publication_weight = 1

# The actions on the rows of a topic during which the topic refuses new publications.
Topic_Action_Delete = 'deleted'
Topic_Action_Rename = 'renamed'

# How many times a group commit is run again after PostgreSQL rolled it back on a conflict with concurrent transactions.
_max_conflict_retries = 5

# From how many delivery rows on, a commit writes them with COPY rather than with multi-row inserts.
_copy_min_delivery_rows = 200

# ################################################################################################################################
# ################################################################################################################################

# The statements of a group commit are built once here, the bind parameters take their values at execution time.
_subscribers_query = select(topic_sub_table.c.topic_name, topic_sub_table.c.sub_key)
_subscribers_query = _subscribers_query.where(
    topic_sub_table.c.topic_name.in_(bindparam('write_topic_names', expanding=True)))

# An unsubscription deletes the subscription row and only then the pending deliveries,
# so its delete must wait until each publication that read the row has committed its deliveries.
_subscribers_query_plain = PlainStatement(_subscribers_query.with_for_update(read=True, key_share=True))

# The row of a pair pending in the subscription list, which a publication inserts in its own commit,
# leaving a row that a concurrent transaction committed first as it is.
_topic_sub_insert = postgresql_insert(topic_sub_table).on_conflict_do_nothing()
_topic_sub_insert_plain = PlainStatement(_topic_sub_insert)

# A message whose identifier exists already is not inserted, and the statement returns the messages it inserted ..
_message_insert = postgresql_insert(message_table).on_conflict_do_nothing(index_elements=[message_table.c.msg_id])
_message_insert = _message_insert.returning(message_table.c.id, message_table.c.msg_id)
_message_insert_plain = PlainStatement(_message_insert)

# .. and what a message that exists already was published with tells a repeated publication from a different message.
_existing_messages_query = select(message_table.c.msg_id, message_table.c.topic_name, message_table.c.payload_crc32)
_existing_messages_query = _existing_messages_query.where(
    message_table.c.msg_id.in_(bindparam('write_msg_ids', expanding=True)))

_delivery_insert = PlainStatement(delivery_table.insert())

# The subscriber column is concatenated with an empty string, which keeps the query planner from looking the rows up
# through an index of subscribers, whose queues may be deep, rather than through the index of messages.
_unindexed_sub_key = delivery_table.c.sub_key.concat('')

_ack_deliveries_query = select(delivery_table.c.id, delivery_table.c.sub_key, delivery_table.c.message_id)
_ack_deliveries_query_plain = PlainStatement(_ack_deliveries_query.where(and_(
    delivery_table.c.message_id.in_(bindparam('ack_message_ids', expanding=True)),
    _unindexed_sub_key.in_(bindparam('ack_sub_keys', expanding=True)),
)))

# A concurrent commit may have removed some of the rows first, so the statement returns those it removed.
_delivery_delete = delivery_table.delete().where(delivery_table.c.id.in_(bindparam('ack_delivery_ids', expanding=True)))
_delivery_delete_plain = PlainStatement(_delivery_delete.returning(delivery_table.c.id))

# What records the next push attempt of each delivery row of a batch and returns the numbers of the rows that remain.
_record_attempts_statement = delivery_table.update()
_record_attempts_statement = _record_attempts_statement.where(
    delivery_table.c.id.in_(bindparam('attempt_delivery_ids', expanding=True)))
_record_attempts_statement = _record_attempts_statement.values(attempt=delivery_table.c.attempt + 1)
_record_attempts_statement = _record_attempts_statement.returning(delivery_table.c.id, delivery_table.c.attempt)
_record_attempts_statement_plain = PlainStatement(_record_attempts_statement)

# ################################################################################################################################
# ################################################################################################################################

class PubSubWriter:
    """ Writes the publications, acknowledgements and pulls of concurrent callers in shared transactions.
    Each caller waits until the transaction with its item is committed.
    A transaction writes publications first, acknowledgements next and pulls last, and its size is limited
    by the number of messages it refers to. Publications also have a commit reserved for them,
    so that a publisher does not wait for the acknowledgements of deep queues being committed.
    The audit events of the items commit in the transaction of the items.
    """

    def __init__(self, audit_log:'AuditLog', subscription_list:'SubscriptionList') -> 'None':

        # The audit log whose events commit in the transactions of the items
        self.audit_log = audit_log

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

    def _write_batch(self, batch:'anylist') -> 'None':
        """ Writes all the items of one batch.
        """
        engine = get_database_engine()

        # The audit events of the batch commit in its transaction, unless the audit log was turned off after they were built ..
        if not self.audit_log.prepare_commit():
            drop_audit_events(batch)

        # .. with the payloads of those built already prepared before the transaction begins ..
        prepare = partial(prepare_audit_payloads, batch)

        try:
            audit_events = call_database(engine, self._write_items, engine, batch, prepare=prepare)
        except DBAPIError:
            self._outage.on_failure()
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
        with their publications after them, its push attempts, its pulls and the audit events of all of them last,
        in one transaction. Returns the audit events written.
        """
        publications:'pending_publication_list' = []
        acks:'pending_ack_list' = []
        atomics:'pending_atomic_list' = []
        attempts_list:'pending_attempts_list' = []
        leases:'pending_lease_list' = []
        syncs:'pending_sync_list' = []

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
            else:
                leases.append(item)

        # Each acknowledged message, with the acknowledgement that its full delivery counts towards
        ack_by_message_id:'anydict' = {}

        # The pairs of the subscription list whose rows the publications insert
        added_pairs:'pairlist' = []

        with engine.begin() as connection:

            # Every pub/sub transaction waits for a lock only up to the lock timeout of pub/sub ..
            set_lock_timeout(connection)

            # .. the pairs of the subscription list are written first so that the publications of the same commit see their rows ..
            if syncs:
                apply_syncs(connection, syncs)

            if publications:
                self._insert_publications(connection, publications, added_pairs)

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

            # .. the payloads are dropped after all the writes of delivery rows. Dropping one holds the delivery rows
            # of the other subscribers of its message until the commit, so a transaction that locked a delivery row
            # after a drop could wait for one that waits for it in turn ..
            if ack_by_message_id:
                self._drop_payloads(connection, ack_by_message_id)

            # .. and the audit events of what was written commit with it.
            out = collect_audit_events(publications, atomics, leases)

            if out:
                _ = insert_pending_events(connection, out)

        # The rows that the publications and the syncs wrote count as committed only now that the transaction committed.
        if added_pairs:
            self.subscription_list.mark_committed(added_pairs)

        for sync in syncs:
            if sync.committed_added or sync.committed_removed:
                self.subscription_list.mark_committed(sync.committed_added, sync.committed_removed)

        return out

# ################################################################################################################################

    def _write_atomic(
        self,
        connection:'Connection',
        atomic:'PendingAtomic',
        ack_by_message_id:'anydict',
        added_pairs:'pairlist',
        ) -> 'None':
        """ Writes a fenced acknowledgement with its publications in the caller's transaction. Each reason for which
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
                self._insert_publications(connection, atomic.publications, added_pairs)

            if atomic.is_strict:
                for pending in atomic.publications:
                    if pending.exception:
                        raise pending.exception

            delete_fenced(connection, atomic.ack, fenced_rows)

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

    def _get_subscribers(
        self,
        connection:'Connection',
        publications:'pending_publication_list',
        added_pairs:'pairlist',
        ) -> 'anydict':
        """ Returns the subscriber keys of each topic the publications go to, decided by the subscription list
        from the rows read and locked within the caller's transaction, and inserts the rows of the pending pairs.
        """
        topic_names:'anylist' = []

        for pending in publications:
            topic_name = pending.message_values['topic_name']

            if topic_name not in topic_names:
                topic_names.append(topic_name)

        row_sub_keys:'anydict' = {}

        for topic_name in topic_names:
            row_sub_keys[topic_name] = []

        # The rows of the topics are locked first ..
        for row in _subscribers_query_plain.execute(connection, {'write_topic_names': topic_names}):
            row_sub_keys[row.topic_name].append(row.sub_key)

        # .. the subscription list decides the subscribers of each topic only under that lock ..
        out:'anydict' = {}
        topic_sub_rows:'anylist' = []

        for topic_name in topic_names:
            sub_keys, added = self.subscription_list.decide_subscribers(topic_name, row_sub_keys[topic_name])

            if sub_keys:
                out[topic_name] = sub_keys

            for sub_key, added_topic_name in added:
                topic_sub_rows.append({'sub_key': sub_key, 'topic_name': added_topic_name})

            added_pairs.extend(added)

        # .. and the pending pairs receive their rows in the same commit as the messages.
        if topic_sub_rows:
            _ = _topic_sub_insert_plain.insert_rows(connection, topic_sub_rows)

        return out

# ################################################################################################################################

    def _resolve_duplicates(self, connection:'Connection', duplicates:'pending_publication_list') -> 'None':
        """ Decides about each publication whose message identifier exists already. A message with the same topic
        and payload is a publication repeated after its outcome was unknown to its publisher, which receives
        the original result again, and any other message fails its own publisher alone.
        """
        msg_ids:'strlist' = []

        for pending in duplicates:
            msg_ids.append(pending.message_values['msg_id'])

        existing:'anydict' = {}

        for chunk in get_chunks(msg_ids):
            for row in connection.execute(_existing_messages_query, {'write_msg_ids': chunk}):
                existing[row.msg_id] = row

        for pending in duplicates:

            message_values = pending.message_values
            msg_id = message_values['msg_id']
            row = existing.get(msg_id)

            # The cleanup removed the existing message after the insert met it, which happens only to a message
            # that was published and fully processed, so this one is its repetition.
            if row is None:
                logger.info('Repeated publication of a removed message -> msg_id:%s', msg_id)
                pending.is_repeat = True
                continue

            is_same_topic = row.topic_name == message_values['topic_name']
            is_same_payload = row.payload_crc32 == message_values['payload_crc32']

            if is_same_topic and is_same_payload:
                logger.info('Repeated publication of an existing message -> msg_id:%s', msg_id)
                pending.is_repeat = True
            else:
                message = f'Message ID `{msg_id}` belongs to a different message that exists already'
                pending.exception = PubSubDuplicateMsgID(message)

# ################################################################################################################################

    def _insert_deliveries(self, connection:'Connection', delivery_rows:'anylist') -> 'None':
        """ Inserts delivery rows with multi-row inserts or, when there are many of them, with COPY.
        """
        delivery_row_count = len(delivery_rows)

        if delivery_row_count >= _copy_min_delivery_rows:
            copy_rows(connection, delivery_table, delivery_rows)
        else:
            _ = _delivery_insert.insert_rows(connection, delivery_rows)

# ################################################################################################################################

    def _insert_publications(
        self,
        connection:'Connection',
        publications:'pending_publication_list',
        added_pairs:'pairlist',
        ) -> 'None':
        """ Writes the dedup records of the publications, then inserts the messages of those whose dedup records
        were written and one delivery row per message and subscriber.
        """

        # A publication whose dedup record remains from an earlier one inserts nothing ..
        publications = write_dedup_records(connection, publications)

        if not publications:
            return

        # .. the subscribers as of this very commit ..
        subscribers = self._get_subscribers(connection, publications, added_pairs)

        message_rows:'anylist' = []

        for pending in publications:

            message_values = pending.message_values
            topic_name = message_values['topic_name']

            # .. a topic without subscribers has its messages stored without their payloads ..
            if topic_name in subscribers:
                pending.subscriber_keys = subscribers[topic_name]
            else:
                pending.subscriber_keys = []
                message_values['payload'] = None
                message_values['payload_encrypted'] = False

            message_rows.append(message_values)

        # .. all the messages go in one statement, which returns the primary keys of those it inserted ..
        inserted:'anydict' = {}

        for row in _message_insert_plain.insert_rows(connection, message_rows):
            inserted[row.msg_id] = row.id

        # .. a message that was not inserted has an identifier that exists already ..
        delivery_rows:'anylist' = []
        duplicates:'pending_publication_list' = []

        for pending in publications:

            message_values = pending.message_values
            msg_id = message_values['msg_id']

            # .. only the first publication of an identifier within a commit can have inserted it ..
            if msg_id not in inserted:
                pending.subscriber_keys = []
                duplicates.append(pending)
                continue

            message_id = inserted.pop(msg_id)

            for sub_key in pending.subscriber_keys:
                delivery_rows.append({
                    'message_id': message_id,
                    'sub_key': sub_key,
                    'topic_name': message_values['topic_name'],
                    'priority': message_values['priority'],
                    'expiration_ms': message_values['expiration_ms'],
                })

        # .. a message that met a stored one under the same ID gives its dedup record the fingerprint of the stored one ..
        if duplicates:
            self._resolve_duplicates(connection, duplicates)
            rewrite_fingerprints(connection, duplicates)

        # .. and all the delivery rows go in one statement too.
        if delivery_rows:
            self._insert_deliveries(connection, delivery_rows)

# ################################################################################################################################

    def _resolve_ack_message_ids(self, connection:'Connection', acks:'pending_ack_list') -> 'anylist':
        """ Returns the primary keys of the messages of each acknowledgement, in the order of the acknowledgements,
        looking up the keys of those that were given public identifiers alone.
        """
        lookup_msg_ids:'strlist' = []

        for pending in acks:
            if pending.sequence_ids is None:
                lookup_msg_ids.extend(pending.msg_ids)

        if lookup_msg_ids:
            found = get_message_ids(connection, lookup_msg_ids)
        else:
            found = {}

        out:'anylist' = []

        for pending in acks:

            if pending.sequence_ids is None:
                message_ids:'intlist' = []

                for msg_id in pending.msg_ids:
                    if message_id := found.get(msg_id):
                        message_ids.append(message_id)

            else:
                message_ids = pending.sequence_ids

            out.append(message_ids)

        return out

# ################################################################################################################################

    def _delete_acks(self, connection:'Connection', acks:'pending_ack_list', ack_by_message_id:'anydict') -> 'None':
        """ Removes the delivery rows the acknowledgements are about and records each of their messages with the
        acknowledgement that its full delivery counts towards. A row that two acknowledgements of one commit are about
        counts towards the first of them, and a message counts towards the last acknowledgement that removed one
        of its rows, or, with no such acknowledgement, the first one that was about it.
        """
        message_ids_by_ack = self._resolve_ack_message_ids(connection, acks)

        all_message_ids:'anylist' = []
        sub_keys:'strlist' = []
        acked_pairs:'set[tuple[str, int]]' = set()

        for pending, message_ids in zip(acks, message_ids_by_ack):
            all_message_ids.extend(message_ids)

            if pending.sub_key not in sub_keys:
                sub_keys.append(pending.sub_key)

            for message_id in message_ids:
                acked_pairs.add((pending.sub_key, message_id))

        if not all_message_ids:
            return

        # Read the delivery rows of the acknowledged messages that belong to the acknowledging subscribers.
        # The query matches every subscriber of the commit with every message of the commit, so a row
        # of a subscriber that did not acknowledge that particular message is still pending and stays in place ..
        delivery_ids_by_pair:'anydict' = {}

        for chunk in get_chunks(all_message_ids):

            parameters = {
                'ack_message_ids': chunk,
                'ack_sub_keys': sub_keys,
            }

            for row in _ack_deliveries_query_plain.execute(connection, parameters):
                pair = (row.sub_key, row.message_id)

                if pair in acked_pairs:
                    delivery_ids_by_pair[pair] = row.id

        # .. remove them, in the order of their keys, so that concurrent commits lock them in the same order,
        # learning which of them this commit removed ..
        delivery_ids = sorted(delivery_ids_by_pair.values())
        removed_ids:'set[int]' = set()

        for chunk in get_chunks(delivery_ids):
            for row in _delivery_delete_plain.execute(connection, {'ack_delivery_ids': chunk}):
                removed_ids.add(row.id)

        # .. and assign each removed row to the acknowledgement that removed it.
        for pending, message_ids in zip(acks, message_ids_by_ack):
            for message_id in message_ids:

                pair = (pending.sub_key, message_id)
                delivery_id = delivery_ids_by_pair.pop(pair, None)

                if delivery_id in removed_ids:
                    pending.removed_count += 1
                    ack_by_message_id[message_id] = pending

                elif message_id not in ack_by_message_id:
                    ack_by_message_id[message_id] = pending

# ################################################################################################################################

    def _drop_payloads(self, connection:'Connection', ack_by_message_id:'anydict') -> 'None':
        """ Drops the payloads of the acknowledged messages that no subscriber needs anymore, each counting
        as fully delivered towards its acknowledgement.
        """
        message_ids = list(ack_by_message_id)

        for message_id in drop_payloads(connection, message_ids):
            pending = ack_by_message_id[message_id]
            pending.fully_delivered_count += 1

# ################################################################################################################################
# ################################################################################################################################
