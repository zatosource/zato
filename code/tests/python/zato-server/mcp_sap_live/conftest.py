# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The shared harness lives with the other cross-suite libraries and the OData
# test server lives with the shared OData client libraries
_this_directory = os.path.dirname(__file__)
_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))
_odata_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'odata', 'lib'))

# The TLS material builder the OData test server imports flat is shared with the soap suite.
_soap_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'soap', 'lib'))

sys.path.insert(0, _this_directory)
sys.path.insert(0, _lib_directory)
sys.path.insert(0, _odata_lib_directory)
sys.path.insert(0, _soap_lib_directory)

# pytest
import pytest  # noqa: E402

# Zato
from zato.common.crypto.api import CryptoManager  # noqa: E402

# Zato - test helpers
from mcp_connections import harness  # noqa: E402

# The LLM agent harness modules import flat.
harness.add_llm_harness_to_path()

# Zato - test helpers
import ollama_containers  # noqa: E402
from odata_test_server import ODataTestServer, Profile  # noqa: E402

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
Security_Name = 'test.mcp.connections.sap.auth'
Group_Name = 'mcp.test-connections-sap-group'
Connection_Name = 'erp.sales'
Gateway_Name = 'test.mcp.connections.sap'
Gateway_Path = '/mcp/connections-sap'

Username = 'test.mcp.connections.sap.user'
Password = 'test.mcp.connections.sap.password'

# What the connection's tool is called - the group prefix plus the fs-safe connection name
Tool_Name = 'sap.erp_sales'

# The credentials the simulated S/4HANA system enforces
Backend_Username = 'test.sap.user'

# The entity set the tests read and the parties its seeded orders sell to
Entity_Set = 'A_SalesOrder'
Sold_To_Party_First = 'CUST-17'
Sold_To_Party_Second = 'CUST-23'

# ################################################################################################################################
# ################################################################################################################################

def _build_enmasse_config(backend_address:'str', backend_password:'str') -> 'any_':
    """ The import document of the suite - the security definition, its group,
    the SAP connection against the simulated S/4HANA system and the gateway exposing it.
    """

    gateway = harness.build_gateway_entry(
        Gateway_Name, Gateway_Path, Group_Name,
        sap_connections=[Connection_Name])

    out = {
        'security': [
            harness.build_basic_auth_entry(Security_Name, Username, Password),
        ],
        'groups': [
            harness.build_group_entry(Group_Name, [Security_Name]),
        ],
        'sap': [
            {
                'name': Connection_Name,
                'address': backend_address,
                'odata_version': '2.0',
                'auth_type': 'basic',
                'username': Backend_Username,
                'secret': backend_password,
                'needs_csrf_token': True,
            },
        ],
        'mcp_gateway': [gateway],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - the simulated S/4HANA system, a quickstart environment
    and one enmasse import that creates the connection and the gateway exposing it.
    """

    # The simulated S/4HANA system comes up first, with credentials of this run's own,
    # speaking OData V2 with the CSRF exchange its profile enforces on writes ..
    backend_password = 'test.sap.' + CryptoManager.generate_hex_string()

    backend_server = ODataTestServer(Profile.S4HANA)
    backend_server.start()
    backend_server.set_credentials(Backend_Username, backend_password)

    # .. with a small, predictable set of sales orders ..
    backend_server.add_entities(Entity_Set, 'SalesOrder', [
        {'SalesOrder': '1', 'SalesOrderType': 'OR', 'SoldToParty': Sold_To_Party_First, 'TotalNetAmount': 100},
        {'SalesOrder': '2', 'SalesOrderType': 'OR', 'SoldToParty': Sold_To_Party_Second, 'TotalNetAmount': 250},
    ])

    # .. the quickstart environment follows ..
    environment = harness.start_environment('mcp_connections_sap')

    try:
        # .. one import creates everything ..
        backend_address = backend_server.service_root + '/'
        harness.run_enmasse_import(environment.server_directory, _build_enmasse_config(backend_address, backend_password))

        # .. and the suite starts once the gateway lists the connection tool.
        mcp_url = environment.mcp_url(Gateway_Path)
        auth = (Username, Password)

        harness.wait_for_gateway_tool(mcp_url, auth, Tool_Name)

        yield {
            'environment': environment,
            'mcp_url': mcp_url,
            'auth': auth,
            'backend_server': backend_server,
        }

    finally:
        backend_server.stop()
        harness.stop_environment(environment)

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
