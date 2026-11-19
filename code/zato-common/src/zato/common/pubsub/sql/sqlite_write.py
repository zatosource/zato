# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The transaction of the items of a pub/sub batch on SQLite, which writes all of them in Rust, with the GIL released,
# through the handle of the driver's connection and in the transaction that the connection holds open.

# stdlib
from logging import getLogger
from sqlite3 import Error as SQLiteError, sqlite_version
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import and_, bindparam, exists, false, literal_column, null, select
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.db_env.write_path import check_write_path
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.pubsub.sql.pull import message_columns
from zato.common.pubsub.sql.schema import delivery_table, message_table, topic_sub_table
from zato.common.typing_ import cast_

# Zato - Rust
from zato_common_core.zato_common_core import SQLitePubSubWriter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from sqlalchemy.sql.expression import ClauseElement
    from zato.common.pubsub.sql.pending import pending_ack_list, pending_atomic_list, pending_attempts_list, \
        pending_lease_list, pending_publication_list
    from zato.common.typing_ import any_, anylist, strlist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anylist = anylist
    ClauseElement = ClauseElement
    Connection = Connection
    pending_ack_list = pending_ack_list
    pending_atomic_list = pending_atomic_list
    pending_attempts_list = pending_attempts_list
    pending_lease_list = pending_lease_list
    pending_publication_list = pending_publication_list
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The statement that opens the transaction the driver opens itself before a statement that changes rows
_begin_statement = 'BEGIN'

# The dialect that the statements are compiled for
_dialect = sqlite.dialect()

# The prefix of the parameters of the message insert, whose names may not be those of the columns
_value_prefix = 'value_'

# The columns of a message that the values of a publication provide, in the order of the table
_message_column_names:'strlist' = []

for _column in message_table.c:
    if _column.name != message_table.c.id.name:
        _message_column_names.append(_column.name)

# The columns of a leased message, in the order in which the messages of a pull are built from them
_lease_column_names:'strlist' = []
_lease_fields:'anylist' = []

for _column in message_columns:
    _lease_column_names.append(_column.name)
    _lease_fields.append((_column.name, object))

# The row of a leased message, whose values are read by position and by the name of their column, as those of a query are
LeasedMessageRow = NamedTuple('LeasedMessageRow', _lease_fields)

# ################################################################################################################################
# ################################################################################################################################

def _compile(statement:'ClauseElement', parameter_names:'strlist') -> 'str':
    """ Returns the text of a statement for SQLite, whose positional parameters are those that the writer binds.
    """
    compiled = statement.compile(dialect=_dialect)
    positions = list(cast_('strlist', compiled.positiontup))

    if positions != parameter_names:
        raise Exception(f'Parameters `{positions}` differ from `{parameter_names}` -> `{compiled.string}`')

    out = compiled.string
    return out

# ################################################################################################################################
# ################################################################################################################################

# The subscribers of one topic.
_select_subscribers = select(topic_sub_table.c.sub_key)
_select_subscribers = _select_subscribers.where(topic_sub_table.c.topic_name == bindparam('topic_name'))

# The insert of one message, which returns its id unless its identifier exists already.
_message_values = {}
_message_parameter_names:'strlist' = []

for _name in _message_column_names:
    _message_values[_name] = bindparam(_value_prefix + _name)
    _message_parameter_names.append(_value_prefix + _name)

_insert_message = sqlite_insert(message_table).values(_message_values)
_insert_message = _insert_message.on_conflict_do_nothing(index_elements=[message_table.c.msg_id])
_insert_message = _insert_message.returning(message_table.c.id)

# What a message that exists already was published with.
_select_existing_message = select(message_table.c.topic_name, message_table.c.payload_crc32)
_select_existing_message = _select_existing_message.where(message_table.c.msg_id == bindparam('msg_id'))

# The insert of one delivery row.
_insert_delivery = delivery_table.insert().values(
    message_id=bindparam('delivery_message_id'),
    sub_key=bindparam('delivery_sub_key'),
    topic_name=bindparam('delivery_topic_name'),
    priority=bindparam('delivery_priority'),
    expiration_ms=bindparam('delivery_expiration_ms'),
)

# The id of the message of one identifier.
_select_message_id = select(message_table.c.id).where(message_table.c.msg_id == bindparam('msg_id'))

# The delivery rows of one message that belong to one subscriber. The subscriber column is concatenated
# with an empty string, which keeps SQLite from looking the rows up through an index of subscribers,
# whose queues may be deep, rather than through the index of messages.
_select_ack_delivery = select(delivery_table.c.id).where(and_(
    delivery_table.c.message_id == bindparam('message_id'),
    delivery_table.c.sub_key.concat(literal_column("''")) == bindparam('sub_key'),
))

# The delete of one delivery row, which returns its id if the row existed.
_delete_delivery = delivery_table.delete().where(delivery_table.c.id == bindparam('delivery_id'))
_delete_delivery = _delete_delivery.returning(delivery_table.c.id)

# The record of the next push attempt of one delivery row.
_record_attempt = delivery_table.update().where(delivery_table.c.id == bindparam('delivery_id'))
_record_attempt = _record_attempt.values(attempt=delivery_table.c.attempt + literal_column('1'))
_record_attempt = _record_attempt.returning(delivery_table.c.attempt)

# The deliverable rows of one subscriber that no pull holds a lease on, or whose lease has run out, in the order of the queue.
_lease_join = delivery_table.join(message_table, message_table.c.id == delivery_table.c.message_id)

_select_lease_candidates = select(delivery_table.c.id, message_table.c.data_size).select_from(_lease_join)
_select_lease_candidates = _select_lease_candidates.where(and_(
    delivery_table.c.sub_key == bindparam('sub_key'),
    delivery_table.c.expiration_ms > bindparam('now_ms'),
    delivery_table.c.leased_until_ms < bindparam('now_ms'),
))
_select_lease_candidates = _select_lease_candidates.order_by(
    delivery_table.c.priority.desc(), delivery_table.c.message_id.asc())
_select_lease_candidates = _select_lease_candidates.limit(bindparam('max_messages')).offset(literal_column('0'))

# The lease of one delivery row, which a row that a concurrent pull leased in the meantime no longer matches.
_lease_delivery = delivery_table.update().where(and_(
    delivery_table.c.id == bindparam('delivery_id'),
    delivery_table.c.leased_until_ms < bindparam('now_ms'),
))
_lease_delivery = _lease_delivery.values(
    leased_until_ms=bindparam('lease_leased_until_ms'),
    attempt=delivery_table.c.attempt + literal_column('1'),
)
_lease_delivery = _lease_delivery.returning(delivery_table.c.message_id, delivery_table.c.attempt)

# The columns of one leased message.
_select_leased_message = select(*message_columns).where(message_table.c.id == bindparam('message_id'))

# The delivery rows of one subscriber for the message of one identifier, with the attempt that each was handed out with.
_select_fenced_delivery = select(delivery_table.c.id, delivery_table.c.message_id, delivery_table.c.attempt)
_select_fenced_delivery = _select_fenced_delivery.select_from(_lease_join)
_select_fenced_delivery = _select_fenced_delivery.where(and_(
    delivery_table.c.sub_key == bindparam('sub_key'),
    message_table.c.msg_id == bindparam('msg_id'),
))
_select_fenced_delivery = _select_fenced_delivery.order_by(delivery_table.c.id)

# The drop of the payload of one message that no delivery row references anymore.
_still_needed = exists().where(delivery_table.c.message_id == message_table.c.id)

_drop_payload = message_table.update().where(and_(
    message_table.c.id == bindparam('message_id'),
    message_table.c.payload.isnot(None),
    ~_still_needed,
))
_drop_payload = _drop_payload.values(payload=null(), payload_encrypted=false())
_drop_payload = _drop_payload.returning(message_table.c.id)

# ################################################################################################################################
# ################################################################################################################################

# The statements of the transaction, each with the parameters in the order in which the writer binds them,
# and each checked against the mechanism of the write before a batch is written.
_select_subscribers = _compile(_select_subscribers, ['topic_name'])
_insert_message = _compile(_insert_message, _message_parameter_names)
_select_existing_message = _compile(_select_existing_message, ['msg_id'])
_insert_delivery = _compile(_insert_delivery, [
    'delivery_message_id', 'delivery_sub_key', 'delivery_topic_name', 'delivery_priority', 'delivery_expiration_ms'])
_select_message_id = _compile(_select_message_id, ['msg_id'])
_select_ack_delivery = _compile(_select_ack_delivery, ['message_id', 'sub_key'])
_delete_delivery = _compile(_delete_delivery, ['delivery_id'])
_record_attempt = _compile(_record_attempt, ['delivery_id'])
_select_lease_candidates = _compile(_select_lease_candidates, ['sub_key', 'now_ms', 'now_ms', 'max_messages'])
_lease_delivery = _compile(_lease_delivery, ['lease_leased_until_ms', 'delivery_id', 'now_ms'])
_select_leased_message = _compile(_select_leased_message, ['message_id'])
_select_fenced_delivery = _compile(_select_fenced_delivery, ['sub_key', 'msg_id'])
_drop_payload = _compile(_drop_payload, ['message_id'])

_write_statements = [
    _begin_statement, _select_subscribers, _insert_message, _select_existing_message, _insert_delivery, _select_message_id,
    _select_ack_delivery, _delete_delivery, _record_attempt, _select_lease_candidates, _lease_delivery,
    _select_leased_message, _select_fenced_delivery, _drop_payload,
]

_writer = SQLitePubSubWriter({
    'sqlite_version': sqlite_version,
    'statements': {
        'begin': _begin_statement,
        'select_subscribers': _select_subscribers,
        'insert_message': _insert_message,
        'select_existing_message': _select_existing_message,
        'insert_delivery': _insert_delivery,
        'select_message_id': _select_message_id,
        'select_ack_delivery': _select_ack_delivery,
        'delete_delivery': _delete_delivery,
        'record_attempt': _record_attempt,
        'select_lease_candidates': _select_lease_candidates,
        'lease_delivery': _lease_delivery,
        'select_leased_message': _select_leased_message,
        'select_fenced_delivery': _select_fenced_delivery,
        'drop_payload': _drop_payload,
    },
    'message_columns': _message_column_names,
    'lease_columns': _lease_column_names,
    'payload_column': message_table.c.payload.name,
    'payload_encrypted_column': message_table.c.payload_encrypted.name,
    'id_column': message_table.c.id.name,
    'priority_column': message_table.c.priority.name,
    'duplicate_error': PubSubDuplicateMsgID,
    'conflict_error': PubSubAckConflict,
    'lease_row_class': LeasedMessageRow,
})

# ################################################################################################################################
# ################################################################################################################################

def write_items_sqlite(
    connection:'Connection',
    publications:'pending_publication_list',
    acks:'pending_ack_list',
    atomics:'pending_atomic_list',
    attempts_list:'pending_attempts_list',
    leases:'pending_lease_list',
    ) -> 'None':
    """ Writes the items of a batch in the open transaction of the connection with the GIL released, stores on each item
    what became of it, and builds the messages of each pull from the rows that it leased.
    """
    # The items join the transaction of the caller, which must therefore be open already ..
    if not connection.in_transaction():
        raise Exception('The connection has no open transaction')

    # .. each statement passes the guard of the write path before the writer runs it ..
    for statement in _write_statements:
        check_write_path(None, None, statement, None, None, True)

    items = {
        'publications': publications,
        'acks': acks,
        'atomics': atomics,
        'attempts': attempts_list,
        'leases': leases,
    }

    dbapi_connection = cast_('any_', connection.connection.dbapi_connection)

    # .. the statements run in Rust, which raises the exceptions of the driver ..
    try:
        repeats = _writer.write_items(dbapi_connection, items)
    except SQLiteError as error:
        raise DBAPIError.instance(None, None, error, SQLiteError) from error

    # .. a repeated publication receives the result of the original one ..
    for msg_id, is_removed in repeats:
        if is_removed:
            logger.info('Repeated publication of a removed message -> msg_id:%s', msg_id)
        else:
            logger.info('Repeated publication of an existing message -> msg_id:%s', msg_id)

    # .. and each pull builds its messages, whose receptions commit with its lease.
    for lease in leases:
        lease.on_leased(lease)

# ################################################################################################################################
# ################################################################################################################################
