# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The shared harness lives with the other cross-suite libraries
_this_directory = os.path.dirname(__file__)
_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))

sys.path.insert(0, _this_directory)
sys.path.insert(0, _lib_directory)

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
from _confluence_server import ConfluenceTestHandler, start_confluence_server  # noqa: E402

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
Security_Name = 'test.mcp.connections.confluence.auth'
Group_Name = 'mcp.test-connections-confluence-group'
Connection_Name = 'kb.main'
Gateway_Name = 'test.mcp.connections.confluence'
Gateway_Path = '/mcp/connections-confluence'

Username = 'test.mcp.connections.confluence.user'
Password = 'test.mcp.connections.confluence.password'

# What the connection's tool is called - the group prefix plus the fs-safe connection name
Tool_Name = 'confluence.kb_main'

# The credentials the simulated Confluence site enforces
Backend_Username = 'test.confluence.user'

# What the simulated site's initial spaces are called
Space_Engineering = 'Engineering wiki'
Space_Product = 'Product documentation'

# ################################################################################################################################
# ################################################################################################################################

def _build_enmasse_config(backend_port:'int', backend_token:'str') -> 'any_':
    """ The import document of the suite - the security definition, its group,
    the Confluence connection against the simulated site and the gateway exposing it.
    """

    gateway = harness.build_gateway_entry(
        Gateway_Name, Gateway_Path, Group_Name,
        confluence_connections=[Connection_Name])

    out = {
        'security': [
            harness.build_basic_auth_entry(Security_Name, Username, Password),
        ],
        'groups': [
            harness.build_group_entry(Group_Name, [Security_Name]),
        ],
        'confluence': [
            {
                'name': Connection_Name,
                'address': f'http://127.0.0.1:{backend_port}',
                'username': Backend_Username,
                'secret': backend_token,
                'is_cloud': False,
            },
        ],
        'mcp_gateway': [gateway],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - the simulated Confluence site, a quickstart environment
    and one enmasse import that creates the connection and the gateway exposing it.
    """

    # The simulated site comes up first, with a token of this run's own ..
    backend_token = 'test.token.' + CryptoManager.generate_hex_string()

    backend_port = harness.find_free_port()
    backend_server, _ignored_thread = start_confluence_server(backend_port, Backend_Username, backend_token)

    # .. the quickstart environment follows ..
    environment = harness.start_environment('mcp_connections_confluence')

    try:
        # .. one import creates everything ..
        harness.run_enmasse_import(environment.server_directory, _build_enmasse_config(backend_port, backend_token))

        # .. and the suite starts once the gateway lists the connection tool.
        mcp_url = environment.mcp_url(Gateway_Path)
        auth = (Username, Password)

        harness.wait_for_gateway_tool(mcp_url, auth, Tool_Name)

        yield {
            'environment': environment,
            'mcp_url': mcp_url,
            'auth': auth,
            'backend_handler': ConfluenceTestHandler,
        }

    finally:
        backend_server.shutdown()
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
