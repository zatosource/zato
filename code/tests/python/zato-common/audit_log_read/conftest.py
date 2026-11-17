# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the writers run under gevent as in the server, so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import atexit
import gc
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# pytest
import pytest

# Zato
from gevent_monitor import pytest_pyfunc_call as pytest_pyfunc_call
from live_sql.containers import start_postgresql, stop_container
from live_sql.env import database_env
from perf import silence_logging_teardown
from support import Backend_PostgreSQL, Backend_SQLite, delete_all_rows
from zato.common.db_env.database import dispose_database_engine
from zato.common.db_env.database_env import DatabaseEnv

_ = atexit.register(silence_logging_teardown)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from live_sql.containers import DatabaseServer

    servergen = Iterator[DatabaseServer]
    strgen    = Iterator[str]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The host port the container listens on and the name of the container, so a stale one can be removed
    PostgreSQL_Port      = 25587
    PostgreSQL_Container = 'zato-audit-log-read-postgresql'

    # The data directory is in memory and the container uses at most this many CPUs
    CPUs = '2'

    # Database credentials
    Username = 'zato_audit_log_read'
    Password = 'test-audit-log-read-password'
    DB_Name  = 'zato_audit_log_read'

    # The name of the SQLite file in the directory of each test
    SQLite_File_Name = 'zato.db'

# ################################################################################################################################
# ################################################################################################################################

def pytest_collection_finish(session:'pytest.Session') -> 'None':
    """ Excludes the objects loaded with the test modules from the collector, as the arbiter of a server does
    before it starts its processes, so that a full collection during a test scans only what the test creates.
    """
    _ = gc.collect()
    gc.freeze()

# ################################################################################################################################

@pytest.fixture(scope='session')
def postgresql_server() -> 'servergen':
    """ A PostgreSQL server whose data directory is in memory, started for the session and removed after it.
    """
    server = start_postgresql(
        container_name=ModuleCtx.PostgreSQL_Container,
        port=ModuleCtx.PostgreSQL_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=False,
        is_in_memory=True,
        cpus=ModuleCtx.CPUs,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(params=[Backend_SQLite, Backend_PostgreSQL])
def audit_backend(request:'pytest.FixtureRequest', tmp_path:'os.PathLike') -> 'strgen':
    """ Points the audit log at an empty database of each backend in turn and yields the name of the backend.
    """
    backend = request.param

    if backend == Backend_PostgreSQL:
        server = request.getfixturevalue('postgresql_server')
        details = server.details
    else:
        db_path = os.path.join(str(tmp_path), ModuleCtx.SQLite_File_Name)
        details = {
            'type': DatabaseEnv.Type_SQLite,
            'path': db_path,
        }

    with database_env(details):
        delete_all_rows()
        yield backend
        dispose_database_engine()

# ################################################################################################################################
# ################################################################################################################################
