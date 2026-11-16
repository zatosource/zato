# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, bindparam, select

# Zato
from zato.common.pubsub.sql.payloads import drop_payloads, get_chunks
from zato.common.pubsub.sql.schema import delivery_table, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.pubsub.sql.writes import PendingAck, PendingPublication
    from zato.common.typing_ import anydict, intlist, strlist

    Connection = Connection
    PendingAck = PendingAck
    PendingPublication = PendingPublication

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

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
_fenced_rows_query = _fenced_rows_query.select_from(delivery_table.join(message_table,
    message_table.c.id == delivery_table.c.message_id))
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

class PubSubAckConflict(Exception):
    """ Raised to the caller of a fenced acknowledgement whose messages another delivery has handed out again
    or concluded, in which case nothing of its transaction is committed.
    """

# ################################################################################################################################
# ################################################################################################################################

def _has_new_message(publications:'list[PendingPublication]') -> 'bool':
    """ Whether the transaction inserted at least one message, as opposed to only repeating existing ones.
    """
    for pending in publications:
        if not pending.is_repeat:
            if not pending.exception:
                return True

    return False

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

def delete_fenced(connection:'Connection', ack:'PendingAck', publications:'list[PendingPublication]') -> 'None':
    """ Removes the delivery rows of a fenced acknowledgement in the caller's transaction, which has inserted
    the publications before. A row with the expected attempt is removed, a row with another attempt was handed out
    again and fails the transaction, and an absent row was concluded already, which fails the transaction
    only if it inserted a new message, so that an acknowledgement repeated with the same publications
    commits nothing and succeeds.
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

        # .. and any other message is removed from the queue, once even if the acknowledgement names it twice.
        if row.id not in delivery_ids:
            delivery_ids.append(row.id)
            message_ids.append(row.message_id)

    if absent:
        if _has_new_message(publications):
            message = f'Message `{absent[0]}` was concluded by another delivery'
            raise PubSubAckConflict(message)

        logger.info('Fenced acknowledgement of concluded messages -> sub_key:%s, msg_ids:%s', ack.sub_key, absent)

    # The rows are removed in the order of their keys, so that concurrent transactions lock them in the same order ..
    delivery_ids.sort()

    for chunk in get_chunks(delivery_ids):
        for _ in connection.execute(_fenced_delete, {'fenced_delivery_ids': chunk}):
            ack.removed_count += 1

    # .. and the payloads of the messages that no subscriber needs anymore are dropped.
    dropped = drop_payloads(connection, message_ids)
    ack.fully_delivered_count = len(dropped)

# ################################################################################################################################
# ################################################################################################################################
