# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The complete SQL audit scenario every backend must pass - a connection that never
# opted in leaves no trail, each capture level carries exactly what it promised
# and nothing more, a failed statement is recorded before the caller learns about it,
# and a level nobody defined refuses to build a connection at all.

# stdlib
import os
from contextlib import contextmanager
from json import loads

# gevent
from gevent import sleep as gevent_sleep

# SQLAlchemy
from sqlalchemy import create_engine, select, text
from sqlalchemy.pool import NullPool

# Zato
from live_sql.env import database_env
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource, \
    ModuleCtx as AuditLogCtx
from zato.common.odb.api import PoolStore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.odb.api import SessionWrapper
    from zato.common.typing_ import any_, anylist, stranydict

    envgen = Iterator[None]
    conngen = Iterator['SessionWrapper']

# ################################################################################################################################
# ################################################################################################################################

# The server the audit events are written under
Server_Name = 'test-sql-audit-server'

# The name the connection under test goes by
Connection_Name = 'test.sql.audit'

# The engines the scenario runs against
Engine_MySQL      = 'mysql+pymysql'
Engine_PostgreSQL = 'postgresql+pg8000'

# The table the statements under test run against and what it holds
_table_name = 'lab_results'

_seed_rows = [
    {'code': 'A1', 'label': 'First'},
    {'code': 'A2', 'label': 'Second'},
]

# The statements the checks run
_select_all     = f'select code, label from {_table_name} order by code'
_select_by_code = f'select code, label from {_table_name} where code = :code'

_select_params = {'code': 'A2'}

# A statement that no backend can run - the table it names does not exist
_select_missing_table = f'select code from {_table_name}_missing'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# How long to wait for a session wrapper to finish its initialization
_init_timeout_seconds = 5

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _audit_db_env(tmp_path:'any_', check_name:'str') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database of one check's own.
    """
    directory = os.path.join(str(tmp_path), check_name)
    os.makedirs(directory)

    db_path = os.path.join(directory, 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################

def _seed_table(details:'stranydict', engine_name:'str') -> 'None':
    """ Creates the table the statements under test run against, with known rows -
    containers can be reused between test runs so the table always starts from scratch.
    """
    url = '{}://{}:{}@{}:{}/{}'.format(engine_name,
        details['username'], details['password'], details['host'], details['port'], details['name'])

    engine = create_engine(url, poolclass=NullPool)

    with engine.begin() as connection:
        _ = connection.execute(text(f'drop table if exists {_table_name}'))
        _ = connection.execute(text(f'create table {_table_name} (code varchar(20), label varchar(200))'))

        for row in _seed_rows:
            _ = connection.execute(text(f'insert into {_table_name} (code, label) values (:code, :label)'), row)

    engine.dispose()

# ################################################################################################################################

@contextmanager
def _new_connection(details:'stranydict', engine_name:'str', extra:'str') -> 'conngen':
    """ Builds the connection under test through the pool store - the same wiring
    a server uses - and takes it apart when the block ends.
    """
    config = {
        'name': Connection_Name,
        'is_active': True,
        'engine': engine_name,
        'host': details['host'],
        'port': details['port'],
        'username': details['username'],
        'password': details['password'],
        'db_name': details['name'],
        'pool_size': 1,
        'fs_sql_config': {},
        'extra': extra,
    }

    store = PoolStore(server_name=Server_Name)
    store[Connection_Name] = config

    wrapper = store[Connection_Name]

    # The wrapper initializes its session on a greenlet of its own,
    # so give it a moment when it has not finished yet.
    waited = 0.0

    while not wrapper.session_initialized:
        gevent_sleep(0.05)
        waited += 0.05

        if waited > _init_timeout_seconds:
            raise Exception('The session was not initialized in time')

    try:
        yield wrapper
    finally:
        del store[Connection_Name]

# ################################################################################################################################

def _get_events() -> 'anylist':
    """ Everything the audit log holds, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################

def _get_endpoint(details:'stranydict') -> 'str':
    """ What the events under test say they ran against.
    """
    out = '{}:{}/{}'.format(details['host'], details['port'], details['name'])
    return out

# ################################################################################################################################
# ################################################################################################################################

def _check_no_extra_leaves_no_trail(details:'stranydict', engine_name:'str', tmp_path:'any_') -> 'None':
    """ A connection that never opted in runs its statements and leaves nothing behind.
    """
    with _audit_db_env(tmp_path, 'no-extra'):
        with _new_connection(details, engine_name, '') as conn:

            rows = conn.execute(_select_all)

            assert rows == _seed_rows
            assert _get_events() == []

# ################################################################################################################################

def _check_level_off_leaves_no_trail(details:'stranydict', engine_name:'str', tmp_path:'any_') -> 'None':
    """ Saying off explicitly is the same as saying nothing.
    """
    with _audit_db_env(tmp_path, 'level-off'):
        with _new_connection(details, engine_name, 'audit_log=off') as conn:

            rows = conn.execute(_select_all)

            assert rows == _seed_rows
            assert _get_events() == []

# ################################################################################################################################

def _check_level_statement(details:'stranydict', engine_name:'str', tmp_path:'any_') -> 'None':
    """ The statement level records the SQL text alone - no parameters, no rows.
    """
    with _audit_db_env(tmp_path, 'level-statement'):
        with _new_connection(details, engine_name, 'audit_log=statement') as conn:

            rows = conn.execute(_select_by_code, _select_params)
            assert rows == [_seed_rows[1]]

            events = _get_events()
            assert len(events) == 1

            event = events[0]

            assert event['source'] == AuditSource.SQL_Outgoing
            assert event['event_type'] == AuditEvent.Request_Sent
            assert event['object_name'] == Connection_Name
            assert event['endpoint'] == _get_endpoint(details)
            assert event['outcome'] == AuditOutcome.OK
            assert event['server_name'] == Server_Name

            # Each statement runs under a correlation id of its own
            assert event['cid']

            summary = loads(event['data'])

            assert summary['statement'] == _select_by_code
            assert 'params' not in summary
            assert 'rows' not in summary

# ################################################################################################################################

def _check_level_statement_params(details:'stranydict', engine_name:'str', tmp_path:'any_') -> 'None':
    """ The statement-params level adds the parameters and still keeps the rows out.
    """
    with _audit_db_env(tmp_path, 'level-statement-params'):
        with _new_connection(details, engine_name, 'audit_log=statement-params') as conn:

            _ = conn.execute(_select_by_code, _select_params)

            events = _get_events()
            assert len(events) == 1

            summary = loads(events[0]['data'])

            assert summary['statement'] == _select_by_code
            assert summary['params'] == _select_params
            assert 'rows' not in summary

# ################################################################################################################################

def _check_level_full(details:'stranydict', engine_name:'str', tmp_path:'any_') -> 'None':
    """ The full level carries everything - the statement, its parameters
    and the rows that came back.
    """
    with _audit_db_env(tmp_path, 'level-full'):
        with _new_connection(details, engine_name, 'audit_log=full') as conn:

            rows = conn.execute(_select_by_code, _select_params)
            assert rows == [_seed_rows[1]]

            events = _get_events()
            assert len(events) == 1

            summary = loads(events[0]['data'])

            assert summary['statement'] == _select_by_code
            assert summary['params'] == _select_params
            assert summary['rows'] == [_seed_rows[1]]
            assert summary['row_count'] == 1

# ################################################################################################################################

def _check_a_failed_statement_is_recorded(details:'stranydict', engine_name:'str', tmp_path:'any_') -> 'None':
    """ A statement the database refused leaves an error entry before the caller
    learns about it.
    """
    with _audit_db_env(tmp_path, 'error-outcome'):
        with _new_connection(details, engine_name, 'audit_log=statement') as conn:

            try:
                _ = conn.execute(_select_missing_table)
            except Exception:
                pass
            else:
                raise Exception('A failed statement was expected to propagate')

            events = _get_events()
            assert len(events) == 1

            event = events[0]

            assert event['outcome'] == AuditOutcome.Error

            summary = loads(event['data'])

            assert summary['statement'] == _select_missing_table
            assert summary['error']

# ################################################################################################################################

def _check_an_unknown_level_is_refused(details:'stranydict', engine_name:'str', tmp_path:'any_') -> 'None':
    """ A level nobody defined refuses to build a connection at all.
    """
    with _audit_db_env(tmp_path, 'unknown-level'):

        try:
            with _new_connection(details, engine_name, 'audit_log=everything'):
                pass
        except Exception as e:
            assert 'Unknown SQL audit level' in str(e)
        else:
            raise Exception('An unknown audit level was expected to be refused')

# ################################################################################################################################
# ################################################################################################################################

def run_sql_audit_scenario(details:'stranydict', engine_name:'str', tmp_path:'any_') -> 'None':
    """ The complete SQL audit scenario every backend must pass.
    """

    # The statements under test always run against known rows
    _seed_table(details, engine_name)

    # No opt-in and an explicit off leave no trail
    _check_no_extra_leaves_no_trail(details, engine_name, tmp_path)
    _check_level_off_leaves_no_trail(details, engine_name, tmp_path)

    # Each level carries exactly what it promised and nothing more
    _check_level_statement(details, engine_name, tmp_path)
    _check_level_statement_params(details, engine_name, tmp_path)
    _check_level_full(details, engine_name, tmp_path)

    # A failed statement is recorded before the caller learns about it
    _check_a_failed_statement_is_recorded(details, engine_name, tmp_path)

    # A level nobody defined refuses to build a connection at all
    _check_an_unknown_level_is_refused(details, engine_name, tmp_path)

# ################################################################################################################################
# ################################################################################################################################
