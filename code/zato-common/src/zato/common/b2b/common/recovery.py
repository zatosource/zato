# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.audit_log.api import AuditBody, event_attr_table, event_body_table, event_table
from zato.common.b2b.common.schema import open_table
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from sqlalchemy.sql import Select
    from zato.common.typing_ import any_, anylist, intanydict, intlist, strintdict, strlist
    any_ = any_
    anylist = anylist
    Connection = Connection
    intanydict = intanydict
    intlist = intlist
    Select = Select
    strintdict = strintdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# How many values one IN list holds.
In_List_Size = 500

# ################################################################################################################################
# ################################################################################################################################

def open_statement(kind:'str', source:'str', server_name:'str') -> 'Select':
    """ Returns the query of the open records of one kind that one server holds.
    """
    conditions = and_(
        open_table.c.source == source,
        open_table.c.server_name == server_name,
        open_table.c.kind == kind,
    )

    out = select(open_table.c.message_id, open_table.c.event_id).where(conditions)
    return out

# ################################################################################################################################

def events_statement(source:'str', server_name:'str', message_ids:'strlist', event_types:'any_') -> 'Select':
    """ Returns the query of the events of the given messages that one server recorded, in the order they were recorded.
    """
    conditions = and_(
        event_table.c.msg_id.in_(message_ids),
        event_table.c.source == source,
        event_table.c.server_name == server_name,
        event_table.c.event_type.in_(event_types),
    )

    out = select(event_table).where(conditions).order_by(event_table.c.id)
    return out

# ################################################################################################################################

def attrs_statement(event_ids:'intlist') -> 'Select':
    """ Returns the query of the attributes of the given events.
    """
    query = select(event_attr_table.c.event_id, event_attr_table.c.name, event_attr_table.c.value)

    out = query.where(event_attr_table.c.event_id.in_(event_ids))
    return out

# ################################################################################################################################

def body_statement(event_id:'int') -> 'Select':
    """ Returns the query of the attachment stored with one event.
    """
    conditions = and_(
        event_body_table.c.event_id == event_id,
        event_body_table.c.kind == AuditBody.Attachment,
    )

    out = select(event_body_table.c.data).where(conditions).order_by(event_body_table.c.id)
    return out

# ################################################################################################################################
# ################################################################################################################################

def read_open(connection:'Connection', kind:'str', source:'str', server_name:'str') -> 'strintdict':
    """ Returns the event that starts each open record of one kind, by its message identifier.
    """
    statement = open_statement(kind, source, server_name)

    out:'strintdict' = {}

    for row in connection.execute(statement):
        out[row.message_id] = row.event_id

    return out

# ################################################################################################################################

def read_events(
    connection:'Connection',
    source:'str',
    server_name:'str',
    message_ids:'strlist',
    event_types:'any_',
    ) -> 'dict[str, anylist]':
    """ Returns the events of the given messages, by message identifier, each list in the order the events were recorded.
    """
    out:'dict[str, anylist]' = {}

    for message_id in message_ids:
        out[message_id] = []

    for start in range(0, len(message_ids), In_List_Size):

        chunk = message_ids[start:start + In_List_Size]
        statement = events_statement(source, server_name, chunk, event_types)

        for row in connection.execute(statement):
            events = out[row.msg_id]
            events.append(row)

    return out

# ################################################################################################################################

def read_attrs(connection:'Connection', event_ids:'intlist') -> 'intanydict':
    """ Returns the attributes of each of the given events, by the event's identifier.
    """
    out:'intanydict' = {}

    for event_id in event_ids:
        out[event_id] = {}

    for start in range(0, len(event_ids), In_List_Size):

        chunk = event_ids[start:start + In_List_Size]
        statement = attrs_statement(chunk)

        for row in connection.execute(statement):
            event_attrs = out[row.event_id]
            event_attrs[row.name] = row.value

    return out

# ################################################################################################################################

def read_bodies(connection:'Connection', event_id:'int') -> 'list[bytes]':
    """ Returns the bytes of each attachment stored with one event, in the order they were stored.
    """
    statement = body_statement(event_id)

    out:'list[bytes]' = []

    for row in connection.execute(statement):
        envelope = loads(row.data)
        content = b64decode(envelope['content'])
        out.append(content)

    return out

# ################################################################################################################################
# ################################################################################################################################
