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
from typing import NamedTuple

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.bulk_insert import insert_pending_events
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.db_env.database import get_database_engine
from zato.common.db_env.engine import call_database
from zato.common.db_env.pg8000_copy import copy_rows
from zato.common.db_env.write_path import Mechanism, write_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from datetime import datetime
    from sqlalchemy import Table
    from sqlalchemy.engine import Connection, Engine
    from sqlalchemy.orm import Session
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import any_, anylist, anytuple, callable_, dictlist, intlist, stranydict, strtuple

    any_ = any_
    anylist = anylist
    datetime = datetime
    anytuple = anytuple
    stranydict = stranydict
    strtuple = strtuple
    intlist = intlist
    pending_event_list = pending_event_list
    callable_ = callable_
    Connection = Connection
    dictlist = dictlist
    Engine = Engine
    Iterator = Iterator
    Session = Session
    Table = Table

    table_rows_list = list[tuple[Table, dictlist]]
    tablelist = list[Table]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The isolation level under which each statement commits on its own
    Autocommit = 'AUTOCOMMIT'

    # How many rows of a bulk seed one statement carries
    Bulk_Batch_Size = 50_000

# ################################################################################################################################
# ################################################################################################################################

class BulkLoad(NamedTuple):
    """ The rows of one table of a bulk seed - the names of the columns they fill, the rows as tuples in the order
    of the names, and whether the rows give the values of the identity column themselves.
    """
    table: 'Table'
    names: 'strtuple'
    rows: 'Iterator[anytuple]'
    has_identity: 'bool'

bulk_load_list = list[BulkLoad]

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

def seed_config_row(session:'Session', table:'Table', values:'stranydict') -> 'any_':
    """ Inserts one row into a table of config.db through a session of its own and returns its primary key,
    for the models whose constructors do not accept every column.
    """
    result = session.execute(table.insert().values(**values))
    session.commit()

    out = result.inserted_primary_key[0]
    return out

# ################################################################################################################################

def seed_config_objects(session:'Session', objects:'anylist') -> 'None':
    """ Adds configuration objects to a session of config.db, which writes them with the rest of its transaction.
    """
    session.add_all(objects)

# ################################################################################################################################

def seed_audit_events(engine:'Engine', batch:'pending_event_list') -> 'intlist':
    """ Inserts audit events that AuditLog.new_pending_event built, each complete with its own time, which may be
    in the past, together with their attributes, bodies and links, in one transaction. Returns the ids of the events
    in the order of the batch.
    """
    out = run_seed(engine, insert_pending_events, batch)
    return out

# ################################################################################################################################

def seed_event(
    audit_log:'AuditLog',
    event_time:'datetime',
    source:'str',
    event_type:'str',
    object_name:'str',
    **kwargs:'any_',
    ) -> 'int':
    """ Inserts one audit event that took place at the given time, which may be in the past, built as AuditLog.insert
    builds it from the same arguments, and returns its id.
    """
    pending = audit_log.new_pending_event(source, event_type, object_name, **kwargs)
    pending.values['event_time'] = event_time

    engine = get_database_engine()
    event_ids = seed_audit_events(engine, [pending])

    out = event_ids[0]
    return out

# ################################################################################################################################

class SeedAuditLog(AuditLog):
    """ An audit log whose every event is seeded as having taken place at one given time, which may be in the past,
    so that the code which records its events through an audit log produces its rows complete with their event time.
    """

    def __init__(self, server_name:'str', event_time:'datetime') -> 'None':
        super().__init__(server_name)
        self.event_time = event_time

    def insert(self, source:'str', event_type:'str', object_name:'str', *, needs_id:'bool'=False, **kwargs:'any_') -> 'int':
        out = seed_event(self, self.event_time, source, event_type, object_name, **kwargs)
        return out

# ################################################################################################################################

def _get_batches(load:'BulkLoad') -> 'Iterator[dictlist]':
    """ Yields the rows of one table in batches of at most Bulk_Batch_Size rows each.
    """
    batch:'dictlist' = []

    for row in load.rows:
        values = dict(zip(load.names, row))
        batch.append(values)

        if len(batch) == ModuleCtx.Bulk_Batch_Size:
            yield batch
            batch = []

    if batch:
        yield batch

# ################################################################################################################################

def _load_in_bulk(connection:'Connection', loads:'bulk_load_list') -> 'None':
    is_postgresql = connection.dialect.name == Type_PostgreSQL

    for load in loads:

        # PostgreSQL receives each batch as one COPY stream, and the other databases as one executemany ..
        for batch in _get_batches(load):
            if is_postgresql:
                copy_rows(connection, load.table, batch)
            else:
                _ = connection.execute(load.table.insert(), batch)

        # .. and a COPY with the values of an identity column leaves its sequence behind them,
        # which the next row of the system under test would collide with.
        if is_postgresql and load.has_identity:
            table_name = load.table.name
            column_name = load.table.primary_key.columns[0].name

            sequence = f"pg_get_serial_sequence('{table_name}', '{column_name}')"
            statement = f'select setval({sequence}, (select max({column_name}) from {table_name}))'

            _ = connection.exec_driver_sql(statement)

# ################################################################################################################################

def seed_bulk(engine:'Engine', loads:'bulk_load_list') -> 'None':
    """ Inserts the rows of each table over the fastest path of the database - COPY on PostgreSQL and executemany
    on the other databases - in one transaction, in turn with the other writes to the database. The rows are read
    from their iterators as they are inserted, so a seed of any size is never held in memory at once.
    """
    _ = run_seed(engine, _load_in_bulk, loads)

# ################################################################################################################################

def _refresh_statistics(engine:'Engine', tables:'tablelist') -> 'None':

    dialect_name = engine.dialect.name
    table_names = [table.name for table in tables]

    # VACUUM runs outside of a transaction only, and it builds the visibility map that index-only scans of PostgreSQL need ..
    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level=ModuleCtx.Autocommit)

        if dialect_name == Type_PostgreSQL:
            for table_name in table_names:
                _ = connection.exec_driver_sql(f'vacuum analyze {table_name}')

        # .. and SQLite analyzes the whole database.
        else:
            _ = connection.exec_driver_sql('analyze')

# ################################################################################################################################

def refresh_statistics(engine:'Engine', tables:'tablelist') -> 'None':
    """ Refreshes the statistics of the optimizer of the database after a bulk seed, so that the queries
    of the system under test are planned against the seeded rows rather than against the empty tables.
    """
    with write_path(Mechanism.Seed):
        _ = call_database(engine, _refresh_statistics, engine, tables)

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
