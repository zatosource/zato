# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import and_, delete, exists, func, or_, select

# Zato
from zato.common.audit_log.api import AuditEvent, event_body_table, event_table, get_retention_days
from zato.common.b2b.common.schema import b2b_event_table, held_message_table, message_table, open_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import any_, intlist, strlist
    any_ = any_
    Connection = Connection
    datetime = datetime
    intlist = intlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# How many identifiers one IN list of a select or a delete holds.
_in_list_size = 500

# The event types of the B2B exchanges, business transactions, received messages and ordered conversations.
B2B_Event_Types = (
    AuditEvent.Message_Sent,
    AuditEvent.Message_Resent,
    AuditEvent.Signal_Received,
    AuditEvent.Message_Completed,
    AuditEvent.Business_Message_Sent,
    AuditEvent.Business_Reply_Received,
    AuditEvent.Business_Timed_Out,
    AuditEvent.Business_Delivery_Failed,
    AuditEvent.Message_Received,
    AuditEvent.Message_Delivered,
    AuditEvent.Message_Redelivered,
    AuditEvent.Message_Held,
    AuditEvent.Sequence_Gap_Timed_Out,
    AuditEvent.Sequence_Gap_Released,
    AuditEvent.Conversation_Discarded,
    AuditEvent.Delivery_Suspended,
    AuditEvent.Delivery_Resumed,
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RetentionResult:
    """ How many rows one run of retention deleted.
    """
    messages: int
    held:     int
    events:   int

    def is_at_limit(self, limit:'int') -> 'bool':
        """ Says whether one kind of row reached the row limit, so that more rows of it may be due for deletion.
        """
        out = False

        for count in (self.messages, self.held, self.events):
            if count >= limit:
                out = True

        return out

# ################################################################################################################################

@dataclass(init=False)
class RetentionCandidates:
    """ The identifiers of the rows one run of retention found due for deletion - the records of received messages,
    the held messages of each source and the B2B audit events.
    """
    messages: 'intlist'
    held:     'dict[str, intlist]'
    events:   'intlist'

# ################################################################################################################################
# ################################################################################################################################

def _select_ids(connection:'Connection', statement:'any_') -> 'intlist':
    """ Returns the identifiers a select of one column returns.
    """
    out:'intlist' = []

    for row_id in connection.execute(statement).scalars():
        out.append(row_id)

    return out

# ################################################################################################################################

def _delete_by_ids(connection:'Connection', column:'any_', ids:'intlist', *conditions:'any_') -> 'int':
    """ Deletes the rows whose given column holds one of the identifiers and which meet the conditions,
    in IN lists of a bounded size, and returns how many it deleted.
    """
    out = 0

    for start in range(0, len(ids), _in_list_size):
        chunk = ids[start:start + _in_list_size]
        statement = delete(column.table).where(column.in_(chunk), *conditions)
        result = connection.execute(statement)
        out += result.rowcount

    return out

# ################################################################################################################################

def _retention_cutoff(source:'str', now:'datetime') -> 'datetime':
    retention_days = get_retention_days(source)
    retention = timedelta(days=retention_days)

    out = now - retention
    return out

# ################################################################################################################################
# ################################################################################################################################

def select_expired_messages(connection:'Connection', now:'datetime', limit:'int') -> 'intlist':
    """ Returns up to the limit of the identifiers of the records of received messages whose duplicate detection
    window has passed.
    """
    query = select(message_table.c.id).where(message_table.c.expires_at <= now)
    statement = query.limit(limit)

    out = _select_ids(connection, statement)
    return out

# ################################################################################################################################

def delete_expired_messages(connection:'Connection', now:'datetime', ids:'intlist') -> 'int':
    """ Deletes the records of received messages with the given identifiers whose duplicate detection window
    is still passed, since a claim of the same message replaces an expired record, and returns how many it deleted.
    """
    out = _delete_by_ids(connection, message_table.c.id, ids, message_table.c.expires_at <= now)
    return out

# ################################################################################################################################
# ################################################################################################################################

def select_old_held(connection:'Connection', source:'str', now:'datetime', limit:'int') -> 'intlist':
    """ Returns up to the limit of the identifiers of the held messages of one source that were held for longer
    than the retention of the source.
    """
    cutoff = _retention_cutoff(source, now)

    of_source = and_(
        event_table.c.id == held_message_table.c.event_id,
        event_table.c.source == source,
    )
    is_of_source = exists(select(event_table.c.id).where(of_source))

    conditions = and_(
        held_message_table.c.held_at < cutoff,
        is_of_source,
    )
    statement = select(held_message_table.c.id).where(conditions).limit(limit)

    out = _select_ids(connection, statement)
    return out

# ################################################################################################################################

def delete_old_held(connection:'Connection', source:'str', now:'datetime', ids:'intlist') -> 'int':
    """ Deletes the held messages of one source with the given identifiers that are still held for longer
    than the retention of the source, and returns how many it deleted.
    """
    cutoff = _retention_cutoff(source, now)

    out = _delete_by_ids(connection, held_message_table.c.id, ids, held_message_table.c.held_at < cutoff)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _is_event_kept(held_ids:'intlist') -> 'any_':
    """ Returns the condition under which an event is kept whatever its age - the exchange, business transaction
    or delivery of its message is open, or the message is held other than by one of the given held messages.
    """
    is_open_conditions = and_(
        open_table.c.message_id == event_table.c.msg_id,
        open_table.c.source == event_table.c.source,
    )
    is_open = exists(select(open_table.c.id).where(is_open_conditions))

    is_held_conditions = and_(
        held_message_table.c.message_id == event_table.c.msg_id,
        held_message_table.c.id.not_in(held_ids),
    )
    is_held = exists(select(held_message_table.c.id).where(is_held_conditions))

    out = or_(is_open, is_held)
    return out

# ################################################################################################################################

def select_old_events(
    connection:'Connection',
    source:'str',
    now:'datetime',
    limit:'int',
    held_ids:'intlist',
    ) -> 'intlist':
    """ Returns up to the limit of the identifiers of the B2B audit events of one source that are older than
    the retention of the source and are not kept. The given held messages are deleted before the events,
    so the events of their receipt are not kept on their account.
    """
    cutoff = _retention_cutoff(source, now)

    conditions = and_(
        event_table.c.source == source,
        event_table.c.event_type.in_(B2B_Event_Types),
        event_table.c.event_time < cutoff,
        ~_is_event_kept(held_ids),
    )
    statement = select(event_table.c.id).where(conditions).limit(limit)

    out = _select_ids(connection, statement)
    return out

# ################################################################################################################################

def delete_events(connection:'Connection', ids:'intlist') -> 'int':
    """ Deletes the B2B audit events with the given identifiers that are still not kept, together with their
    attributes and bodies, and returns how many events it deleted.
    """
    is_not_kept = ~_is_event_kept([])

    deleted:'intlist' = []

    # The events a message opened or held since they were selected are kept ..
    for start in range(0, len(ids), _in_list_size):
        chunk = ids[start:start + _in_list_size]
        statement = select(event_table.c.id).where(event_table.c.id.in_(chunk), is_not_kept)
        deleted.extend(_select_ids(connection, statement))

    # .. and the rows that reference an event go before the event itself.
    _ = _delete_by_ids(connection, b2b_event_table.c.event_id, deleted)
    _ = _delete_by_ids(connection, event_body_table.c.event_id, deleted)
    _ = _delete_by_ids(connection, event_table.c.id, deleted)

    out = len(deleted)
    return out

# ################################################################################################################################

def delete_old_events(connection:'Connection', source:'str', now:'datetime', limit:'int') -> 'int':
    """ Deletes up to the limit of the B2B audit events of one source that are older than the retention of the source,
    together with their attributes and bodies, and returns how many events it deleted. The events of a message
    whose exchange, business transaction or delivery is open, or which is held, are kept, whatever their age.
    """
    ids = select_old_events(connection, source, now, limit, [])

    out = delete_events(connection, ids)
    return out

# ################################################################################################################################
# ################################################################################################################################

def select_retained(connection:'Connection', now:'datetime', sources:'strlist', limit:'int') -> 'RetentionCandidates':
    """ Returns the identifiers of what retention deletes, each kind of row up to the row limit.
    """
    out = RetentionCandidates()
    out.messages = select_expired_messages(connection, now, limit)
    out.held = {}
    out.events = []

    # A held message goes before the events of its receipt, which are kept while it is held.
    for source in sources:
        held_ids = select_old_held(connection, source, now, limit)
        out.held[source] = held_ids
        out.events.extend(select_old_events(connection, source, now, limit, held_ids))

    return out

# ################################################################################################################################

def read_candidate_rows(connection:'Connection', candidates:'RetentionCandidates') -> 'None':
    """ Reads the attributes and the bodies of the events retention found due for deletion, the bodies in full,
    so that their deletion finds the pages it changes in the memory of the database.
    """
    ids = candidates.events

    for start in range(0, len(ids), _in_list_size):
        chunk = ids[start:start + _in_list_size]

        # Each attribute row is read from its table rather than from an index ..
        attrs = select(func.count(b2b_event_table.c.final_state)).where(b2b_event_table.c.event_id.in_(chunk))
        _ = connection.execute(attrs).scalar()

        # .. and each body is read with all of its stored parts.
        data = func.count(func.md5(event_body_table.c.data))
        content = func.count(func.md5(event_body_table.c.content))
        bodies = select(data, content).where(event_body_table.c.event_id.in_(chunk))
        _ = connection.execute(bodies).one()

# ################################################################################################################################

def delete_candidates(connection:'Connection', now:'datetime', candidates:'RetentionCandidates') -> 'RetentionResult':
    """ Deletes the rows retention found due for deletion that are still due, and returns how many rows it deleted.
    """
    out = RetentionResult()
    out.messages = delete_expired_messages(connection, now, candidates.messages)
    out.held = 0

    # The held messages go before the events of their receipt ..
    for source, held_ids in candidates.held.items():
        out.held += delete_old_held(connection, source, now, held_ids)

    # .. which are then no longer kept on their account.
    out.events = delete_events(connection, candidates.events)

    return out

# ################################################################################################################################

def delete_retained(connection:'Connection', now:'datetime', sources:'strlist', limit:'int') -> 'RetentionResult':
    """ Deletes what retention deletes, each kind of row up to the row limit, and returns how many rows it deleted.
    """
    candidates = select_retained(connection, now, sources, limit)

    out = delete_candidates(connection, now, candidates)
    return out

# ################################################################################################################################
# ################################################################################################################################
