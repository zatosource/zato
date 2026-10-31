# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import and_, bindparam, exists, select
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.db_env.commit_queue import CommitQueue
from zato.common.db_env.engine import call_database
from zato.common.pubsub.sql.config import get_batch_size, get_commit_max_messages, get_pubsub_engine
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

# Type aliases
pending_publication_list = list['PendingPublication']
pending_ack_list         = list['PendingAck']

# A publication refers to one message.
_publication_weight = 1

# ################################################################################################################################
# ################################################################################################################################

# The statements of a group commit are built once here, the bind parameters take their values at execution time.
_subscribers_query = select(topic_sub_table.c.topic_name, topic_sub_table.c.sub_key)
_subscribers_query = _subscribers_query.where(
    topic_sub_table.c.topic_name.in_(bindparam('write_topic_names', expanding=True)))

_message_insert = message_table.insert()
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

_delivery_delete = delivery_table.delete()
_delivery_delete = _delivery_delete.where(delivery_table.c.id.in_(bindparam('ack_delivery_ids', expanding=True)))

# A message is still in flight while any delivery row references it -
# the update drops the payloads of the given messages that have none left.
_still_needed = exists()
_still_needed = _still_needed.where(delivery_table.c.message_id == message_table.c.id)

drop_payloads_statement = message_table.update()
drop_payloads_statement = drop_payloads_statement.where(and_(
    message_table.c.id.in_(bindparam('drop_message_ids', expanding=True)),
    message_table.c.payload.isnot(None),
    ~_still_needed,
))
drop_payloads_statement = drop_payloads_statement.values(payload=None, payload_encrypted=False)

# The same update, telling which messages it dropped the payloads of
_drop_payloads_returning = drop_payloads_statement.returning(message_table.c.id)

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
    in the thread pool of the gevent hub. Each caller waits until the transaction with its item is committed.
    Publications go into the next transaction ahead of acknowledgements, and the size of a transaction
    is limited by the number of messages it refers to, so that a publisher waits for at most one transaction
    of a bounded size, however many acknowledgements of deep queues are waiting.
    """

    def __init__(self) -> 'None':
        commit_max_messages = get_commit_max_messages()
        self._commit_queue = CommitQueue(write_batch=self._write_batch, max_weight=commit_max_messages)

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
        """ Writes all the items of one batch, in a thread of the pool under gevent.
        """
        engine = get_pubsub_engine()
        call_database(engine, self._write_items, engine, batch)

# ################################################################################################################################

    def _write_items(self, engine:'Engine', batch:'anylist') -> 'None':
        """ Writes the items of a batch in one transaction. A message whose identifier exists already makes
        the transaction fail, in which case each item is written in a transaction of its own, so that
        the exception reaches the caller of that message alone.
        """
        try:
            self._write_transaction(engine, batch)

        except IntegrityError:
            for item in batch:
                try:
                    self._write_transaction(engine, [item])
                except IntegrityError as e:
                    item.exception = e

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

    def _insert_publications(self, connection:'Connection', publications:'pending_publication_list') -> 'None':
        """ Inserts the messages of the publications and one delivery row per message and subscriber.
        """

        # The subscribers as of this very commit ..
        subscribers = self._get_subscribers(connection, publications)

        message_rows:'anylist' = []
        msg_ids:'strlist' = []

        for pending in publications:

            message_values = pending.message_values
            topic_name = message_values['topic_name']

            # .. a topic without subscribers has its messages stored without their payloads ..
            if sub_keys := subscribers.get(topic_name):
                pending.subscriber_keys = sub_keys
            else:
                pending.subscriber_keys = []
                message_values['payload'] = None
                message_values['payload_encrypted'] = False

            message_rows.append(message_values)
            msg_ids.append(message_values['msg_id'])

        # .. all the messages go in one statement ..
        _ = connection.execute(_message_insert, message_rows)

        # .. their primary keys are what the delivery rows point to ..
        message_ids = _get_message_ids(connection, msg_ids)

        delivery_rows:'anylist' = []

        for pending in publications:

            message_values = pending.message_values
            message_id = message_ids[message_values['msg_id']]

            for sub_key in pending.subscriber_keys:
                delivery_rows.append({
                    'message_id': message_id,
                    'sub_key': sub_key,
                    'topic_name': message_values['topic_name'],
                    'priority': message_values['priority'],
                    'expiration_ms': message_values['expiration_ms'],
                })

        # .. and so do all the delivery rows.
        if delivery_rows:
            _ = connection.execute(_delivery_insert, delivery_rows)

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

        # .. assign each of them to the acknowledgement that removes it ..
        delivery_ids:'intlist' = []
        ack_by_message_id:'anydict' = {}

        for pending, message_ids in zip(acks, message_ids_by_ack):
            for message_id in message_ids:

                pair = (pending.sub_key, message_id)

                if delivery_id := delivery_ids_by_pair.pop(pair, None):
                    delivery_ids.append(delivery_id)
                    pending.removed_count += 1
                    ack_by_message_id[message_id] = pending

                elif message_id not in ack_by_message_id:
                    ack_by_message_id[message_id] = pending

        # .. remove the rows ..
        for chunk in _get_chunks(delivery_ids):
            _ = connection.execute(_delivery_delete, {'ack_delivery_ids': chunk})

        # .. and drop the payloads of the messages that no subscriber needs anymore.
        for chunk in _get_chunks(all_message_ids):
            for row in connection.execute(_drop_payloads_returning, {'drop_message_ids': chunk}):
                pending = ack_by_message_id[row.id]
                pending.fully_delivered_count += 1

# ################################################################################################################################
# ################################################################################################################################
