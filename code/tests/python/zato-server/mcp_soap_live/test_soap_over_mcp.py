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
from conftest import Connection_Name, Gateway_Name, Tool_Name
from mcp_connections import harness

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPToolDiscovery:
    """ The gateway lists the SOAP connection as a tool.
    """

# ################################################################################################################################

    def test_tool_listed(self, zato_server:'anydict') -> 'None':

        tool_names = harness.get_tool_names(zato_server['mcp_url'], zato_server['auth'])

        assert Tool_Name in tool_names, tool_names

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPEnmasseRoundTrip:
    """ The gateway's SOAP allow list survives an export and a reimport.
    """

# ################################################################################################################################

    def test_round_trip(self, zato_server:'anydict') -> 'None':

        environment = zato_server['environment']
        server_directory = environment.server_directory

        export_path = os.path.join(tempfile.gettempdir(), 'zato-mcp-connections-soap-export.yaml')

        try:
            # The export brings the gateway back out with its allow list ..
            harness.run_enmasse_export(server_directory, export_path, 'mcp_gateway')

            with open(export_path) as export_file:
                exported = safe_load(export_file.read())

            gateway_by_name = {}

            for gateway in exported['mcp_gateway']:
                gateway_by_name[gateway['name']] = gateway

            gateway = gateway_by_name[Gateway_Name]
            assert gateway['soap_connections'] == [Connection_Name], gateway

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

class TestSOAPAgentEndToEnd:
    """ A real model discovers the SOAP tool through MCP and calls it.
    """

# ################################################################################################################################

    def test_agent_calls_tool(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = MCPClient(zato_server['mcp_url'], auth=zato_server['auth'])

        soap_server = zato_server['soap_server']
        requests_before = len(soap_server.recorded_requests)

        task = (
            'Create an invoice header for customer CUST-0001 through the ERP invoicing tool - '
            'the operation is CreateInvoiceHeader and the message carries one field, '
            'customerNo, set to CUST-0001. Then tell me what the ERP answered.')

        result = run_agent(client, task)

        # The model called the SOAP tool ..
        called_tools = []

        for call in result.tool_calls:
            called_tools.append(call.tool_name)

        assert Tool_Name in called_tools, result.messages

        # .. the ERP really was hit ..
        assert len(soap_server.recorded_requests) > requests_before, soap_server.recorded_requests

        # .. and the ERP's ok status came back through a successful tool call.
        successful_calls = []

        for call in result.tool_calls:
            if call.tool_name == Tool_Name and not call.is_error:
                successful_calls.append(call)

        assert successful_calls, result.tool_calls
        assert 'ok' in successful_calls[0].result_text, successful_calls[0].result_text

# ################################################################################################################################
# ################################################################################################################################
