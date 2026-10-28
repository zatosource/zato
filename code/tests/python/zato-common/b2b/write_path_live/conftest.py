# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the writer runs under gevent as in the server, so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import atexit
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

# pytest
import pytest

# Zato
from gevent_monitor import pytest_pyfunc_call as pytest_pyfunc_call
from live_db import clear_tables, Env_Prefix, LiveDB, Type_MySQL, Type_PostgreSQL, Type_SQLite
from live_sql.containers import start_mysql, start_postgresql, stop_container
from live_sql.env import build_env, database_env
from perf import silence_logging_teardown
from zato.common.audit_log.api import get_audit_engine
from zato.common.b2b.common.commit_group import GroupCommitWriter

_ = atexit.register(silence_logging_teardown)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from pathlib import Path
    from pytest import FixtureRequest
    from live_sql.containers import DatabaseServer
    from zato.common.typing_ import stranydict

    databasegen = Iterator[LiveDB]
    FixtureRequest = FixtureRequest
    Path = Path
    servergen = Iterator[DatabaseServer]
    writergen = Iterator[GroupCommitWriter]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Host ports the containers listen on
    MySQL_Port      = 23376
    PostgreSQL_Port = 25476

    # Names of the containers so stale ones can be removed
    MySQL_Container      = 'zato-b2b-write-path-mysql'
    PostgreSQL_Container = 'zato-b2b-write-path-postgresql'

    # Database credentials shared by all the containers
    Username = 'zato_b2b'
    Password = 'test-b2b-password'
    DB_Name  = 'zato_b2b'

# How long the writer of a test waits between two commits, in milliseconds.
Interval_Ms = 10

# The databases each live test runs against.
_databases = (Type_SQLite, Type_MySQL, Type_PostgreSQL)

# The file name of the SQLite database of a test.
_sqlite_file_name = 'audit.db'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def mysql_server() -> 'servergen':
    server = start_mysql(
        container_name=ModuleCtx.MySQL_Container,
        port=ModuleCtx.MySQL_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=False,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='session')
def postgresql_server() -> 'servergen':
    server = start_postgresql(
        container_name=ModuleCtx.PostgreSQL_Container,
        port=ModuleCtx.PostgreSQL_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=False,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################

def _details(request:'FixtureRequest', name:'str', tmp_path:'Path') -> 'stranydict':
    """ Returns the connection details of one database, starting its container on first use.
    """
    if name == Type_SQLite:
        path = tmp_path / _sqlite_file_name
        out = {'type': Type_SQLite, 'name': str(path)}

    else:
        server:'DatabaseServer' = request.getfixturevalue(f'{name}_server')
        out = server.details

    return out

# ################################################################################################################################

@pytest.fixture(params=_databases)
def database(request:'FixtureRequest', tmp_path:'Path') -> 'databasegen':
    """ One database of each type, with the audit log and the B2B tables empty.
    """
    name = request.param
    details = _details(request, name, tmp_path)

    with database_env(Env_Prefix, details):

        engine = get_audit_engine()
        clear_tables(engine)

        out = LiveDB()
        out.name = name
        out.engine = engine
        out.env = build_env(Env_Prefix, details)

        yield out

# ################################################################################################################################

@pytest.fixture
def writer(database:'LiveDB') -> 'writergen':
    """ A writer whose commit loop, a greenlet under gevent, commits the writes of a test.
    """
    out = GroupCommitWriter(database.engine, interval_ms=Interval_Ms)
    yield out

    out.stop()

# ################################################################################################################################
# ################################################################################################################################
