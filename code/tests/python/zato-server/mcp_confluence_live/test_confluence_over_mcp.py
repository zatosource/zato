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
from conftest import Connection_Name, Gateway_Name, Space_Engineering, Space_Product, Tool_Name
from mcp_connections import harness

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class TestConfluenceToolDiscovery:
    """ The gateway lists the Confluence connection as a tool.
    """

# ################################################################################################################################

    def test_tool_listed(self, zato_server:'anydict') -> 'None':

        tool_names = harness.get_tool_names(zato_server['mcp_url'], zato_server['auth'])

        assert Tool_Name in tool_names, tool_names

# ################################################################################################################################
# ################################################################################################################################

class TestConfluenceEnmasseRoundTrip:
    """ The gateway's Confluence allow list survives an export and a reimport.
    """

# ################################################################################################################################

    def test_round_trip(self, zato_server:'anydict') -> 'None':

        environment = zato_server['environment']
        server_directory = environment.server_directory

        export_path = os.path.join(tempfile.gettempdir(), 'zato-mcp-connections-confluence-export.yaml')

        try:
            # The export brings the gateway back out with its allow list ..
            harness.run_enmasse_export(server_directory, export_path, 'mcp_gateway')

            with open(export_path) as export_file:
                exported = safe_load(export_file.read())

            gateway_by_name = {}

            for gateway in exported['mcp_gateway']:
                gateway_by_name[gateway['name']] = gateway

            gateway = gateway_by_name[Gateway_Name]
            assert gateway['confluence_connections'] == [Connection_Name], gateway

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

class TestConfluenceAgentEndToEnd:
    """ A real model discovers the Confluence tool through MCP and reads
    the simulated site's spaces with it.
    """

# ################################################################################################################################

    def test_agent_lists_spaces(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = MCPClient(zato_server['mcp_url'], auth=zato_server['auth'])

        task = (
            'List the spaces of the Confluence site through the Confluence tool - '
            'the method is get_all_spaces and it needs no arguments - '
            'and tell me the names of every space you find.')

        result = run_agent(client, task)

        # The model called the Confluence tool ..
        called_tools = []

        for call in result.tool_calls:
            called_tools.append(call.tool_name)

        assert Tool_Name in called_tools, result.messages

        # .. and both of the site's spaces made it into the final answer.
        assert Space_Engineering in result.final_text, result.final_text
        assert Space_Product in result.final_text, result.final_text

# ################################################################################################################################
# ################################################################################################################################
