# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The inserts of the audit log that write all the rows of one table in a batch with a single statement.

# SQLAlchemy
from sqlalchemy import bindparam, func, select

# Zato
from zato.common.audit_log.attachment import build_attachment_rows
from zato.common.audit_log.attr_rows import build_attr_rows
from zato.common.audit_log.common import event_attr_table, event_body_table, event_link_table, event_table
from zato.common.audit_log.payload import assign_payload_ids, find_stored_payloads, get_event_rows, insert_new_payloads
from zato.common.db_env.pg8000_copy import copy_rows
from zato.common.db_env.plain_sql import PlainStatement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, CursorResult
    from sqlalchemy.sql.schema import Table
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import any_, anydict, anylist, dictlist, intlist, strstrdict

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anylist = anylist
    CursorResult = CursorResult
    strstrdict = strstrdict
    Connection = Connection
    dictlist = dictlist
    intlist = intlist
    pending_event_list = pending_event_list
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# The driver whose connections insert rows with COPY.
_copy_driver = 'pg8000'

# The fewest rows a COPY statement inserts. COPY takes one round trip more than a multi-row insert,
# so the few rows of a single event are inserted with a statement of their own.
_copy_min_rows = 16

# The insert of a single event, which returns its id
_insert_event_statement = PlainStatement(event_table.insert().returning(event_table.c.id))

# The given number of new ids from the sequence of the event table
_event_id_sequence = func.pg_get_serial_sequence(event_table.name, event_table.c.id.name)
_reserve_event_ids = select(func.nextval(_event_id_sequence))
_reserve_event_ids = _reserve_event_ids.select_from(func.generate_series(1, bindparam('row_count')))
_reserve_event_ids_statement = PlainStatement(_reserve_event_ids)

# The multi-row insert of each table, by the name of the table
_insert_statements:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

def _reserve_ids(connection:'Connection', row_count:'int') -> 'CursorResult[any_] | None':
    """ Reserves the ids of a batch of more than one event from the sequence of the event table
    and returns the result whose rows are the ids, which _insert_with_reserved_ids reads.
    """
    if row_count > 1:
        out = _reserve_event_ids_statement.execute(connection, {'row_count': row_count})
    else:
        out = None

    return out

# ################################################################################################################################

def _insert_with_reserved_ids(connection:'Connection', rows:'dictlist', reserved:'CursorResult[any_]') -> 'intlist':
    """ Assigns the reserved ids to the event rows in ascending order and inserts the rows with the ids they were assigned.
    """
    out:'intlist' = list(reserved.scalars())
    out.sort()

    id_rows:'dictlist' = []

    for row, event_id in zip(rows, out):
        id_row = dict(row)
        id_row['id'] = event_id
        id_rows.append(id_row)

    insert_rows(connection, event_table, id_rows)

    return out

# ################################################################################################################################

def _insert_events(connection:'Connection', rows:'dictlist', reserved:'CursorResult[any_] | None') -> 'intlist':
    """ Inserts the event rows of one batch and returns their ids in the order of the rows.
    """

    # A batch of more than one event is inserted with the ids it reserved ..
    if reserved is not None:
        out = _insert_with_reserved_ids(connection, rows, reserved)

    # .. and a single event receives its id from the insert itself.
    else:
        inserted = _insert_event_statement.insert_rows(connection, rows)
        out = [inserted[0].id]

    return out

# ################################################################################################################################

def insert_events(connection:'Connection', rows:'dictlist', payloads:'strstrdict', search_texts:'strstrdict') -> 'intlist':
    """ Stores the payloads of a batch, keyed by their digests, that are not stored yet, then inserts the event rows
    of get_event_rows with the ids of their payloads' rows, and returns the ids of the events in the order of the rows.
    Within deferred_replies, the lookup of the stored payloads and the reservation of the ids are sent before
    either result is read, so their replies arrive together.
    """
    if payloads:
        stored = find_stored_payloads(connection, payloads)
    else:
        stored = None

    reserved = _reserve_ids(connection, len(rows))

    # The events reference the rows of their payloads, which exist once the payloads are stored.
    if stored is not None:
        payload_ids = insert_new_payloads(connection, stored, payloads, search_texts)
    else:
        payload_ids = {}

    assign_payload_ids(rows, payload_ids)

    out = _insert_events(connection, rows, reserved)
    return out

# ################################################################################################################################

def insert_rows(connection:'Connection', table:'Table', rows:'dictlist') -> 'None':
    """ Inserts rows into a table with a single statement - COPY for many rows on pg8000 and a multi-row insert otherwise.
    All the rows have the same keys.
    """
    row_count = len(rows)

    if connection.dialect.driver == _copy_driver and row_count >= _copy_min_rows:
        copy_rows(connection, table, rows)
    else:
        if not (insert_statement := _insert_statements.get(table.name)):
            insert_statement = PlainStatement(table.insert().inline())
            _insert_statements[table.name] = insert_statement

        _ = insert_statement.insert_rows(connection, rows)

# ################################################################################################################################

def insert_pending_events(connection:'Connection', batch:'pending_event_list') -> 'intlist':
    """ Inserts the events of one batch with their attributes, bodies and lineage links in the transaction
    of the connection, with one statement per table, and returns the ids of the events in the order of the batch.
    """
    # The payloads of the batch, each once, are stored before the events that reference them ..
    payloads:'strstrdict' = {}
    search_texts:'strstrdict' = {}

    event_rows = get_event_rows(batch, payloads, search_texts)

    # The companion rows of all the events, one list per table
    attr_rows:'anylist' = []
    body_rows:'anylist' = []
    link_rows:'anylist' = []

    # .. the event rows come next, so everything else can reference their ids ..
    out = insert_events(connection, event_rows, payloads, search_texts)

    for pending, event_id in zip(batch, out):

        # .. the export needs the id once the batch is written ..
        pending.event_id = event_id
        event_time = pending.values['event_time']

        # .. searchable attributes ..
        if pending.attrs:
            event_attr_rows = build_attr_rows(event_id, pending.attrs)
            attr_rows.extend(event_attr_rows)

        # .. message bodies, stamped with the event's own time so pruning never needs a join ..
        for kind, body_data in pending.bodies.items():
            body_rows.append({
                'event_id': event_id,
                'kind': kind,
                'event_time': event_time,
                'data': body_data,
                'content': None,
            })

        # .. attachments, one body row each, stamped the same way ..
        if pending.attachments:
            attachment_rows = build_attachment_rows(event_id, event_time, pending.attachments)
            body_rows.extend(attachment_rows)

        # .. lineage links to parent events ..
        for parent_event_id in pending.parents:
            link_rows.append({
                'child_event_id': event_id,
                'parent_event_id': parent_event_id,
                'link_type': pending.parent_link_type,
            })

    # .. and one statement for each of the tables that has rows to write.
    if attr_rows:
        insert_rows(connection, event_attr_table, attr_rows)

    if body_rows:
        insert_rows(connection, event_body_table, body_rows)

    if link_rows:
        insert_rows(connection, event_link_table, link_rows)

    return out

# ################################################################################################################################
# ################################################################################################################################
