# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import delete, func, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, metadata as audit_metadata
from zato.common.b2b.common.commit_sql import EventWrite
from zato.common.b2b.common.schema import create_tables, held_message_table, message_table, open_table, sequence_table
from zato.common.test.b2b_write_path import Server, Source

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Table
    from sqlalchemy.engine import Connection, Engine
    from sqlalchemy.sql import ClauseElement, Select
    from zato.common.typing_ import stranydict, strlist
    ClauseElement = ClauseElement
    Connection = Connection
    Engine = Engine
    Select = Select
    stranydict = stranydict
    strlist = strlist
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# The prefix of the environment variables the audit log database is configured through.
Env_Prefix = 'Zato_Audit_Log_DB_'

Type_SQLite     = 'sqlite'
Type_MySQL      = 'mysql'
Type_PostgreSQL = 'postgresql'
Type_Oracle     = 'oracle'

# The program that runs the other side of the tests in a process of its own.
Child_Program = os.path.join(os.path.dirname(__file__), 'child.py')

# Each line a child prints when it reaches a point the test waits for.
Line_Ready      = 'ready'
Line_Committing = 'committing'
Line_Claimed    = 'claimed'

# The tables whose statistics the query planners read.
_planned_tables = ('event', 'event_attr', 'event_body', 'b2b_open')

# The statement under which Oracle DB stores an explained plan.
_oracle_statement_id = 'zato_b2b'

# The plan operations of Oracle DB that read a table or an index in full.
_oracle_full_options = ('FULL', 'FULL SCAN', 'FAST FULL SCAN')

# The access types of MySQL that read a table or an index in full.
_mysql_full_types = ('ALL', 'index')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LiveDB:
    """ One database the live tests run against.
    """
    name: str
    engine: 'Engine'

    # The environment variables a child process connects to the database with.
    env: 'stranydict'

# ################################################################################################################################
# ################################################################################################################################

def clear_tables(engine:'Engine') -> 'None':
    """ Creates the B2B tables if needed and deletes every row of them and of the audit log.
    """
    create_tables(engine)

    with engine.begin() as connection:

        for table in (open_table, message_table, sequence_table, held_message_table):
            _ = connection.execute(delete(table))

        for table in reversed(audit_metadata.sorted_tables):
            _ = connection.execute(delete(table))

# ################################################################################################################################

def count_rows(engine:'Engine', table:'Table', *conditions:'ClauseElement') -> 'int':
    query = select(func.count()).select_from(table)

    if conditions:
        query = query.where(*conditions)

    with engine.connect() as connection:
        out = connection.execute(query).scalar_one()

    return out

# ################################################################################################################################

def new_event(audit_log:'AuditLog', message_id:'str', event_type:'str'=AuditEvent.Message_Sent) -> 'EventWrite':
    """ Returns an event whose attribute and body both hold the identifier of its message.
    """
    out = EventWrite()
    out.pending = audit_log.new_pending_event(Source, event_type, 'b2b-agreement', msg_id=message_id, data='{}',
        attrs={'b2b_marker': message_id}, bodies={'request': message_id})

    return out

# ################################################################################################################################

def new_audit_log() -> 'AuditLog':
    out = AuditLog(Server, flush_max_size=1)
    return out

# ################################################################################################################################
# ################################################################################################################################

def child_env(database:'LiveDB') -> 'stranydict':
    out = dict(os.environ)
    out.update(database.env)

    return out

# ################################################################################################################################

def start_child(database:'LiveDB', *args:'str') -> 'subprocess.Popen[str]':
    """ Starts the child program and returns its process, whose output is read line by line.
    """
    command = [sys.executable, Child_Program]
    command.extend(args)

    env = child_env(database)

    out = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return out

# ################################################################################################################################

def wait_for_line(process:'subprocess.Popen[str]', expected:'str') -> 'None':
    """ Reads the output of a child process until a line says what is expected.
    """
    stdout = process.stdout
    if stdout is None:
        raise Exception('The child process has no output to read')

    while True:
        line = stdout.readline()

        if not line:
            stderr = process.stderr
            if stderr is None:
                raise Exception(f'The child process ended before `{expected}`')
            raise Exception(f'The child process ended before `{expected}`: {stderr.read()}')

        if line.strip() == expected:
            return

# ################################################################################################################################
# ################################################################################################################################

def gather_statistics(database:'LiveDB') -> 'None':
    """ Makes the query planner of the database read the current contents of the tables of the recovery queries.
    """
    with database.engine.connect() as connection:

        if database.name == Type_SQLite:
            _ = connection.exec_driver_sql('ANALYZE')

        elif database.name == Type_PostgreSQL:
            for table_name in _planned_tables:
                _ = connection.exec_driver_sql(f'ANALYZE {table_name}')

        elif database.name == Type_MySQL:
            table_names = ', '.join(_planned_tables)
            _ = connection.exec_driver_sql(f'ANALYZE TABLE {table_names}').all()

        else:
            for table_name in _planned_tables:
                upper_name = table_name.upper()
                _ = connection.exec_driver_sql(f"BEGIN DBMS_STATS.GATHER_TABLE_STATS(USER, '{upper_name}'); END;")

        connection.commit()

# ################################################################################################################################

def _sqlite_full_scans(connection:'Connection', sql:'str') -> 'strlist':
    out:'strlist' = []

    for row in connection.exec_driver_sql('EXPLAIN QUERY PLAN ' + sql):
        detail = row[3]
        if detail.startswith('SCAN '):
            out.append(detail)

    return out

# ################################################################################################################################

def _postgresql_full_scans(connection:'Connection', sql:'str') -> 'strlist':

    # A small table is read in full whenever that is cheaper, so only the indexes the planner can use are compared.
    _ = connection.exec_driver_sql('SET enable_seqscan = off')

    out:'strlist' = []

    for row in connection.exec_driver_sql('EXPLAIN ' + sql):
        line = row[0]
        if 'Seq Scan' in line:
            out.append(line)

    return out

# ################################################################################################################################

def _mysql_full_scans(connection:'Connection', sql:'str') -> 'strlist':
    out:'strlist' = []

    for row in connection.exec_driver_sql('EXPLAIN ' + sql).mappings():
        if row['type'] in _mysql_full_types:
            out.append(f'{row["table"]} {row["type"]}')

    return out

# ################################################################################################################################

def _oracle_full_scans(connection:'Connection', sql:'str') -> 'strlist':
    statement_id = _oracle_statement_id

    _ = connection.exec_driver_sql(f"DELETE FROM plan_table WHERE statement_id = '{statement_id}'")
    _ = connection.exec_driver_sql(f"EXPLAIN PLAN SET STATEMENT_ID = '{statement_id}' FOR {sql}")

    query = f"SELECT operation, options, object_name FROM plan_table WHERE statement_id = '{statement_id}'"

    out:'strlist' = []

    for operation, options, object_name in connection.exec_driver_sql(query):
        if options in _oracle_full_options:
            out.append(f'{operation} {options} {object_name}')

    return out

# ################################################################################################################################

def full_scans(database:'LiveDB', statement:'Select') -> 'strlist':
    """ Returns each step of the plan of a statement that reads a table or an index in full.
    """
    engine = database.engine
    compiled = statement.compile(dialect=engine.dialect, compile_kwargs={'literal_binds': True})
    sql = str(compiled)

    with engine.connect() as connection:

        if database.name == Type_SQLite:
            out = _sqlite_full_scans(connection, sql)

        elif database.name == Type_PostgreSQL:
            out = _postgresql_full_scans(connection, sql)

        elif database.name == Type_MySQL:
            out = _mysql_full_scans(connection, sql)

        else:
            out = _oracle_full_scans(connection, sql)

        connection.rollback()

    return out

# ################################################################################################################################
# ################################################################################################################################
