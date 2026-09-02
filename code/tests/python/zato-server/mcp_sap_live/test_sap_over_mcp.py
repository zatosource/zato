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
from conftest import Connection_Name, Entity_Set, Gateway_Name, Sold_To_Party_First, Sold_To_Party_Second, Tool_Name
from mcp_connections import harness

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class TestSAPToolDiscovery:
    """ The gateway lists the SAP connection as a tool.
    """

# ################################################################################################################################

    def test_tool_listed(self, zato_server:'anydict') -> 'None':

        tool_names = harness.get_tool_names(zato_server['mcp_url'], zato_server['auth'])

        assert Tool_Name in tool_names, tool_names

# ################################################################################################################################
# ################################################################################################################################

class TestSAPEnmasseRoundTrip:
    """ The gateway's SAP allow list survives an export and a reimport.
    """

# ################################################################################################################################

    def test_round_trip(self, zato_server:'anydict') -> 'None':

        environment = zato_server['environment']
        server_directory = environment.server_directory

        export_path = os.path.join(tempfile.gettempdir(), 'zato-mcp-connections-sap-export.yaml')

        try:
            # The export brings the gateway back out with its allow list ..
            harness.run_enmasse_export(server_directory, export_path, 'mcp_gateway')

            with open(export_path) as export_file:
                exported = safe_load(export_file.read())

            gateway_by_name = {}

            for gateway in exported['mcp_gateway']:
                gateway_by_name[gateway['name']] = gateway

            gateway = gateway_by_name[Gateway_Name]
            assert gateway['sap_connections'] == [Connection_Name], gateway

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

class TestSAPAgentEndToEnd:
    """ A real model discovers the SAP tool through MCP and reads
    the simulated S/4HANA system's sales orders with it.
    """

# ################################################################################################################################

    def test_agent_reads_sales_orders(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = MCPClient(zato_server['mcp_url'], auth=zato_server['auth'])

        task = (
            f'Read the sales orders of the SAP system through the SAP tool - '
            f'the operation is read and the entity_set is {Entity_Set}, no other arguments - '
            f'and tell me the sold-to party of every order you find.')

        result = run_agent(client, task)

        # The model called the SAP tool ..
        called_tools = []

        for call in result.tool_calls:
            called_tools.append(call.tool_name)

        assert Tool_Name in called_tools, result.messages

        # .. and both of the seeded orders' parties made it into the final answer -
        # a model may render a hyphen as its non-breaking variant, so the answer
        # is normalized back to the ASCII form first.
        final_text = result.final_text.replace('\u2011', '-')

        assert Sold_To_Party_First in final_text, result.final_text
        assert Sold_To_Party_Second in final_text, result.final_text

# ################################################################################################################################
# ################################################################################################################################
