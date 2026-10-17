# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

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

    # Host ports the containers listen on - distinct from the audit log test suite's
    # so both suites can run at the same time.
    MySQL_Port      = 23316
    PostgreSQL_Port = 25442

    # Names of the containers so stale ones can be removed
    MySQL_Container      = 'zato-analytics-test-mysql'
    PostgreSQL_Container = 'zato-analytics-test-postgresql'

    # Database credentials shared by all the containers
    Username = 'zato_analytics'
    Password = 'test-analytics-password'
    DB_Name  = 'zato_analytics'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def mysql_server() -> 'servergen':
    """ A plain MySQL server started on demand in a container, holding the audit log.
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
    """ A plain PostgreSQL server started on demand in a container, holding the audit log.
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
