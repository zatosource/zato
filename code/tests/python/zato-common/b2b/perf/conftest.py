# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the run and the parties run under gevent as in the server, so the patching runs before anything else is imported.
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
from live_sql.containers import start_mysql, start_postgresql, stop_container
from perf_db import Env_Prefix, PerfDatabase, Type_MySQL, Type_PostgreSQL
from live_sql.env import build_env, database_env
from perf import silence_logging_teardown
from zato.common.audit_log.api import get_audit_engine
from zato.common.test.b2b_perf_seed import clear_database

_ = atexit.register(silence_logging_teardown)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from pytest import FixtureRequest
    from live_sql.containers import DatabaseServer

    databasegen = Iterator[PerfDatabase]
    FixtureRequest = FixtureRequest
    servergen = Iterator[DatabaseServer]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Host ports the containers listen on
    MySQL_Port      = 23386
    PostgreSQL_Port = 25486

    # Names of the containers so stale ones can be removed
    MySQL_Container      = 'zato-b2b-perf-mysql'
    PostgreSQL_Container = 'zato-b2b-perf-postgresql'

    # Database credentials shared by all the containers
    Username = 'zato_b2b'
    Password = 'test-b2b-password'
    DB_Name  = 'zato_b2b'

# The databases each performance test runs against.
_databases = (Type_MySQL, Type_PostgreSQL)

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

@pytest.fixture(params=_databases)
def database(request:'FixtureRequest') -> 'databasegen':
    """ One database of each type, started on first use, with the audit log and the B2B tables empty.
    """
    name = request.param
    server:'DatabaseServer' = request.getfixturevalue(f'{name}_server')
    details = server.details

    with database_env(Env_Prefix, details):

        engine = get_audit_engine()
        clear_database(engine)

        out = PerfDatabase()
        out.name = name
        out.engine = engine
        out.env = build_env(Env_Prefix, details)

        yield out

# ################################################################################################################################
# ################################################################################################################################
