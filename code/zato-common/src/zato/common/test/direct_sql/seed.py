# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Seeding test data in bulk - the rows that a test needs before the system under test uses them are inserted
# in transactions as large as the seed requires, with the durability settings of every other write. A seed creates
# and removes rows and its scratch tables, and never changes a row that a test or the system under test wrote.

# stdlib
from contextlib import contextmanager

# Zato
from zato.common.audit_log.bulk_insert import insert_pending_events
from zato.common.db_env.engine import call_database
from zato.common.db_env.write_path import Mechanism, write_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy import Table
    from sqlalchemy.engine import Connection, Engine
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import any_, callable_, dictlist, intlist, stranydict

    any_ = any_
    stranydict = stranydict
    intlist = intlist
    pending_event_list = pending_event_list
    callable_ = callable_
    Connection = Connection
    dictlist = dictlist
    Engine = Engine
    Iterator = Iterator
    Table = Table

    table_rows_list = list[tuple[Table, dictlist]]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The isolation level under which each statement commits on its own
    Autocommit = 'AUTOCOMMIT'

# ################################################################################################################################
# ################################################################################################################################

def _run_in_transaction(engine:'Engine', func:'callable_', args:'any_') -> 'any_':
    with engine.begin() as connection:
        out = func(connection, *args)

    return out

# ################################################################################################################################

def _insert_rows(connection:'Connection', table_rows:'table_rows_list') -> 'None':

    # The tables are filled in the order given, so that rows referring to others follow them
    for table, rows in table_rows:
        if rows:
            _ = connection.execute(table.insert(), rows)

# ################################################################################################################################

def run_seed(engine:'Engine', func:'callable_', *args:'any_') -> 'any_':
    """ Runs a function that writes seed rows on the connection it receives, in one transaction,
    in turn with the other writes to the database. Returns what the function returns.
    """
    with write_path(Mechanism.Seed):
        out = call_database(engine, _run_in_transaction, engine, func, args)

    return out

# ################################################################################################################################

def _insert_row(connection:'Connection', table:'Table', values:'stranydict') -> 'any_':
    result = connection.execute(table.insert(), values)

    out = result.inserted_primary_key[0]
    return out

# ################################################################################################################################

def seed_rows(engine:'Engine', table_rows:'table_rows_list') -> 'None':
    """ Inserts the rows of each table in one transaction, in turn with the other writes to the database.
    """
    _ = run_seed(engine, _insert_rows, table_rows)

# ################################################################################################################################

def seed_row(engine:'Engine', table:'Table', values:'stranydict') -> 'any_':
    """ Inserts one row in a transaction of its own, in turn with the other writes to the database,
    and returns its primary key.
    """
    out = run_seed(engine, _insert_row, table, values)
    return out

# ################################################################################################################################

def seed_audit_events(engine:'Engine', batch:'pending_event_list') -> 'intlist':
    """ Inserts audit events that AuditLog.new_pending_event built, each complete with its own time, which may be
    in the past, together with their attributes, bodies and links, in one transaction. Returns the ids of the events
    in the order of the batch.
    """
    out = run_seed(engine, insert_pending_events, batch)
    return out

# ################################################################################################################################

@contextmanager
def seed_autocommit_connection(engine:'Engine') -> 'Iterator[Connection]':
    """ Yields a connection on which each statement of a seed commits on its own, outside of a transaction.
    """
    with write_path(Mechanism.Seed):
        connection = engine.connect()
        connection = connection.execution_options(isolation_level=ModuleCtx.Autocommit)

        try:
            yield connection
        finally:
            connection.close()

# ################################################################################################################################
# ################################################################################################################################
