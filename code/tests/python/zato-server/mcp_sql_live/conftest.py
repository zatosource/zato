# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The shared harness and the container helpers live with the other cross-suite libraries
_this_directory = os.path.dirname(__file__)
_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))

sys.path.insert(0, _this_directory)
sys.path.insert(0, _lib_directory)

# pytest
import pytest  # noqa: E402

# SQLAlchemy
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.pool import NullPool  # noqa: E402

# Zato - test helpers
from live_sql.containers import start_postgresql, stop_container  # noqa: E402
from mcp_connections import harness  # noqa: E402

# The LLM agent harness modules import flat.
harness.add_llm_harness_to_path()

# Zato - test helpers
import ollama_containers  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, tupnone

# ################################################################################################################################
# ################################################################################################################################

def pytest_report_teststatus(report:'any_', config:'any_') -> 'tupnone':
    if report.when == 'call':
        outcome = report.outcome.upper()
        return report.outcome, f' {outcome} ', f'{outcome} {report.nodeid}'
    return None

# ################################################################################################################################
# ################################################################################################################################

# What the suite's objects are called
Security_Name = 'test.mcp.connections.sql.auth'
Group_Name = 'mcp.test-connections-sql-group'
Connection_Name = 'reporting.db'
Gateway_Name = 'test.mcp.connections.sql'
Gateway_Path = '/mcp/connections-sql'

Username = 'test.mcp.connections.sql.user'
Password = 'test.mcp.connections.sql.password'

# What the connection's tool is called - the group prefix plus the fs-safe connection name
Tool_Name = 'sql.reporting_db'

# The container the database runs in - the port is distinct from the other suites'.
DB_Container = 'zato-mcp-connections-test-postgresql'
DB_Port = 25467
DB_Username = 'zato_mcp_connections'
DB_Password = 'test-mcp-connections-password'
DB_Name = 'zato_mcp_connections'

# What the seeded table holds
Table_Name = 'account_balances'
Seeded_Customer = '123'
Seeded_Balance = 357

# ################################################################################################################################
# ################################################################################################################################

def _seed_database() -> 'None':
    """ Creates the balances table and puts the one row the tests ask about in it.
    """

    engine_url = f'postgresql+pg8000://{DB_Username}:{DB_Password}@127.0.0.1:{DB_Port}/{DB_Name}'
    engine = create_engine(engine_url, poolclass=NullPool)

    with engine.connect() as connection:
        _ = connection.execute(text(f'create table {Table_Name} (customer_id text, balance integer)'))
        _ = connection.execute(text(f"insert into {Table_Name} values ('{Seeded_Customer}', {Seeded_Balance})"))

    engine.dispose()

# ################################################################################################################################

def _build_enmasse_config() -> 'any_':
    """ The import document of the suite - the security definition, its group,
    the SQL connection against the container and the gateway exposing it.
    """

    gateway = harness.build_gateway_entry(
        Gateway_Name, Gateway_Path, Group_Name,
        sql_connections=[Connection_Name])

    out = {
        'security': [
            harness.build_basic_auth_entry(Security_Name, Username, Password),
        ],
        'groups': [
            harness.build_group_entry(Group_Name, [Security_Name]),
        ],
        'sql': [
            {
                'name': Connection_Name,
                'type': 'postgresql',
                'host': '127.0.0.1',
                'port': DB_Port,
                'db_name': DB_Name,
                'username': DB_Username,
                'password': DB_Password,
            },
        ],
        'mcp_gateway': [gateway],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - a PostgreSQL container with seeded data, a quickstart
    environment and one enmasse import that creates the connection and the gateway.
    """

    if not ollama_containers.is_docker_available():
        pytest.skip('Docker is not available')

    # The database comes up first and gets its data ..
    database_server = start_postgresql(
        container_name=DB_Container,
        port=DB_Port,
        username=DB_Username,
        password=DB_Password,
        db_name=DB_Name,
        needs_ssl=False,
    )

    _seed_database()

    # .. the quickstart environment follows ..
    environment = harness.start_environment('mcp_connections_sql')

    try:
        # .. one import creates everything ..
        harness.run_enmasse_import(environment.server_directory, _build_enmasse_config())

        # .. and the suite starts once the gateway lists the connection tool.
        mcp_url = environment.mcp_url(Gateway_Path)
        auth = (Username, Password)

        harness.wait_for_gateway_tool(mcp_url, auth, Tool_Name)

        yield {
            'environment': environment,
            'mcp_url': mcp_url,
            'auth': auth,
        }

    finally:
        harness.stop_environment(environment)
        stop_container(database_server.container_name)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def ollama() -> 'any_':
    """ Session-scoped fixture that makes sure the Ollama container is running
    with the model pulled - only the test that drives the model depends on it.
    """

    if not ollama_containers.is_docker_available():
        pytest.skip('Docker is not available')

    ollama_containers.ensure_ollama()
    ollama_containers.ensure_model()

    out = {
        'openai_url': ollama_containers.Ollama_OpenAI_URL,
        'model': ollama_containers.Model_Name,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
