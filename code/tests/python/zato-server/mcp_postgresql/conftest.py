# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The tests start their PostgreSQL server with the container helpers of the main repository
_main_lib_dir = os.path.expanduser('~/projects/zatosource-zato/4.1/code/tests/python/zato-common/lib')
sys.path.insert(0, _main_lib_dir)

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

    # The host port and the name of the container, distinct from those of the other suites
    PostgreSQL_Port = 25448
    PostgreSQL_Container = 'zato-mcp-sessions-test-postgresql'

    Username = 'zato_mcp_sessions'
    Password = 'test-mcp-sessions-password'
    DB_Name  = 'zato_mcp_sessions'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def postgresql_server() -> 'servergen':
    """ A PostgreSQL server in a container, which holds the pub/sub database with the MCP sessions.
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
