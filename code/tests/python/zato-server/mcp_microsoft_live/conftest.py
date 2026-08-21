# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# Where the shared harness, the simulated 365 tenant, the simulated Fabric tenant
# and the simulated Power Automate environment are imported from.
_this_directory = os.path.dirname(__file__)
_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))
_microsoft_365_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', 'microsoft_cloud_live'))
_fabric_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', 'fabric_live'))
_power_automate_lib_directory = os.path.abspath(os.path.join(_this_directory, '..', 'power_automate_live'))

sys.path.insert(0, _this_directory)
sys.path.insert(0, _lib_directory)

# The simulator directories go last - each has its own conftest.py
# and going first would shadow this suite's conftest.
sys.path.append(_microsoft_365_lib_directory)
sys.path.append(_fabric_lib_directory)
sys.path.append(_power_automate_lib_directory)

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
from _fabric_server import start_fabric_server  # noqa: E402
from _microsoft_365_server import Microsoft365TestHandler, start_microsoft_365_server  # noqa: E402
from _power_automate_server import start_power_automate_server  # noqa: E402

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

# What the suite's shared objects are called
Security_Name = 'test.mcp.connections.microsoft.auth'
Group_Name = 'mcp.test-connections-microsoft-group'

Username = 'test.mcp.connections.microsoft.user'
Password = 'test.mcp.connections.microsoft.password'

# The Microsoft 365 side - the simulated tenant of microsoft_cloud_live serves it.
Microsoft_365_Connection_Name = 'microsoft365.main'
Microsoft_365_Gateway_Name = 'test.mcp.connections.microsoft-365'
Microsoft_365_Gateway_Path = '/mcp/connections-microsoft-365'
Microsoft_365_Tool_Name = 'microsoft365.microsoft365_main'

# What the simulated tenant's directory users are called
Microsoft_365_User_Maria = 'Maria Garcia'
Microsoft_365_User_James = 'James Wilson'

# The Teams side - the same simulated tenant serves it.
Teams_Connection_Name = 'teams.main'
Teams_Gateway_Name = 'test.mcp.connections.microsoft-teams'
Teams_Gateway_Path = '/mcp/connections-microsoft-teams'
Teams_Tool_Name = 'teams.teams_main'

# The chat the Teams test sends to - any ID works, the simulated tenant records them all.
Teams_Chat_ID = 'chat-id-19-001'

# The Fabric side - the simulated tenant of fabric_live serves it.
Fabric_Connection_Name = 'fabric.lake'
Fabric_Gateway_Name = 'test.mcp.connections.fabric'
Fabric_Gateway_Path = '/mcp/connections-fabric'
Fabric_Tool_Name = 'fabric.fabric_lake'

# What the simulated tenant's initial workspaces are called
Fabric_Workspace_Sales = 'Sales analytics'
Fabric_Workspace_Finance = 'Finance'

# The Power Automate side - the simulated environment of power_automate_live serves it.
Power_Automate_Connection_Name = 'powerautomate.main'
Power_Automate_Gateway_Name = 'test.mcp.connections.power-automate'
Power_Automate_Gateway_Path = '/mcp/connections-power-automate'
Power_Automate_Tool_Name = 'powerautomate.powerautomate_main'

# What the simulated environment's initial flows are called
Power_Automate_Flow_Invoice = 'Invoice approval'
Power_Automate_Flow_Notifications = 'Customer notifications'

# ################################################################################################################################
# ################################################################################################################################

def _build_enmasse_config(
    microsoft_365_port:'int',
    fabric_port:'int',
    power_automate_port:'int',
    tenant_id:'str',
    client_id:'str',
    client_secret:'str',
    environment_id:'str',
) -> 'any_':
    """ The import document of the suite - the security definition, its group,
    one connection per Microsoft subtype against its simulated backend
    and one gateway per subtype exposing that connection.
    """

    microsoft_365_gateway = harness.build_gateway_entry(
        Microsoft_365_Gateway_Name, Microsoft_365_Gateway_Path, Group_Name,
        microsoft_365_connections=[Microsoft_365_Connection_Name])

    teams_gateway = harness.build_gateway_entry(
        Teams_Gateway_Name, Teams_Gateway_Path, Group_Name,
        microsoft_teams_connections=[Teams_Connection_Name])

    fabric_gateway = harness.build_gateway_entry(
        Fabric_Gateway_Name, Fabric_Gateway_Path, Group_Name,
        microsoft_fabric_connections=[Fabric_Connection_Name])

    power_automate_gateway = harness.build_gateway_entry(
        Power_Automate_Gateway_Name, Power_Automate_Gateway_Path, Group_Name,
        microsoft_power_automate_connections=[Power_Automate_Connection_Name])

    # Both 365-based connections point at the TLS tenant with certificate verification off.
    microsoft_365_address = f'https://127.0.0.1:{microsoft_365_port}'

    microsoft_365_connection = {
        'name': Microsoft_365_Connection_Name,
        'address': microsoft_365_address,
        'tenant_id': tenant_id,
        'client_id': client_id,
        'secret_value': client_secret,
        'auth_server_url': microsoft_365_address,
        'verify_tls': False,
    }

    teams_connection = {
        'name': Teams_Connection_Name,
        'address': microsoft_365_address,
        'tenant_id': tenant_id,
        'client_id': client_id,
        'secret_value': client_secret,
        'auth_server_url': microsoft_365_address,
        'verify_tls': False,
    }

    fabric_connection = {
        'name': Fabric_Connection_Name,
        'address': f'http://127.0.0.1:{fabric_port}',
        'tenant_id': tenant_id,
        'client_id': client_id,
        'client_secret': client_secret,
        'token_url': f'http://127.0.0.1:{fabric_port}/{tenant_id}/oauth2/v2.0/token',
        'onelake_address': f'http://127.0.0.1:{fabric_port}/onelake',
    }

    power_automate_connection = {
        'name': Power_Automate_Connection_Name,
        'address': f'http://127.0.0.1:{power_automate_port}',
        'tenant_id': tenant_id,
        'client_id': client_id,
        'client_secret': client_secret,
        'environment_id': environment_id,
        'token_url': f'http://127.0.0.1:{power_automate_port}/{tenant_id}/oauth2/v2.0/token',
    }

    out = {
        'security': [
            harness.build_basic_auth_entry(Security_Name, Username, Password),
        ],
        'groups': [
            harness.build_group_entry(Group_Name, [Security_Name]),
        ],
        'microsoft_cloud': [microsoft_365_connection],
        'microsoft_teams': [teams_connection],
        'microsoft_fabric': [fabric_connection],
        'microsoft_power_automate': [power_automate_connection],
        'mcp_gateway': [microsoft_365_gateway, teams_gateway, fabric_gateway, power_automate_gateway],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - the three simulated Microsoft backends, a quickstart
    environment and one enmasse import that creates the four connections
    and the four gateways exposing them.
    """

    # Every simulated backend accepts the same generated credentials of this run's own ..
    tenant_id = 'test-tenant-' + CryptoManager.generate_hex_string()
    client_id = 'test-client-' + CryptoManager.generate_hex_string()
    client_secret = 'test.secret.' + CryptoManager.generate_hex_string()

    # .. the 365 simulator also takes a short-lived client ID ..
    short_lived_client_id = 'test-client-short-' + CryptoManager.generate_hex_string()

    environment_id = 'test-environment'

    # .. the three simulated backends come up first, each on a free port of its own ..
    microsoft_365_port = harness.find_free_port()
    fabric_port = harness.find_free_port()
    power_automate_port = harness.find_free_port()

    microsoft_365_server, _ignored_thread = start_microsoft_365_server(
        microsoft_365_port, tenant_id, client_id, client_secret, short_lived_client_id)

    fabric_server, _ignored_thread = start_fabric_server(fabric_port, tenant_id, client_id, client_secret)

    power_automate_server, _ignored_thread = start_power_automate_server(
        power_automate_port, tenant_id, client_id, client_secret, environment_id)

    # .. the quickstart environment follows ..
    environment = harness.start_environment('mcp_connections_microsoft')

    try:
        # .. one import creates everything ..
        config = _build_enmasse_config(
            microsoft_365_port, fabric_port, power_automate_port,
            tenant_id, client_id, client_secret, environment_id)

        harness.run_enmasse_import(environment.server_directory, config)

        # .. and the suite starts once every gateway lists its connection tool.
        auth = (Username, Password)

        microsoft_365_mcp_url = environment.mcp_url(Microsoft_365_Gateway_Path)
        teams_mcp_url = environment.mcp_url(Teams_Gateway_Path)
        fabric_mcp_url = environment.mcp_url(Fabric_Gateway_Path)
        power_automate_mcp_url = environment.mcp_url(Power_Automate_Gateway_Path)

        harness.wait_for_gateway_tool(microsoft_365_mcp_url, auth, Microsoft_365_Tool_Name)
        harness.wait_for_gateway_tool(teams_mcp_url, auth, Teams_Tool_Name)
        harness.wait_for_gateway_tool(fabric_mcp_url, auth, Fabric_Tool_Name)
        harness.wait_for_gateway_tool(power_automate_mcp_url, auth, Power_Automate_Tool_Name)

        yield {
            'environment': environment,
            'auth': auth,
            'microsoft_365_mcp_url': microsoft_365_mcp_url,
            'teams_mcp_url': teams_mcp_url,
            'fabric_mcp_url': fabric_mcp_url,
            'power_automate_mcp_url': power_automate_mcp_url,
            'microsoft_365_handler': Microsoft365TestHandler,
        }

    finally:
        microsoft_365_server.shutdown()
        fabric_server.shutdown()
        power_automate_server.shutdown()
        harness.stop_environment(environment)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def ollama() -> 'any_':
    """ Session-scoped fixture that makes sure the Ollama container is running
    with the model pulled - only the tests that drive the model depend on it.
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
