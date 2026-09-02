# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The shared harness lives with the other cross-suite libraries and the live SOAP
# test server lives in the zato-common SOAP suite, shared by every suite that needs one
_this_directory = os.path.dirname(__file__)
_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))
_soap_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'soap', 'lib'))

sys.path.insert(0, _this_directory)
sys.path.insert(0, _lib_directory)
sys.path.insert(0, _soap_lib_directory)

# pytest
import pytest  # noqa: E402

# Zato - test helpers
from mcp_connections import harness  # noqa: E402

# The LLM agent harness modules import flat.
harness.add_llm_harness_to_path()

# Zato - test helpers
import ollama_containers  # noqa: E402
from soap_test_server import SOAPTestServer  # noqa: E402

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
Security_Name = 'test.mcp.connections.soap.auth'
Group_Name = 'mcp.test-connections-soap-group'
Connection_Name = 'erp.invoicing'
Gateway_Name = 'test.mcp.connections.soap'
Gateway_Path = '/mcp/connections-soap'

Username = 'test.mcp.connections.soap.user'
Password = 'test.mcp.connections.soap.password'

# What the connection's tool is called - the group prefix plus the fs-safe connection name
Tool_Name = 'soap.erp_invoicing'

# Where the ERP test server answers
Backend_Path = '/erp/WS/Codeunit/InvoiceEntryService'

# The action the connection sends
SOAP_Action = 'urn:example-erp/codeunit/InvoiceEntryService:CreateInvoiceHeader'

# ################################################################################################################################
# ################################################################################################################################

def _build_enmasse_config(backend_address:'str') -> 'any_':
    """ The import document of the suite - the security definition, its group,
    the outgoing SOAP connection against the ERP test server and the gateway exposing it.
    """

    gateway = harness.build_gateway_entry(
        Gateway_Name, Gateway_Path, Group_Name,
        soap_connections=[Connection_Name])

    out = {
        'security': [
            harness.build_basic_auth_entry(Security_Name, Username, Password),
        ],
        'groups': [
            harness.build_group_entry(Group_Name, [Security_Name]),
        ],
        'outconn_soap': [
            {
                'name': Connection_Name,
                'host': backend_address,
                'url_path': Backend_Path,
                'soap_action': SOAP_Action,
                'soap_version': '1.1',
                'timeout': 20,
            },
        ],
        'mcp_gateway': [gateway],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - the live SOAP test server as the ERP, a quickstart
    environment and one enmasse import that creates the connection and the gateway.
    """

    # The ERP comes up first ..
    soap_server = SOAPTestServer()
    soap_server.start()

    # .. the quickstart environment follows ..
    environment = harness.start_environment('mcp_connections_soap')

    try:
        # .. one import creates everything ..
        harness.run_enmasse_import(environment.server_directory, _build_enmasse_config(soap_server.address))

        # .. and the suite starts once the gateway lists the connection tool.
        mcp_url = environment.mcp_url(Gateway_Path)
        auth = (Username, Password)

        harness.wait_for_gateway_tool(mcp_url, auth, Tool_Name)

        yield {
            'environment': environment,
            'mcp_url': mcp_url,
            'auth': auth,
            'soap_server': soap_server,
        }

    finally:
        soap_server.stop()
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
