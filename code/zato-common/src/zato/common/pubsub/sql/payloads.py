# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode, b64encode

# SQLAlchemy
from sqlalchemy import and_, bindparam, exists, select, true

# Zato
from zato.common.api import PubSub
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.sql.config import get_batch_size
from zato.common.pubsub.sql.schema import delivery_table, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import anydict, anylist, intlist, intset, strlist

    Connection = Connection

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
    message_table.c.msg_id.in_(bindparam('write_msg_ids', expanding=True))))

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
_drop_payloads_statement = _drop_payloads_statement.values(payload=None, payload_encrypted=False, payload_base64=False)
_drop_payloads_statement_plain = PlainStatement(_drop_payloads_statement.returning(message_table.c.id))

# Two transactions that remove the last two delivery rows of a message would each see the row
# of the other one and both keep the payload, so the message rows are locked first, and the update that follows
# sees every removal committed by the time the lock is granted.
_lock_messages_query = select(message_table.c.id)
_lock_messages_query = _lock_messages_query.where(
    message_table.c.id.in_(bindparam('drop_message_ids', expanding=True)))
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
    message_table.c.id.in_(bindparam('drop_message_ids', expanding=True))))

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
# ################################################################################################################################
