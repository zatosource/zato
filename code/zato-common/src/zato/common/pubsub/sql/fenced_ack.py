# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import and_, bindparam, select

# Zato
from zato.common.pubsub.sql.payloads import get_chunks
from zato.common.pubsub.sql.schema import delivery_table, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.pubsub.sql.pending import PendingAck
    from zato.common.typing_ import anydict, intlist, strlist

    Connection = Connection
    PendingAck = PendingAck

# ################################################################################################################################
# ################################################################################################################################

# The delivery rows of one subscriber for the given messages, with the attempt that each of them was handed out with.
# On PostgreSQL, the rows are locked until the commit, so a lease of the same rows and a concurrent acknowledgement
# of them wait for this transaction or this transaction waits for them, and each one sees what the other one committed.
_fenced_rows_query = select(
    delivery_table.c.id,
    delivery_table.c.message_id,
    delivery_table.c.attempt,
    message_table.c.msg_id,
)
_fenced_join = delivery_table.join(message_table, message_table.c.id == delivery_table.c.message_id)

_fenced_rows_query = _fenced_rows_query.select_from(_fenced_join)
_fenced_rows_query = _fenced_rows_query.where(and_(
    delivery_table.c.sub_key == bindparam('fenced_sub_key'),
    message_table.c.msg_id.in_(bindparam('fenced_msg_ids', expanding=True)),
))
_fenced_rows_query = _fenced_rows_query.order_by(delivery_table.c.id)
_fenced_rows_query = _fenced_rows_query.with_for_update(of=delivery_table)

_fenced_delete = delivery_table.delete()
_fenced_delete = _fenced_delete.where(delivery_table.c.id.in_(bindparam('fenced_delivery_ids', expanding=True)))
_fenced_delete = _fenced_delete.returning(delivery_table.c.id)

# ################################################################################################################################
# ################################################################################################################################

class FencedRows(NamedTuple):
    """ The delivery rows that a fenced acknowledgement removes and the messages that they belong to.
    """
    delivery_ids: 'intlist'
    message_ids: 'intlist'

# ################################################################################################################################

class PubSubAckConflict(Exception):
    """ Raised to the caller of a fenced acknowledgement whose messages another delivery has handed out again
    or concluded, in which case nothing of its transaction is committed.
    """

# ################################################################################################################################
# ################################################################################################################################

def _read_rows(connection:'Connection', ack:'PendingAck') -> 'anydict':
    """ Returns the delivery rows of the acknowledgement that exist, by the message ID of each.
    """
    out:'anydict' = {}

    for chunk in get_chunks(ack.msg_ids):

        parameters = {
            'fenced_sub_key': ack.sub_key,
            'fenced_msg_ids': chunk,
        }

        for row in connection.execute(_fenced_rows_query, parameters):
            out[row.msg_id] = row

    return out

# ################################################################################################################################

def check_fenced(connection:'Connection', ack:'PendingAck', has_new_message:'bool') -> 'FencedRows':
    """ Reads the delivery rows of a fenced acknowledgement in the caller's transaction, before anything of the acknowledgement
    is written, and returns those that it is to remove. A row with the expected attempt is to be removed, a row with another
    attempt was handed out again and raises PubSubAckConflict, and an absent row was concluded already, which raises it
    only if the publications of the acknowledgement insert a new message, so that an acknowledgement repeated
    with the same publications commits nothing and succeeds.
    """
    rows = _read_rows(connection, ack)

    delivery_ids:'intlist' = []
    message_ids:'intlist' = []
    absent:'strlist' = []

    for index, msg_id in enumerate(ack.msg_ids):

        # A message that is not in the queue anymore was concluded by an earlier delivery ..
        if msg_id not in rows:
            absent.append(msg_id)
            continue

        row = rows[msg_id]

        # .. a message handed out again since belongs to the delivery that holds its current attempt ..
        if ack.expected_attempts is not None:
            expected_attempt = ack.expected_attempts[index]

            if row.attempt != expected_attempt:
                message = f'Message `{msg_id}` was handed out again with delivery attempt {row.attempt}, ' + \
                    f'the acknowledgement is for attempt {expected_attempt}'
                raise PubSubAckConflict(message)

        # .. and any other message is to be removed from the queue, once even if the acknowledgement names it twice.
        if row.id not in delivery_ids:
            delivery_ids.append(row.id)
            message_ids.append(row.message_id)

    if absent:
        if has_new_message:
            first_absent = absent[0]
            message = f'Message `{first_absent}` was concluded by another delivery'
            raise PubSubAckConflict(message)

        # The caller logs these after the commit, outside the thread that writes it
        ack.concluded_msg_ids = absent

    out = FencedRows(delivery_ids, message_ids)
    return out

# ################################################################################################################################

def delete_fenced(connection:'Connection', ack:'PendingAck', rows:'FencedRows') -> 'None':
    """ Removes the delivery rows that check_fenced returned, in the caller's transaction, which drops the payloads
    of their messages once it holds every delivery row that it locks.
    """

    # The rows are removed in the order of their keys, so that concurrent transactions lock them in the same order.
    delivery_ids = sorted(rows.delivery_ids)

    for chunk in get_chunks(delivery_ids):
        parameters = {'fenced_delivery_ids': chunk}

        for _ in connection.execute(_fenced_delete, parameters):
            ack.removed_count += 1

# ################################################################################################################################
# ################################################################################################################################
