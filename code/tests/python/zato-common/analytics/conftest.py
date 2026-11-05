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
from live_sql.containers import start_postgresql, stop_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from live_sql.containers import DatabaseServer

    servergen = Iterator[DatabaseServer]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The host port the container listens on - distinct from the audit log test suite's
    # so both suites can run at the same time.
    PostgreSQL_Port = 25442

    # The name of the container so a stale one can be removed
    PostgreSQL_Container = 'zato-analytics-test-postgresql'

    # The database credentials of the container
    Username = 'zato_analytics'
    Password = 'test-analytics-password'
    DB_Name  = 'zato_analytics'

# ################################################################################################################################
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
