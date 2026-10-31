# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, bindparam, exists, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.db_env.commit_queue import CommitQueue
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite
from zato.common.db_env.engine import call_database
from zato.common.db_env.errors import is_conflict
from zato.common.db_env.pg8000_copy import copy_rows
from zato.common.pubsub.sql.config import get_batch_size, get_commit_max_messages, get_commits_in_flight, \
    get_pubsub_engine
from zato.common.pubsub.sql.schema import delivery_table, message_table, topic_sub_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import any_, anydict, anylist, intlist, intlistnone, strlist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict
    Connection = Connection
    Engine = Engine
    intlistnone = intlistnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
pending_publication_list = list['PendingPublication']
pending_ack_list         = list['PendingAck']

# A publication refers to one message.
_publication_weight = 1

# How many times a group commit is run again after PostgreSQL rolled it back on a conflict with concurrent transactions.
_max_conflict_retries = 5

# From how many delivery rows on, a commit writes them with COPY rather than with multi-row inserts on PostgreSQL.
_copy_min_delivery_rows = 1_000

# ################################################################################################################################
# ################################################################################################################################

class PubSubDuplicateMsgID(Exception):
    """ Raised to the publisher of a message whose identifier belongs to a different message that exists already.
    """

# ################################################################################################################################
# ################################################################################################################################

def drop_payloads(connection:'Connection', message_ids:'intlist') -> 'intlist':
    """ Sets the payload to NULL for each of the given messages that no subscriber needs anymore, in the caller's
    transaction, which has removed delivery rows of these messages before. Returns the messages it dropped
    the payloads of. The message rows are locked in the order of their keys, which every caller follows
    after its delivery rows, so concurrent transactions cannot deadlock on them.
    """
    message_ids = sorted(message_ids)
    is_postgresql = connection.dialect.name == Type_PostgreSQL

    out:'intlist' = []

    for chunk in _get_chunks(message_ids):

        parameters = {'drop_message_ids': chunk}

        if is_postgresql:
            _ = connection.execute(_lock_messages_query, parameters).fetchall()

        for row in connection.execute(_drop_payloads_statement, parameters):
            out.append(row.id)

    return out

# ################################################################################################################################
# ################################################################################################################################

# The statements of a group commit are built once here, the bind parameters take their values at execution time.
_subscribers_query = select(topic_sub_table.c.topic_name, topic_sub_table.c.sub_key)
_subscribers_query = _subscribers_query.where(
    topic_sub_table.c.topic_name.in_(bindparam('write_topic_names', expanding=True)))

# On PostgreSQL, an unsubscription deletes the subscription row and only then the pending deliveries,
# so its delete must wait until each publication that read the row has committed its deliveries.
_subscribers_query = _subscribers_query.with_for_update(read=True, key_share=True)

# A message whose identifier exists already is not inserted, and the statement returns the messages it inserted ..
_message_inserts:'anydict' = {}

for _dialect_name, _insert in ((Type_SQLite, sqlite_insert), (Type_PostgreSQL, postgresql_insert)):
    _message_insert = _insert(message_table)
    _message_insert = _message_insert.on_conflict_do_nothing(index_elements=[message_table.c.msg_id])
    _message_insert = _message_insert.returning(message_table.c.id, message_table.c.msg_id)
    _message_inserts[_dialect_name] = _message_insert

# .. and what a message that exists already was published with tells a repeated publication from a different message.
_existing_messages_query = select(message_table.c.msg_id, message_table.c.topic_name, message_table.c.payload_crc32)
_existing_messages_query = _existing_messages_query.where(
    message_table.c.msg_id.in_(bindparam('write_msg_ids', expanding=True)))

_delivery_insert = delivery_table.insert()

_message_ids_query = select(message_table.c.id, message_table.c.msg_id)
_message_ids_query = _message_ids_query.where(message_table.c.msg_id.in_(bindparam('write_msg_ids', expanding=True)))

# The subscriber column is concatenated with an empty string, which keeps SQLite from looking the rows up
# through an index of subscribers, whose queues may be deep, rather than through the index of messages.
_unindexed_sub_key = delivery_table.c.sub_key.concat('')

_ack_deliveries_query = select(delivery_table.c.id, delivery_table.c.sub_key, delivery_table.c.message_id)
_ack_deliveries_query = _ack_deliveries_query.where(and_(
    delivery_table.c.message_id.in_(bindparam('ack_message_ids', expanding=True)),
    _unindexed_sub_key.in_(bindparam('ack_sub_keys', expanding=True)),
))

# A concurrent commit on PostgreSQL may have removed some of the rows first, so the statement returns those it removed.
_delivery_delete = delivery_table.delete()
_delivery_delete = _delivery_delete.where(delivery_table.c.id.in_(bindparam('ack_delivery_ids', expanding=True)))
_delivery_delete = _delivery_delete.returning(delivery_table.c.id)

# A message is still in flight while any delivery row references it -
# the update drops the payloads of the given messages that have none left.
_still_needed = exists()
_still_needed = _still_needed.where(delivery_table.c.message_id == message_table.c.id)

_drop_payloads_statement = message_table.update()
_drop_payloads_statement = _drop_payloads_statement.where(and_(
    message_table.c.id.in_(bindparam('drop_message_ids', expanding=True)),
    message_table.c.payload.isnot(None),
    ~_still_needed,
))
_drop_payloads_statement = _drop_payloads_statement.values(payload=None, payload_encrypted=False)
_drop_payloads_statement = _drop_payloads_statement.returning(message_table.c.id)

# Two transactions of PostgreSQL that remove the last two delivery rows of a message would each see the row
# of the other one and both keep the payload, so the message rows are locked first, and the update that follows
# sees every removal committed by the time the lock is granted.
_lock_messages_query = select(message_table.c.id)
_lock_messages_query = _lock_messages_query.where(
    message_table.c.id.in_(bindparam('drop_message_ids', expanding=True)))
_lock_messages_query = _lock_messages_query.order_by(message_table.c.id)
_lock_messages_query = _lock_messages_query.with_for_update(key_share=True)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingPublication:
    """ One message to publish, with the subscribers it was published to once it is written.
    """

    # The values of the message row
    message_values: 'anydict'

    # The subscribers of the topic as of the commit that wrote the message
    subscriber_keys: 'strlist'

    # Why the message could not be written, while the other items of its commit could
    exception: 'BaseException | None'

# ################################################################################################################################

@dataclass(init=False)
class PendingAck:
    """ The acknowledgement of messages by one subscriber, with what it removed once it is written.
    """

    # Who acknowledges the messages and which ones, by their public identifiers and, when known, by their primary keys
    sub_key: 'str'
    msg_ids: 'strlist'
    sequence_ids: 'intlistnone'

    # How many of the subscriber's delivery rows it removed and how many of the messages became fully delivered
    removed_count: 'int'
    fully_delivered_count: 'int'

# ################################################################################################################################
# ################################################################################################################################

def new_pending_publication(message_values:'anydict') -> 'PendingPublication':
    """ Returns a publication that is yet to be written.
    """
    out = PendingPublication()
    out.message_values = message_values
    out.subscriber_keys = []
    out.exception = None

    return out

# ################################################################################################################################

def new_pending_ack(sub_key:'str', msg_ids:'strlist', sequence_ids:'intlistnone') -> 'PendingAck':
    """ Returns an acknowledgement that is yet to be written.
    """
    out = PendingAck()
    out.sub_key = sub_key
    out.msg_ids = msg_ids
    out.sequence_ids = sequence_ids
    out.removed_count = 0
    out.fully_delivered_count = 0

    return out

# ################################################################################################################################

def _reset_item(item:'PendingPublication | PendingAck') -> 'None':
    """ Clears what a commit that was rolled back stored in one of its items.
    """
    if isinstance(item, PendingPublication):
        item.subscriber_keys = []
        item.exception = None
    else:
        item.removed_count = 0
        item.fully_delivered_count = 0

# ################################################################################################################################

def _get_chunks(items:'anylist') -> 'anylist':
    """ Splits a list into parts no longer than one bulk statement may touch.
    """
    batch_size = get_batch_size()
    item_count = len(items)

    out:'anylist' = []

    for start in range(0, item_count, batch_size):
        end = start + batch_size
        chunk = items[start:end]
        out.append(chunk)

    return out

# ################################################################################################################################

def _get_message_ids(connection:'Connection', msg_ids:'strlist') -> 'anydict':
    """ Maps public message identifiers to their primary keys, read within the caller's transaction.
    """
    out:'anydict' = {}

    for chunk in _get_chunks(msg_ids):
        for row in connection.execute(_message_ids_query, {'write_msg_ids': chunk}):
            out[row.msg_id] = row.id

    return out

# ################################################################################################################################
# ################################################################################################################################

class PubSubWriter:
    """ Writes the publications and acknowledgements of concurrent callers in shared transactions,
    in the thread pool of the gevent hub on SQLite. Each caller waits until the transaction with its item is committed.
    Publications go into the next transaction ahead of acknowledgements, and the size of a transaction
    is limited by the number of messages it refers to, so that a publisher waits for at most one transaction
    of a bounded size, however many acknowledgements of deep queues are waiting.
    """

    def __init__(self) -> 'None':
        commit_max_messages = get_commit_max_messages()
        commits_in_flight = get_commits_in_flight()

        self._commit_queue = CommitQueue(
            write_batch=self._write_batch,
            max_weight=commit_max_messages,
            max_in_flight=commits_in_flight,
        )

# ################################################################################################################################

    def publish(self, pending:'PendingPublication') -> 'None':
        """ Writes one message together with its delivery rows.
        """
        self._commit_queue.write(pending, weight=_publication_weight, is_urgent=True)

        if pending.exception:
            raise pending.exception

# ################################################################################################################################

    def ack(self, pending:'PendingAck') -> 'None':
        """ Removes a subscriber's delivery rows of the given messages and drops the payloads
        of the messages that no subscriber needs anymore.
        """
        weight = len(pending.msg_ids)
        self._commit_queue.write(pending, weight=weight, is_urgent=False)

# ################################################################################################################################

    def _write_batch(self, batch:'anylist') -> 'None':
        """ Writes all the items of one batch, in a thread of the pool under gevent with SQLite.
        """
        engine = get_pubsub_engine()
        call_database(engine, self._write_items, engine, batch)

# ################################################################################################################################

    def _write_items(self, engine:'Engine', batch:'anylist') -> 'None':
        """ Writes the items of a batch in one transaction, which PostgreSQL may roll back as a whole on a conflict
        with concurrent transactions, in which case nothing of it was committed and it runs again.
        """
        attempt = 0

        while True:
            try:
                self._write_transaction(engine, batch)
                break

            except DBAPIError as e:

                attempt += 1

                if attempt > _max_conflict_retries or not is_conflict(e):
                    raise

                logger.info('Pub/sub commit rolled back on a conflict, running it again -> attempt:%d, %s', attempt, e.orig)

                for item in batch:
                    _reset_item(item)

# ################################################################################################################################

    def _write_transaction(self, engine:'Engine', batch:'anylist') -> 'None':
        """ Writes the publications of a batch first and its acknowledgements next, in one transaction.
        """
        publications:'pending_publication_list' = []
        acks:'pending_ack_list' = []

        for item in batch:
            if isinstance(item, PendingPublication):
                publications.append(item)
            else:
                acks.append(item)

        with engine.begin() as connection:

            if publications:
                self._insert_publications(connection, publications)

            if acks:
                self._delete_acks(connection, acks)

# ################################################################################################################################

    def _get_subscribers(self, connection:'Connection', publications:'pending_publication_list') -> 'anydict':
        """ Returns the subscriber keys of each topic the publications go to, read within the caller's transaction.
        """
        topic_names:'anylist' = []

        for pending in publications:
            topic_name = pending.message_values['topic_name']

            if topic_name not in topic_names:
                topic_names.append(topic_name)

        out:'anydict' = {}

        for row in connection.execute(_subscribers_query, {'write_topic_names': topic_names}):

            if row.topic_name not in out:
                out[row.topic_name] = []

            out[row.topic_name].append(row.sub_key)

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

        for chunk in _get_chunks(msg_ids):
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
                continue

            is_same_topic = row.topic_name == message_values['topic_name']
            is_same_payload = row.payload_crc32 == message_values['payload_crc32']

            if is_same_topic and is_same_payload:
                logger.info('Repeated publication of an existing message -> msg_id:%s', msg_id)
            else:
                message = f'Message ID `{msg_id}` belongs to a different message that exists already'
                pending.exception = PubSubDuplicateMsgID(message)

# ################################################################################################################################

    def _insert_deliveries(self, connection:'Connection', delivery_rows:'anylist') -> 'None':
        """ Inserts delivery rows with multi-row inserts or, when there are many of them on PostgreSQL, with COPY.
        """
        dialect_name = connection.dialect.name

        if dialect_name == Type_PostgreSQL and len(delivery_rows) >= _copy_min_delivery_rows:
            copy_rows(connection, delivery_table, delivery_rows)
        else:
            _ = connection.execute(_delivery_insert, delivery_rows)

# ################################################################################################################################

    def _insert_publications(self, connection:'Connection', publications:'pending_publication_list') -> 'None':
        """ Inserts the messages of the publications and one delivery row per message and subscriber.
        """

        # The subscribers as of this very commit ..
        subscribers = self._get_subscribers(connection, publications)

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
        message_insert = _message_inserts[connection.dialect.name]

        inserted:'anydict' = {}

        for row in connection.execute(message_insert, message_rows):
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

        if duplicates:
            self._resolve_duplicates(connection, duplicates)

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
            found = _get_message_ids(connection, lookup_msg_ids)
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

    def _delete_acks(self, connection:'Connection', acks:'pending_ack_list') -> 'None':
        """ Removes the delivery rows the acknowledgements are about and drops the payloads of the messages
        that no subscriber needs anymore. A row that two acknowledgements of one commit are about counts
        towards the first of them, and a message that became fully delivered counts towards the last acknowledgement
        that removed one of its rows, or, with no such acknowledgement, the first one that was about it.
        """
        message_ids_by_ack = self._resolve_ack_message_ids(connection, acks)

        all_message_ids:'anylist' = []
        sub_keys:'strlist' = []

        for pending, message_ids in zip(acks, message_ids_by_ack):
            all_message_ids.extend(message_ids)

            if pending.sub_key not in sub_keys:
                sub_keys.append(pending.sub_key)

        if not all_message_ids:
            return

        # Read the delivery rows of the acknowledged messages that belong to the acknowledging subscribers ..
        delivery_ids_by_pair:'anydict' = {}

        for chunk in _get_chunks(all_message_ids):

            parameters = {
                'ack_message_ids': chunk,
                'ack_sub_keys': sub_keys,
            }

            for row in connection.execute(_ack_deliveries_query, parameters):
                pair = (row.sub_key, row.message_id)
                delivery_ids_by_pair[pair] = row.id

        # .. remove them, in the order of their keys, so that concurrent commits lock them in the same order,
        # learning which of them this commit removed ..
        delivery_ids = sorted(delivery_ids_by_pair.values())
        removed_ids:'set[int]' = set()

        for chunk in _get_chunks(delivery_ids):
            for row in connection.execute(_delivery_delete, {'ack_delivery_ids': chunk}):
                removed_ids.add(row.id)

        # .. assign each removed row to the acknowledgement that removed it ..
        ack_by_message_id:'anydict' = {}

        for pending, message_ids in zip(acks, message_ids_by_ack):
            for message_id in message_ids:

                pair = (pending.sub_key, message_id)
                delivery_id = delivery_ids_by_pair.pop(pair, None)

                if delivery_id in removed_ids:
                    pending.removed_count += 1
                    ack_by_message_id[message_id] = pending

                elif message_id not in ack_by_message_id:
                    ack_by_message_id[message_id] = pending

        # .. and drop the payloads of the messages that no subscriber needs anymore.
        for message_id in drop_payloads(connection, all_message_ids):
            pending = ack_by_message_id[message_id]
            pending.fully_delivered_count += 1

# ################################################################################################################################
# ################################################################################################################################
