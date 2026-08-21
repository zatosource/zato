# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile

# PyYAML
from yaml import safe_load

# Zato - test helpers
from _agent import run_agent
from _client import MCPClient
from conftest import Backend_Balance, Connection_Name, Gateway_Name, Tool_Name
from mcp_connections import harness

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class TestRESTToolDiscovery:
    """ The gateway lists the REST connection as a tool.
    """

# ################################################################################################################################

    def test_tool_listed(self, zato_server:'anydict') -> 'None':

        tool_names = harness.get_tool_names(zato_server['mcp_url'], zato_server['auth'])

        assert Tool_Name in tool_names, tool_names

# ################################################################################################################################
# ################################################################################################################################

class TestRESTEnmasseRoundTrip:
    """ The gateway's REST allow list survives an export and a reimport.
    """

# ################################################################################################################################

    def test_round_trip(self, zato_server:'anydict') -> 'None':

        environment = zato_server['environment']
        server_directory = environment.server_directory

        export_path = os.path.join(tempfile.gettempdir(), 'zato-mcp-connections-rest-export.yaml')

        try:
            # The export brings the gateway back out with its allow list ..
            harness.run_enmasse_export(server_directory, export_path, 'mcp_gateway')

            with open(export_path) as export_file:
                exported = safe_load(export_file.read())

            gateway_by_name = {}

            for gateway in exported['mcp_gateway']:
                gateway_by_name[gateway['name']] = gateway

            gateway = gateway_by_name[Gateway_Name]
            assert gateway['rest_connections'] == [Connection_Name], gateway

            # .. the export is a clean input of its own ..
            harness.run_enmasse_import(server_directory, exported)

            # .. and the gateway still lists the tool afterwards.
            tool_names = harness.get_tool_names(zato_server['mcp_url'], zato_server['auth'])
            assert Tool_Name in tool_names, tool_names

        finally:
            if os.path.isfile(export_path):
                os.remove(export_path)

# ################################################################################################################################
# ################################################################################################################################

class TestRESTAgentEndToEnd:
    """ A real model discovers the REST tool through MCP and calls it.
    """

# ################################################################################################################################

    def test_agent_calls_tool(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = MCPClient(zato_server['mcp_url'], auth=zato_server['auth'])

        backend_state = zato_server['backend_state']
        requests_before = len(backend_state.requests)

        task = (
            'Check the current balance of customer 123 through the billing backend tool, '
            'using the GET method, and tell me the number.')

        result = run_agent(client, task)

        # The model called the REST tool ..
        called_tools = []

        for call in result.tool_calls:
            called_tools.append(call.tool_name)

        assert Tool_Name in called_tools, result.messages

        # .. the backend really was hit ..
        assert len(backend_state.requests) > requests_before, backend_state.requests

        # .. and the balance made it into the model's final answer.
        assert str(Backend_Balance) in result.final_text, result.final_text

# ################################################################################################################################
# ################################################################################################################################
