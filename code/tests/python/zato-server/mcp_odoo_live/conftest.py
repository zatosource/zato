# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The shared harness and the Odoo container helper live with the other cross-suite libraries
_this_directory = os.path.dirname(__file__)
_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))

sys.path.insert(0, _this_directory)
sys.path.insert(0, _lib_directory)

# pytest
import pytest  # noqa: E402

# Odoo
import odoolib  # noqa: E402

# Zato
from zato.common.crypto.api import CryptoManager  # noqa: E402

# Zato - test helpers
from live_odoo import containers as odoo_containers  # noqa: E402
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
Security_Name = 'test.mcp.connections.odoo.auth'
Group_Name = 'mcp.test-connections-odoo-group'
Connection_Name = 'erp.main'
Gateway_Name = 'test.mcp.connections.odoo'
Gateway_Path = '/mcp/connections-odoo'

Username = 'test.mcp.connections.odoo.user'
Password = 'test.mcp.connections.odoo.password'

# What the connection's tool is called - the group prefix plus the fs-safe connection name
Tool_Name = 'odoo.erp_main'

# What the containers of the suite are called
Odoo_Container = 'zato-test-mcp-odoo'
Odoo_DB_Container = 'zato-test-mcp-odoo-db'
Odoo_Network = 'zato-test-mcp-odoo-network'

# The database the Odoo server initializes on first start
Odoo_DB_Name = 'zato_test'

# The partners the suite seeds - what the agent reads back
Partner_First = 'Northwind Traders'
Partner_Second = 'Contoso Ltd'

# ################################################################################################################################
# ################################################################################################################################

def _seed_partners(details:'any_') -> 'None':
    """ Creates the partners the tests read - a small, predictable set
    next to whatever the base module installed on its own.
    """

    connection = odoolib.get_connection(
        hostname=details['host'], protocol=details['protocol'], port=details['port'],
        database=details['database'], login=details['user'], password=details['password'])

    partner_model = connection.get_model('res.partner')

    _ = partner_model.create({'name': Partner_First, 'is_company': True})
    _ = partner_model.create({'name': Partner_Second, 'is_company': True})

# ################################################################################################################################
# ################################################################################################################################

def _build_enmasse_config(details:'any_') -> 'any_':
    """ The import document of the suite - the security definition, its group,
    the Odoo connection against the container and the gateway exposing it.
    """

    gateway = harness.build_gateway_entry(
        Gateway_Name, Gateway_Path, Group_Name,
        odoo_connections=[Connection_Name])

    out = {
        'security': [
            harness.build_basic_auth_entry(Security_Name, Username, Password),
        ],
        'groups': [
            harness.build_group_entry(Group_Name, [Security_Name]),
        ],
        'odoo': [
            {
                'name': Connection_Name,
                'host': details['host'],
                'port': details['port'],
                'protocol': details['protocol'],
                'database': details['database'],
                'user': details['user'],
                'password': details['password'],
            },
        ],
        'mcp_gateway': [gateway],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - a real Odoo server in a container, a quickstart
    environment and one enmasse import that creates the connection
    and the gateway exposing it.
    """

    if not ollama_containers.is_docker_available():
        pytest.skip('Docker is not available')

    # The Odoo server comes up first, with a database password of this run's own ..
    db_password = 'test.odoo.' + CryptoManager.generate_hex_string()
    odoo_port = harness.find_free_port()

    odoo_server = odoo_containers.start_odoo(
        container_name=Odoo_Container,
        db_container_name=Odoo_DB_Container,
        network_name=Odoo_Network,
        port=odoo_port,
        db_name=Odoo_DB_Name,
        db_password=db_password,
    )

    try:
        # .. the partners the tests read go in right away ..
        _seed_partners(odoo_server.details)

        # .. the quickstart environment follows ..
        environment = harness.start_environment('mcp_connections_odoo')

        try:
            # .. one import creates everything ..
            harness.run_enmasse_import(environment.server_directory, _build_enmasse_config(odoo_server.details))

            # .. and the suite starts once the gateway lists the connection tool.
            mcp_url = environment.mcp_url(Gateway_Path)
            auth = (Username, Password)

            harness.wait_for_gateway_tool(mcp_url, auth, Tool_Name)

            yield {
                'environment': environment,
                'mcp_url': mcp_url,
                'auth': auth,
                'odoo_details': odoo_server.details,
            }

        finally:
            harness.stop_environment(environment)

    finally:
        odoo_containers.stop_odoo(odoo_server)

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
