# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode, b64encode

# SQLAlchemy
from sqlalchemy import and_, exists, false, insert, select, true
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.payload import delete_unreferenced_payloads, store_payload
from zato.common.db_env.any_of import any_of
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.sql.config import get_batch_size
from zato.common.pubsub.sql.schema import delivery_table, message_table, released_payload_table, trace_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.pubsub.sql.pending import PendingUpdate
    from zato.common.typing_ import anydict, anylist, intlist, intset, strlist

    Connection = Connection
    PendingUpdate = PendingUpdate

# ################################################################################################################################
# ################################################################################################################################

# How many leading characters of a payload its preview holds
_data_preview_len = PubSub.Message.Data_Preview_Len

# The character that a text column of PostgreSQL cannot hold ..
_nul_character = '\x00'

# .. and what stands for it in the preview of a payload.
_nul_replacement = '\ufffd'

# ################################################################################################################################
# ################################################################################################################################

def get_data_preview(data:'str') -> 'str':
    """ Returns the preview of a payload, its leading characters with each NUL character replaced,
    because the preview is stored as text, which holds no NUL character.
    """
    out = data[:_data_preview_len]
    out = out.replace(_nul_character, _nul_replacement)

    return out

# ################################################################################################################################

def needs_base64(data:'str') -> 'bool':
    """ Tells whether a payload is stored as Base64, because it holds a NUL character, which text cannot hold.
    """
    out = _nul_character in data
    return out

# ################################################################################################################################

def to_base64(data:'str') -> 'str':
    """ Returns the Base64 of the UTF-8 bytes of a payload, in which form it is stored.
    """
    data_bytes = data.encode('utf8')
    out = b64encode(data_bytes).decode('ascii')

    return out

# ################################################################################################################################

def from_base64(payload:'str') -> 'str':
    """ Returns the payload that was stored as the Base64 of its UTF-8 bytes.
    """
    data_bytes = b64decode(payload)
    out = data_bytes.decode('utf8')

    return out

# ################################################################################################################################
# ################################################################################################################################

# The primary keys of messages by their public identifiers
_message_ids_query = select(message_table.c.id, message_table.c.msg_id)
_message_ids_query_plain = PlainStatement(_message_ids_query.where(
    any_of(message_table.c.msg_id, 'write_msg_ids')))

# A message is still in flight while any delivery row references it -
# the update drops the payloads of the given messages that have none left.
_still_needed = exists()
_still_needed = _still_needed.where(delivery_table.c.message_id == message_table.c.id)

_drop_payloads_statement = message_table.update()
_drop_payloads_statement = _drop_payloads_statement.where(and_(
    any_of(message_table.c.id, 'drop_message_ids'),
    message_table.c.payload_dropped.is_(false()),
    ~_still_needed,
))
_drop_payloads_statement = _drop_payloads_statement.values(payload_dropped=True, payload_encrypted=False, payload_base64=False)
_drop_payloads_statement = _drop_payloads_statement.returning(
    message_table.c.id, message_table.c.topic_name, message_table.c.pub_time_ms, message_table.c.payload_id)
_dropped_messages = _drop_payloads_statement.cte('dropped_messages')

# The same statement adds each message that dropped its payload to the traces ..
_traced_query = select(_dropped_messages.c.id, _dropped_messages.c.topic_name, _dropped_messages.c.pub_time_ms)

_add_traces = postgresql_insert(trace_table)
_add_traces = _add_traces.from_select([trace_table.c.message_id, trace_table.c.topic_name, trace_table.c.pub_time_ms],
    _traced_query)
_add_traces = _add_traces.on_conflict_do_update(index_elements=[trace_table.c.message_id], set_={
    'topic_name': _add_traces.excluded.topic_name,
    'pub_time_ms': _add_traces.excluded.pub_time_ms,
})

# .. and releases the payload for the cleanup sweep.
_released_query = select(_dropped_messages.c.payload_id)
_released_query = _released_query.where(_dropped_messages.c.payload_id.is_not(None))

_release_payloads = insert(released_payload_table)
_release_payloads = _release_payloads.from_select([released_payload_table.c.payload_id], _released_query)

_drop_payloads_query = select(_dropped_messages.c.id)
_drop_payloads_query = _drop_payloads_query.add_cte(_add_traces.cte('traced_messages'))
_drop_payloads_query = _drop_payloads_query.add_cte(_release_payloads.cte('released_payloads'))
_drop_payloads_statement_plain = PlainStatement(_drop_payloads_query)

# Two transactions that remove the last two delivery rows of a message would each see the row
# of the other one and both keep the payload, so the message rows are locked first, and the update that follows
# sees every removal committed by the time the lock is granted.
_lock_messages_query = select(message_table.c.id)
_lock_messages_query = _lock_messages_query.where(
    any_of(message_table.c.id, 'drop_message_ids'))
_lock_messages_query = _lock_messages_query.order_by(message_table.c.id)
_lock_messages_query_plain = PlainStatement(_lock_messages_query.with_for_update(key_share=True))

# A message with a delivery row that no transaction is removing still has a subscriber, and the row is held for key share
# until the commit, so that the transaction which removes it later waits for this one and then sees its removals.
# Only the other messages are locked as above, which keeps the subscribers of a fanned-out message
# from acknowledging it one transaction after another.
_live_delivery = select(delivery_table.c.id)
_live_delivery = _live_delivery.where(delivery_table.c.message_id == message_table.c.id)
_live_delivery = _live_delivery.limit(1)
_live_delivery = _live_delivery.with_for_update(read=True, key_share=True, skip_locked=True)
_live_delivery = _live_delivery.lateral()

_needed_messages_query = select(message_table.c.id)
_needed_messages_query = _needed_messages_query.select_from(message_table.join(_live_delivery, true()))
_needed_messages_query_plain = PlainStatement(_needed_messages_query.where(
    any_of(message_table.c.id, 'drop_message_ids')))

# ################################################################################################################################
# ################################################################################################################################

def get_chunks(items:'anylist') -> 'anylist':
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

def get_message_ids(connection:'Connection', msg_ids:'strlist') -> 'anydict':
    """ Maps public message identifiers to their primary keys, read within the caller's transaction.
    """
    out:'anydict' = {}

    for chunk in get_chunks(msg_ids):
        for row in _message_ids_query_plain.execute(connection, {'write_msg_ids': chunk}):
            out[row.msg_id] = row.id

    return out

# ################################################################################################################################

def drop_payloads(connection:'Connection', message_ids:'intlist') -> 'intlist':
    """ Sets the payload to NULL for each of the given messages that no subscriber needs anymore, in the caller's
    transaction, which has removed delivery rows of these messages before. Returns the messages it dropped
    the payloads of. The message rows that are locked are locked in the order of their keys, which every caller
    follows after its delivery rows, so concurrent transactions cannot deadlock on them.
    """
    message_ids = sorted(message_ids)

    out:'intlist' = []

    for chunk in get_chunks(message_ids):

        # Only the messages without a delivery row that remains are locked ..
        needed:'intset' = set()

        for row in _needed_messages_query_plain.execute(connection, {'drop_message_ids': chunk}):
            needed.add(row.id)

        candidates:'intlist' = []

        for message_id in chunk:
            if message_id not in needed:
                candidates.append(message_id)

        if not candidates:
            continue

        parameters = {'drop_message_ids': candidates}
        _ = _lock_messages_query_plain.execute(connection, parameters).fetchall()

        # .. and only they lose their payloads.
        for row in _drop_payloads_statement_plain.execute(connection, parameters):
            out.append(row.id)

    return out

# ################################################################################################################################

def update_message_payload(connection:'Connection', pending:'PendingUpdate') -> 'bool':
    """ Stores the new payload of one message in the payload table and makes the message reference it, with the values
    derived from it, in the caller's transaction, and deletes the payload it replaced if nothing else references it.
    Returns True if the message existed and was updated.
    """
    condition = and_(
        message_table.c.msg_id == pending.msg_id,
        message_table.c.topic_name == pending.topic_name,
    )

    # The payload that the message has not dropped yet, if any ..
    previous_query = select(message_table.c.id, message_table.c.payload_id, message_table.c.payload_dropped)
    previous_query = previous_query.where(condition)
    previous_query = previous_query.with_for_update()

    previous = connection.execute(previous_query).fetchone()

    if previous is None:
        return False

    # .. the new one is stored unless it is stored already ..
    payload_id = store_payload(connection, pending.payload)

    # .. the message references it ..
    update_statement = message_table.update()
    update_statement = update_statement.where(condition)
    update_statement = update_statement.values(payload_id=payload_id, payload_dropped=False, **pending.values)

    _ = connection.execute(update_statement)

    # .. a message with a payload is no longer a trace ..
    if previous.payload_dropped:
        delete_statement = trace_table.delete()
        delete_statement = delete_statement.where(trace_table.c.message_id == previous.id)

        _ = connection.execute(delete_statement)

    # .. and the previous one is deleted unless something else references it. A dropped one was released
    # when the message dropped it.
    if previous.payload_id is not None and not previous.payload_dropped:
        if previous.payload_id != payload_id:
            delete_unreferenced_payloads(connection, [previous.payload_id])

    return True

# ################################################################################################################################
# ################################################################################################################################
