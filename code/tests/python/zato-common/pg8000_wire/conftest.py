# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the connections run under gevent as in the server, so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import atexit
import os
import sys
from importlib import import_module

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine

# Zato
from gevent_monitor import pytest_pyfunc_call as pytest_pyfunc_call
from live_sql.containers import start_postgresql, stop_container
from logging_teardown import silence_logging_teardown

_ = atexit.register(silence_logging_teardown)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Engine
    from live_sql.containers import DatabaseServer

    enginegen = Iterator[Engine]
    servergen = Iterator[DatabaseServer]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The host port the container listens on and the name of the container, so a stale one can be removed
    PostgreSQL_Port      = 25576
    PostgreSQL_Container = 'zato-pg8000-wire-postgresql'

    # The container uses at most this many CPUs
    CPUs = '2'

    # Database credentials
    Username = 'zato_pg8000_wire'
    Password = 'test-pg8000-wire-password'
    DB_Name  = 'zato_pg8000_wire'

    # The module whose import applies the extensions of pg8000 once per process
    PG8000_Install_Module = 'zato.common.db_env.pg8000_install'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def postgresql_server() -> 'servergen':
    """ A PostgreSQL server, started for the session and removed after it.
    """
    _ = import_module(ModuleCtx.PG8000_Install_Module)

    server = start_postgresql(
        container_name=ModuleCtx.PostgreSQL_Container,
        port=ModuleCtx.PostgreSQL_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=False,
        cpus=ModuleCtx.CPUs,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture
def engine(postgresql_server:'DatabaseServer') -> 'enginegen':
    """ An engine of the PostgreSQL server, disposed of after each test.
    """
    details  = postgresql_server.details
    username = details['username']
    password = details['password']
    port     = details['port']
    db_name  = details['name']

    engine_url = f'postgresql+pg8000://{username}:{password}@localhost:{port}/{db_name}'

    out = create_engine(engine_url)
    yield out

    out.dispose()

# ################################################################################################################################
# ################################################################################################################################
