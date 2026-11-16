# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import and_, bindparam, exists, select, true

# Zato
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.sql.config import get_batch_size
from zato.common.pubsub.sql.schema import delivery_table, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import anylist, intlist

    Connection = Connection

# ################################################################################################################################
# ################################################################################################################################

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
_drop_payloads_statement_plain = PlainStatement(_drop_payloads_statement.returning(message_table.c.id))

# Two transactions of PostgreSQL that remove the last two delivery rows of a message would each see the row
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

def drop_payloads(connection:'Connection', message_ids:'intlist') -> 'intlist':
    """ Sets the payload to NULL for each of the given messages that no subscriber needs anymore, in the caller's
    transaction, which has removed delivery rows of these messages before. Returns the messages it dropped
    the payloads of. The message rows that are locked are locked in the order of their keys, which every caller
    follows after its delivery rows, so concurrent transactions cannot deadlock on them.
    """
    message_ids = sorted(message_ids)
    is_postgresql = connection.dialect.name == Type_PostgreSQL

    out:'intlist' = []

    for chunk in get_chunks(message_ids):

        # On PostgreSQL, only the messages without a delivery row that remains are locked and looked at ..
        if is_postgresql:

            needed:'set[int]' = set()

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

        # .. while SQLite, with its single writer, looks at all of them.
        else:
            parameters = {'drop_message_ids': chunk}

        for row in _drop_payloads_statement_plain.execute(connection, parameters):
            out.append(row.id)

    return out

# ################################################################################################################################
# ################################################################################################################################
