# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The bulk insert of the audit log on SQLite, which writes all the rows of a batch in Rust, with the GIL released,
# through the handle of the driver's connection and in the transaction that the connection holds open.

# stdlib
from sqlite3 import Error as SQLiteError, sqlite_version

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.audit_log.attachment import get_attachment_bodies
from zato.common.audit_log.common import event_attr_table, event_body_table, event_link_table, event_payload_table, event_table
from zato.common.db_env.common import UTC_DateTime
from zato.common.db_env.write_path import check_write_path
from zato.common.typing_ import cast_

# Zato - Rust
from zato_common_core.zato_common_core import SQLiteAuditWriter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from sqlalchemy.sql.schema import Table
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import any_, anylist, intlist, strlist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anylist = anylist
    Connection = Connection
    intlist = intlist
    pending_event_list = pending_event_list
    strlist = strlist
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# The column of the event table that the database assigns
_event_id_column = event_table.c.id.name

# The column of the event table that references the row of the payload, which the writer binds last
_payload_id_column = event_table.c.payload_id.name

# The column of the time of an event, which the body rows of the event are stamped with
_event_time_column = event_table.c.event_time.name

# The statement that opens the transaction the driver opens itself before a statement that changes rows
_begin_statement = 'BEGIN'

# ################################################################################################################################
# ################################################################################################################################

def _insert_statement(table:'Table', column_names:'strlist') -> 'str':
    """ Returns the insert of one row of a table, with one positional parameter per column.
    """
    columns = ', '.join(column_names)
    parameters = ', '.join(['?'] * len(column_names))

    out = f'INSERT INTO {table.name} ({columns}) VALUES ({parameters})'
    return out

# ################################################################################################################################

def _get_event_columns() -> 'anylist':
    """ Returns the name of each column of the event table that the values of an event provide,
    in the order of the table, along with whether the column holds a time.
    """
    out:'anylist' = []

    for column in event_table.columns:
        if column.name not in (_event_id_column, _payload_id_column):
            is_time = isinstance(column.type, UTC_DateTime)
            out.append((column.name, is_time))

    return out

# ################################################################################################################################

def _get_column_names(table:'Table') -> 'strlist':
    """ Returns the names of the columns of a table except for its id, which the database assigns.
    """
    out:'strlist' = []

    for column in table.columns:
        if column.name != table.c.id.name:
            out.append(column.name)

    return out

# ################################################################################################################################
# ################################################################################################################################

_event_columns = _get_event_columns()

_event_insert_columns:'strlist' = []

for _name, _ in _event_columns:
    _event_insert_columns.append(_name)

_event_insert_columns.append(_payload_id_column)

# The statements of the writer, each checked against the mechanism of the write before a batch is written
_insert_event = _insert_statement(event_table, _event_insert_columns)
_select_payload = f'SELECT id FROM {event_payload_table.name} WHERE digest = ?'
_insert_payload = _insert_statement(event_payload_table, _get_column_names(event_payload_table)) + ' ON CONFLICT (digest) DO NOTHING'
_insert_attr = _insert_statement(event_attr_table, _get_column_names(event_attr_table))
_insert_body = _insert_statement(event_body_table, _get_column_names(event_body_table))
_insert_link = _insert_statement(event_link_table, _get_column_names(event_link_table))

_write_statements = [_insert_event, _select_payload, _insert_payload, _insert_attr, _insert_body, _insert_link]

_writer = SQLiteAuditWriter({
    'sqlite_version': sqlite_version,
    'event_columns': _event_columns,
    'event_time_column': _event_time_column,
    'insert_event': _insert_event,
    'select_payload': _select_payload,
    'insert_payload': _insert_payload,
    'insert_attr': _insert_attr,
    'insert_body': _insert_body,
    'insert_link': _insert_link,
    'attachment_bodies': get_attachment_bodies,
})

# ################################################################################################################################
# ################################################################################################################################

def insert_pending_events_sqlite(connection:'Connection', batch:'pending_event_list') -> 'intlist':
    """ Inserts the events of one batch with their payloads, attributes, bodies and lineage links in the transaction
    of the connection, and returns the ids of the events in the order of the batch.
    """

    # The statements are checked against the mechanism of the write, as each statement of the driver is ..
    for statement in _write_statements:
        check_write_path(None, None, statement, None, None, True)

    dbapi_connection = cast_('any_', connection.connection.dbapi_connection)

    # .. the driver opens the transaction itself only before a statement of its own, so it is opened here ..
    if not dbapi_connection.in_transaction:
        _ = connection.exec_driver_sql(_begin_statement)

    # .. and an error of the database is raised as the driver's errors are, so the callers recognize it.
    try:
        out = _writer.insert_events(dbapi_connection, batch)
    except SQLiteError as error:
        raise DBAPIError.instance(None, None, error, SQLiteError) from error

    return out

# ################################################################################################################################
# ################################################################################################################################
