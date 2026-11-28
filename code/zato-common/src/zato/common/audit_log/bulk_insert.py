# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The inserts of the audit log that write all the rows of one table in a batch with a single statement.

# stdlib
from typing import NamedTuple

# zato_pg_wire
from zato_pg_wire.zato_pg_wire import encode_column_arrays

# Zato
from zato.common.audit_log.attachment import build_attachment_rows
from zato.common.audit_log.attr_rows import build_attr_rows
from zato.common.audit_log.common import event_attr_table, event_body_table, event_link_table, event_table
from zato.common.audit_log.payload import assign_payload_ids, get_event_rows, store_payloads
from zato.common.db_env.any_of import type_name_of
from zato.common.db_env.pg8000_copy import copy_rows
from zato.common.db_env.plain_sql import PlainStatement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Dialect
    from sqlalchemy.sql.schema import Table
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import any_, anydict, anylist, dictlist, intlist, strlist, strstrdict

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anylist = anylist
    Dialect = Dialect
    strstrdict = strstrdict
    Connection = Connection
    dictlist = dictlist
    intlist = intlist
    pending_event_list = pending_event_list
    strlist = strlist
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# The fewest rows a COPY statement inserts. COPY takes one round trip more than a multi-row insert,
# so the few rows of a single event are inserted with a statement of their own.
_copy_min_rows = 16

# The multi-row insert of each table, by the name of the table
_insert_statements:'anydict' = {}

# The inserts of event rows, by the keys of the rows
_event_inserts:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

class _EventInsert(NamedTuple):
    """ The statement that inserts event rows with given keys and the name, the type and the bind processor
    of each of its columns, in the order of its arrays.
    """
    sql: 'str'
    columns: 'anylist'

# ################################################################################################################################

def _new_event_insert(dialect:'Dialect', column_keys:'strlist') -> '_EventInsert':
    """ Builds the statement that inserts the event rows of one batch from one array per column and returns the id
    that each row received, with the position of the row in the batch. The ids are drawn from the sequence of the table
    once, in a CTE that both the insert and the result read.
    """
    preparer = dialect.identifier_preparer
    table_name = preparer.format_table(event_table)

    columns:'anylist' = []
    arrays:'strlist' = []
    names:'strlist' = []

    for name in column_keys:
        column = event_table.c[name]
        type_name = type_name_of(column.type, dialect)
        processor = column.type.bind_processor(dialect)

        columns.append((name, type_name, processor))
        arrays.append(f'CAST(%s AS {type_name}[])')
        names.append(preparer.quote(name))

    array_list = ', '.join(arrays)
    name_list = ', '.join(names)
    id_name = preparer.quote(event_table.c.id.name)

    sql = f"""WITH event_input AS MATERIALIZED (
SELECT nextval(pg_get_serial_sequence('{event_table.name}', '{event_table.c.id.name}')) AS {id_name}, event_rows.*
FROM unnest({array_list}) WITH ORDINALITY AS event_rows({name_list}, event_position)
), event_inserted AS (
INSERT INTO {table_name} ({id_name}, {name_list}) SELECT {id_name}, {name_list} FROM event_input
)
SELECT {id_name} FROM event_input ORDER BY event_position"""

    out = _EventInsert(sql, columns)
    return out

# ################################################################################################################################

def _insert_events(connection:'Connection', rows:'dictlist') -> 'intlist':
    """ Inserts the event rows of one batch in one statement and returns their ids in the order of the rows.
    """
    column_keys = sorted(rows[0])
    key = tuple(column_keys)

    if not (event_insert := _event_inserts.get(key)):
        event_insert = _new_event_insert(connection.dialect, column_keys)
        _event_inserts[key] = event_insert

    arrays = encode_column_arrays(rows, event_insert.columns)
    result = connection.exec_driver_sql(event_insert.sql, tuple(arrays))

    out:'intlist' = []

    for row in result:
        out.append(row.id)

    return out

# ################################################################################################################################

def insert_events(connection:'Connection', rows:'dictlist', payloads:'strstrdict', search_texts:'strstrdict') -> 'intlist':
    """ Stores the payloads of a batch, keyed by their digests, that are not stored yet, then inserts the event rows
    of get_event_rows with the ids of their payloads' rows, and returns the ids of the events in the order of the rows.
    """
    # The events reference the rows of their payloads, which exist once the payloads are stored.
    if payloads:
        payload_ids = store_payloads(connection, payloads, search_texts)
    else:
        payload_ids = {}

    assign_payload_ids(rows, payload_ids)

    out = _insert_events(connection, rows)
    return out

# ################################################################################################################################

def insert_rows(connection:'Connection', table:'Table', rows:'dictlist') -> 'None':
    """ Inserts rows into a table with a single statement - COPY for many rows and a multi-row insert otherwise.
    All the rows have the same keys.
    """
    row_count = len(rows)

    if row_count >= _copy_min_rows:
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
