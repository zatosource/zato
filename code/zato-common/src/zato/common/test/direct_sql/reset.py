# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Resetting tables between tests - the tables of a schema are emptied so that the next test starts from no rows.

# SQLAlchemy
from sqlalchemy import inspect

# Zato
from zato.common.common_db.schema import shared_object_table
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.db_env.engine import call_database
from zato.common.db_env.write_path import Mechanism, write_path
from zato.common.odb.model import GenericConn, IntervalBasedJob, Job

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData, Table
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import Session
    from zato.common.typing_ import any_

    any_ = any_
    Engine = Engine
    MetaData = MetaData
    Session = Session
    Table = Table

    tablelist = list[Table]

# ################################################################################################################################
# ################################################################################################################################

def _delete_all_rows(engine:'Engine', metadata:'MetaData') -> 'None':

    # The tables that others refer to are emptied after the tables that refer to them
    tables = reversed(metadata.sorted_tables)

    with engine.begin() as connection:
        for table in tables:
            _ = connection.execute(table.delete())

# ################################################################################################################################

def _delete_rows_of(engine:'Engine', tables:'tablelist') -> 'None':

    with engine.begin() as connection:
        for table in tables:
            _ = connection.execute(table.delete())

# ################################################################################################################################

def reset_table_rows(engine:'Engine', tables:'tablelist') -> 'None':
    """ Deletes every row of each given table in one transaction, in the order given, in turn with the other writes
    to the database.
    """
    with write_path(Mechanism.Seed):
        _ = call_database(engine, _delete_rows_of, engine, tables)

# ################################################################################################################################

def reset_tables(engine:'Engine', metadata:'MetaData') -> 'None':
    """ Deletes every row of every table of a schema in one transaction, in turn with the other writes to the database.
    The rows are removed as a seed removes its own, which no other mechanism may do to the tables of the audit log.
    """
    with write_path(Mechanism.Seed):
        _ = call_database(engine, _delete_all_rows, engine, metadata)

# ################################################################################################################################

def _truncate_tables(engine:'Engine', tables:'tablelist') -> 'None':

    dialect_name = engine.dialect.name
    table_names = [table.name for table in tables]

    with engine.begin() as connection:

        # PostgreSQL truncates a table together with the tables that refer to it in one statement ..
        if dialect_name == Type_PostgreSQL:
            joined = ', '.join(table_names)
            _ = connection.exec_driver_sql(f'truncate table {joined} restart identity')

        # .. and SQLite truncates a table that has no triggers when it deletes all of its rows.
        else:
            for table_name in table_names:
                _ = connection.exec_driver_sql(f'delete from {table_name}')

# ################################################################################################################################

def truncate_tables(engine:'Engine', tables:'tablelist') -> 'None':
    """ Empties the given tables in one transaction over the fastest path of the database, in turn with the other writes
    to the database. The tables that others refer to are given after the tables that refer to them.
    """
    with write_path(Mechanism.Seed):
        _ = call_database(engine, _truncate_tables, engine, tables)

# ################################################################################################################################

def _delete_shared_objects(engine:'Engine', object_type:'str') -> 'None':

    # A database that no server has started on yet has no table of shared objects
    if not inspect(engine).has_table(shared_object_table.name):
        return

    statement = shared_object_table.delete()
    statement = statement.where(shared_object_table.c.object_type == object_type)

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def delete_shared_objects(engine:'Engine', object_type:'str') -> 'None':
    """ Deletes the shared objects of one type that an earlier test left behind, in turn with the other writes
    to the database.
    """
    with write_path(Mechanism.Seed):
        _ = call_database(engine, _delete_shared_objects, engine, object_type)

# ################################################################################################################################

def recreate_public_schema(connection:'any_') -> 'None':
    """ Drops the public schema of a PostgreSQL database together with everything in it and creates it anew,
    through a connection of the database driver with the privileges of the owner of the schema, in autocommit mode.
    """
    cursor = connection.cursor()

    _ = cursor.execute('drop schema public cascade')
    _ = cursor.execute('create schema public')

# ################################################################################################################################

def delete_generic_connections(session:'Session', name_pattern:'str') -> 'None':
    """ Deletes the generic connections of config.db whose names match a pattern of SQL LIKE and commits.
    """
    query = session.query(GenericConn).filter(GenericConn.name.like(name_pattern))
    _ = query.delete(synchronize_session=False)

    session.commit()

# ################################################################################################################################

def delete_config_job(session:'Session', job_name:'str') -> 'None':
    """ Deletes one scheduler job of config.db together with its interval and commits, which leaves config.db
    as an environment that never started holds it.
    """
    job = session.query(Job).filter(Job.name==job_name).one()

    _ = session.query(IntervalBasedJob).filter(IntervalBasedJob.job_id==job.id).delete()
    session.delete(job)

    session.commit()

# ################################################################################################################################
# ################################################################################################################################
