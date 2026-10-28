# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import and_, delete, exists, select

# Zato
from zato.common.audit_log.api import AuditEvent, event_attr_table, event_body_table, event_table, get_retention_days
from zato.common.b2b.common.records import to_iso
from zato.common.b2b.common.schema import message_table, open_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import any_, intlist
    any_ = any_
    Connection = Connection
    datetime = datetime
    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

# How many identifiers one IN list of a delete holds, below the limit of 1,000 that Oracle DB has.
_in_list_size = 500

# The event types of the B2B exchanges and business transactions.
B2B_Event_Types = (
    AuditEvent.Message_Sent,
    AuditEvent.Signal_Received,
    AuditEvent.Message_Completed,
    AuditEvent.Business_Message_Sent,
    AuditEvent.Business_Reply_Received,
    AuditEvent.Business_Timed_Out,
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RetentionResult:
    """ How many rows one run of retention deleted.
    """
    messages: int
    events:   int

# ################################################################################################################################
# ################################################################################################################################

def _delete_by_ids(connection:'Connection', column:'any_', ids:'intlist') -> 'None':
    """ Deletes the rows whose given column holds one of the identifiers, in IN lists of a bounded size.
    """
    for start in range(0, len(ids), _in_list_size):
        chunk = ids[start:start + _in_list_size]
        statement = delete(column.table).where(column.in_(chunk))
        _ = connection.execute(statement)

# ################################################################################################################################

def delete_expired_messages(connection:'Connection', now:'datetime', limit:'int') -> 'int':
    """ Deletes up to the limit of the records of received messages whose duplicate detection window has passed,
    and returns how many it deleted.
    """
    now_iso = to_iso(now)

    query = select(message_table.c.id).where(message_table.c.expires_iso <= now_iso)
    statement = query.limit(limit)

    ids:'intlist' = []

    for message_id in connection.execute(statement).scalars():
        ids.append(message_id)

    _delete_by_ids(connection, message_table.c.id, ids)

    out = len(ids)
    return out

# ################################################################################################################################

def delete_old_events(connection:'Connection', source:'str', now:'datetime', limit:'int') -> 'int':
    """ Deletes up to the limit of the B2B audit events of one source that are older than the retention of the source,
    together with their attributes and bodies, and returns how many events it deleted. The events of a message
    whose exchange or business transaction is open are kept, whatever their age.
    """
    retention_days = get_retention_days(source)
    retention = timedelta(days=retention_days)

    cutoff = now - retention
    cutoff_iso = cutoff.isoformat()

    is_open_conditions = and_(
        open_table.c.message_id == event_table.c.msg_id,
        open_table.c.source == event_table.c.source,
    )
    is_open = exists(select(open_table.c.id).where(is_open_conditions))

    conditions = and_(
        event_table.c.source == source,
        event_table.c.event_type.in_(B2B_Event_Types),
        event_table.c.event_time_iso < cutoff_iso,
        ~is_open,
    )
    statement = select(event_table.c.id).where(conditions).limit(limit)

    ids:'intlist' = []

    for event_id in connection.execute(statement).scalars():
        ids.append(event_id)

    # The rows that reference an event go before the event itself.
    _delete_by_ids(connection, event_attr_table.c.event_id, ids)
    _delete_by_ids(connection, event_body_table.c.event_id, ids)
    _delete_by_ids(connection, event_table.c.id, ids)

    out = len(ids)
    return out

# ################################################################################################################################
# ################################################################################################################################
