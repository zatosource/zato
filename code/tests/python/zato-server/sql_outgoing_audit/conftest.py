# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The scenario helpers live next to the tests and are imported flat, and the container
# helpers are shared with the zato-common suites.
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from live_sql.containers import start_mysql, start_postgresql, stop_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from live_sql.containers import DatabaseServer

    servergen = Iterator[DatabaseServer]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Host ports the containers listen on - distinct from the other suites'
    # so they can all run alongside each other.
    MySQL_Port      = 23346
    PostgreSQL_Port = 25464

    # Names of the containers so stale ones can be removed
    MySQL_Container      = 'zato-sql-audit-test-mysql'
    PostgreSQL_Container = 'zato-sql-audit-test-postgresql'

    # Database credentials shared by both containers
    Username = 'zato_sql_audit'
    Password = 'test-sql-audit-password'
    DB_Name  = 'zato_sql_audit'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def mysql_server() -> 'servergen':
    """ A MySQL server started on demand in a container.
    """
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
    """ A PostgreSQL server started on demand in a container.
    """
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
# ################################################################################################################################
