# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import and_, delete, insert, select, update

# Zato
from zato.common.b2b.common.schema import held_message_table, open_table, OpenKind, sequence_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import any_, strlist
    any_ = any_
    Connection = Connection
    datetime = datetime
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class HeldRow:
    """ A held message of an ordered conversation as its row has it. The identifier is 0 for a row not inserted yet,
    and the time of the report is None until the timeout of the gap it opened is recorded.
    """
    conversation:    str
    sequence_number: int
    message_id:      str
    event_id:        int
    held_at:         'datetime'
    retry_window_ms: int
    reported_at:     'datetime | None' = None
    id:              int = 0

held_row_list = list[HeldRow]

# ################################################################################################################################
# ################################################################################################################################

def _held_of(row:'any_') -> 'HeldRow':
    out = HeldRow()
    out.id = row.id
    out.conversation = row.conversation
    out.sequence_number = row.sequence_number
    out.message_id = row.message_id
    out.event_id = row.event_id
    out.held_at = row.held_at
    out.retry_window_ms = row.retry_window_ms
    out.reported_at = row.reported_at

    return out

# ################################################################################################################################

def _held_condition(conversation:'str', sequence_number:'int') -> 'any_':
    out = and_(
        held_message_table.c.conversation == conversation,
        held_message_table.c.sequence_number == sequence_number,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_next_sequence(connection:'Connection', conversation:'str') -> 'int | None':
    """ Returns the sequence number expected next in an ordered conversation, or None when it has no state yet.
    """
    query = select(sequence_table.c.next_sequence)
    statement = query.where(sequence_table.c.conversation == conversation)

    out = connection.execute(statement).scalar()
    return out

# ################################################################################################################################

def set_next_sequence(connection:'Connection', conversation:'str', sequence_number:'int') -> 'None':
    """ Sets the sequence number expected next in an ordered conversation.
    """
    update_statement = update(sequence_table).where(sequence_table.c.conversation == conversation)
    update_statement = update_statement.values(next_sequence=sequence_number)

    result = connection.execute(update_statement)

    # A conversation that has no state yet receives it.
    if not result.rowcount:
        insert_statement = insert(sequence_table).values(conversation=conversation, next_sequence=sequence_number)
        _ = connection.execute(insert_statement)

# ################################################################################################################################

def is_held(connection:'Connection', conversation:'str', sequence_number:'int') -> 'bool':
    """ Says whether a message is held under a sequence number of a conversation.
    """
    condition = _held_condition(conversation, sequence_number)
    statement = select(held_message_table.c.id).where(condition)

    row = connection.execute(statement).first()

    out = row is not None
    return out

# ################################################################################################################################

def hold(connection:'Connection', row:'HeldRow') -> 'None':
    """ Keeps a message that arrived before the messages preceding it in its conversation.
    """
    statement = insert(held_message_table).values(
        conversation=row.conversation,
        sequence_number=row.sequence_number,
        message_id=row.message_id,
        event_id=row.event_id,
        held_at=row.held_at,
        retry_window_ms=row.retry_window_ms,
    )

    _ = connection.execute(statement)

# ################################################################################################################################

def take_held(connection:'Connection', conversation:'str', sequence_number:'int') -> 'HeldRow | None':
    """ Removes and returns the held message with the given sequence number, or None.
    """
    condition = _held_condition(conversation, sequence_number)
    statement = select(held_message_table).where(condition)

    if row := connection.execute(statement).first():
        out = _held_of(row)
        _ = connection.execute(delete(held_message_table).where(condition))
    else:
        out = None

    return out

# ################################################################################################################################

def held_messages(connection:'Connection', conversation:'str') -> 'held_row_list':
    """ Returns the held messages of a conversation, the lowest sequence number first.
    """
    query = select(held_message_table).where(held_message_table.c.conversation == conversation)
    statement = query.order_by(held_message_table.c.sequence_number)

    out:'held_row_list' = []

    for row in connection.execute(statement):
        held = _held_of(row)
        out.append(held)

    return out

# ################################################################################################################################

def earliest_held(connection:'Connection', conversation:'str') -> 'HeldRow | None':
    """ Returns the held message of a conversation that was held first, which opened the gap of the conversation,
    or None when none is held.
    """
    query = select(held_message_table).where(held_message_table.c.conversation == conversation)
    statement = query.order_by(held_message_table.c.held_at, held_message_table.c.id).limit(1)

    if row := connection.execute(statement).first():
        out = _held_of(row)
    else:
        out = None

    return out

# ################################################################################################################################

def gap_conversations(connection:'Connection', after:'str', limit:'int') -> 'strlist':
    """ Returns, up to the limit and in their order, the conversations that hold messages, starting after the given one.
    """
    query = select(held_message_table.c.conversation).distinct()
    query = query.where(held_message_table.c.conversation > after)
    statement = query.order_by(held_message_table.c.conversation).limit(limit)

    out:'strlist' = []

    for conversation in connection.execute(statement).scalars():
        out.append(conversation)

    return out

# ################################################################################################################################

def set_reported(connection:'Connection', row_id:'int', reported_at:'datetime') -> 'None':
    """ Records when the timeout of the gap that a held message opened was reported.
    """
    statement = update(held_message_table).where(held_message_table.c.id == row_id).values(reported_at=reported_at)
    _ = connection.execute(statement)

# ################################################################################################################################

def discard_held(connection:'Connection', conversation:'str') -> 'int':
    """ Deletes the held messages and the sequence state of a conversation, and returns how many messages were held.
    """
    held_statement = delete(held_message_table).where(held_message_table.c.conversation == conversation)
    result = connection.execute(held_statement)

    sequence_statement = delete(sequence_table).where(sequence_table.c.conversation == conversation)
    _ = connection.execute(sequence_statement)

    out = result.rowcount
    return out

# ################################################################################################################################

def open_delivery(connection:'Connection', source:'str', server_name:'str', message_id:'str', event_id:'int') -> 'None':
    """ Opens the delivery record of a received message whose receipt the given event recorded.
    """
    statement = insert(open_table).values(
        kind=OpenKind.Delivery,
        source=source,
        server_name=server_name,
        message_id=message_id,
        event_id=event_id,
    )

    _ = connection.execute(statement)

# ################################################################################################################################
# ################################################################################################################################
