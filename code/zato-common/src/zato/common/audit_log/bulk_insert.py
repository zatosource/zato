# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The inserts of the audit log that write all the rows of one table in a batch with a single statement.

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.common import event_table
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.db_env.pg8000_copy import copy_rows
from zato.common.db_env.plain_sql import PlainStatement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Dialect
    from sqlalchemy.sql.schema import Table
    from zato.common.typing_ import anydict, dictlist, intlist

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    Dialect = Dialect
    dictlist = dictlist
    intlist = intlist
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

# The multi-row insert of each table, by the name of the table
_insert_statements:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

def returns_ordered_ids(dialect:'Dialect') -> 'bool':
    """ Whether a multi-row insert on this database returns the ids of the rows in the order of the rows.
    """
    out = dialect.name == Type_PostgreSQL
    return out

# ################################################################################################################################

def _insert_returning(connection:'Connection', rows:'dictlist') -> 'intlist':
    """ Inserts the event rows with one statement that returns their ids in the order of the rows.
    """
    statement = event_table.insert()
    statement = statement.returning(event_table.c.id, sort_by_parameter_order=True)

    result = connection.execute(statement, rows)

    out = list(result.scalars())
    return out

# ################################################################################################################################

def _insert_by_commit_id(connection:'Connection', rows:'dictlist', commit_id:'str') -> 'intlist':
    """ Inserts the event rows stamped with the id of their commit and selects their ids by it, in insertion order.
    """
    commit_rows:'dictlist' = []

    for row in rows:
        commit_row = dict(row)
        commit_row['commit_id'] = commit_id
        commit_rows.append(commit_row)

    insert_statement = event_table.insert()
    _ = connection.execute(insert_statement, commit_rows)

    query = select(event_table.c.id)
    query = query.where(event_table.c.commit_id == commit_id)
    query = query.order_by(event_table.c.id)

    result = connection.execute(query)

    out = list(result.scalars())
    return out

# ################################################################################################################################

def insert_events(connection:'Connection', rows:'dictlist', commit_id:'str') -> 'intlist':
    """ Inserts the event rows of one batch and returns their ids in the order of the rows.
    """

    # A single event receives its id from the insert itself ..
    if len(rows) == 1:
        inserted = _insert_event_statement.insert_rows(connection, rows)
        out = [inserted[0].id]

    # .. a database that returns the ids of a multi-row insert in order receives them with the insert ..
    elif returns_ordered_ids(connection.dialect):
        out = _insert_returning(connection, rows)

    # .. and any other one selects them by the id of the commit.
    else:
        out = _insert_by_commit_id(connection, rows, commit_id)

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
            insert_statement = PlainStatement(table.insert())
            _insert_statements[table.name] = insert_statement

        _ = insert_statement.insert_rows(connection, rows)

# ################################################################################################################################
# ################################################################################################################################
