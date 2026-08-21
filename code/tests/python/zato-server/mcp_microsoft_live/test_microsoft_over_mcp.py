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
from conftest import Fabric_Connection_Name, Fabric_Gateway_Name, Fabric_Tool_Name, Fabric_Workspace_Finance, \
    Fabric_Workspace_Sales, Microsoft_365_Connection_Name, Microsoft_365_Gateway_Name, Microsoft_365_Tool_Name, \
    Microsoft_365_User_James, Microsoft_365_User_Maria, Power_Automate_Connection_Name, Power_Automate_Flow_Invoice, \
    Power_Automate_Gateway_Name, Power_Automate_Tool_Name, Teams_Chat_ID, Teams_Connection_Name, Teams_Gateway_Name, \
    Teams_Tool_Name
from mcp_connections import harness

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class TestMicrosoftToolDiscovery:
    """ Each of the four gateways lists its Microsoft connection as a tool.
    """

# ################################################################################################################################

    def test_microsoft_365_tool_listed(self, zato_server:'anydict') -> 'None':

        tool_names = harness.get_tool_names(zato_server['microsoft_365_mcp_url'], zato_server['auth'])

        assert Microsoft_365_Tool_Name in tool_names, tool_names

# ################################################################################################################################

    def test_teams_tool_listed(self, zato_server:'anydict') -> 'None':

        tool_names = harness.get_tool_names(zato_server['teams_mcp_url'], zato_server['auth'])

        assert Teams_Tool_Name in tool_names, tool_names

# ################################################################################################################################

    def test_fabric_tool_listed(self, zato_server:'anydict') -> 'None':

        tool_names = harness.get_tool_names(zato_server['fabric_mcp_url'], zato_server['auth'])

        assert Fabric_Tool_Name in tool_names, tool_names

# ################################################################################################################################

    def test_power_automate_tool_listed(self, zato_server:'anydict') -> 'None':

        tool_names = harness.get_tool_names(zato_server['power_automate_mcp_url'], zato_server['auth'])

        assert Power_Automate_Tool_Name in tool_names, tool_names

# ################################################################################################################################
# ################################################################################################################################

class TestMicrosoftEnmasseRoundTrip:
    """ The four gateways' Microsoft allow lists survive an export and a reimport.
    """

# ################################################################################################################################

    def test_round_trip(self, zato_server:'anydict') -> 'None':

        environment = zato_server['environment']
        server_directory = environment.server_directory

        export_path = os.path.join(tempfile.gettempdir(), 'zato-mcp-connections-microsoft-export.yaml')

        try:
            # The export brings the gateways back out with their allow lists ..
            harness.run_enmasse_export(server_directory, export_path, 'mcp_gateway')

            with open(export_path) as export_file:
                exported = safe_load(export_file.read())

            gateway_by_name = {}

            for gateway in exported['mcp_gateway']:
                gateway_by_name[gateway['name']] = gateway

            microsoft_365_gateway = gateway_by_name[Microsoft_365_Gateway_Name]
            assert microsoft_365_gateway['microsoft_365_connections'] == [Microsoft_365_Connection_Name], microsoft_365_gateway

            teams_gateway = gateway_by_name[Teams_Gateway_Name]
            assert teams_gateway['microsoft_teams_connections'] == [Teams_Connection_Name], teams_gateway

            fabric_gateway = gateway_by_name[Fabric_Gateway_Name]
            assert fabric_gateway['microsoft_fabric_connections'] == [Fabric_Connection_Name], fabric_gateway

            power_automate_gateway = gateway_by_name[Power_Automate_Gateway_Name]
            expected_connections = [Power_Automate_Connection_Name]
            assert power_automate_gateway['microsoft_power_automate_connections'] == expected_connections, power_automate_gateway

            # .. the export is a clean input of its own ..
            harness.run_enmasse_import(server_directory, exported)

            # .. and every gateway still lists its tool afterwards.
            tool_names = harness.get_tool_names(zato_server['microsoft_365_mcp_url'], zato_server['auth'])
            assert Microsoft_365_Tool_Name in tool_names, tool_names

            tool_names = harness.get_tool_names(zato_server['teams_mcp_url'], zato_server['auth'])
            assert Teams_Tool_Name in tool_names, tool_names

            tool_names = harness.get_tool_names(zato_server['fabric_mcp_url'], zato_server['auth'])
            assert Fabric_Tool_Name in tool_names, tool_names

            tool_names = harness.get_tool_names(zato_server['power_automate_mcp_url'], zato_server['auth'])
            assert Power_Automate_Tool_Name in tool_names, tool_names

        finally:
            if os.path.isfile(export_path):
                os.remove(export_path)

# ################################################################################################################################
# ################################################################################################################################

class TestMicrosoft365AgentEndToEnd:
    """ A real model discovers the Microsoft 365 tool through MCP and reads
    the simulated tenant's directory with it.
    """

# ################################################################################################################################

    def test_agent_lists_users(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = MCPClient(zato_server['microsoft_365_mcp_url'], auth=zato_server['auth'])

        task = (
            'List the users of the Microsoft 365 tenant through the Microsoft 365 tool - '
            'the operation is list_users and it needs no arguments - '
            'and tell me the display names of every user you find.')

        result = run_agent(client, task)

        # The model called the 365 tool ..
        called_tools = []

        for call in result.tool_calls:
            called_tools.append(call.tool_name)

        assert Microsoft_365_Tool_Name in called_tools, result.messages

        # .. and both of the tenant's users made it into the final answer.
        assert Microsoft_365_User_Maria in result.final_text, result.final_text
        assert Microsoft_365_User_James in result.final_text, result.final_text

# ################################################################################################################################
# ################################################################################################################################

class TestTeamsAgentEndToEnd:
    """ A real model discovers the Teams tool through MCP and sends
    a chat message through the simulated tenant with it.
    """

# ################################################################################################################################

    def test_agent_sends_message(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = MCPClient(zato_server['teams_mcp_url'], auth=zato_server['auth'])

        handler = zato_server['microsoft_365_handler']
        messages_before = len(handler.chat_messages)

        message_text = 'The invoices for July are ready for review'

        task = (
            f'Send a Microsoft Teams message through the Teams tool - '
            f'the to argument is the chat ID {Teams_Chat_ID} and the text argument is '
            f'"{message_text}" - and confirm once it is sent.')

        result = run_agent(client, task)

        # The model called the Teams tool ..
        called_tools = []

        for call in result.tool_calls:
            called_tools.append(call.tool_name)

        assert Teams_Tool_Name in called_tools, result.messages

        # .. and the simulated tenant really received the chat message.
        assert len(handler.chat_messages) > messages_before, handler.chat_messages

        message = handler.chat_messages[-1]
        assert message['chat_id'] == Teams_Chat_ID, message

        message_payload = message['payload']
        message_body = message_payload['body']
        assert message_text in message_body['content'], message

# ################################################################################################################################
# ################################################################################################################################

class TestFabricAgentEndToEnd:
    """ A real model discovers the Fabric tool through MCP and reads
    the simulated tenant's workspaces with it.
    """

# ################################################################################################################################

    def test_agent_lists_workspaces(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = MCPClient(zato_server['fabric_mcp_url'], auth=zato_server['auth'])

        task = (
            'List the Microsoft Fabric workspaces through the fabric tool - '
            'the method is list_workspaces and it needs no arguments - '
            'and tell me the display names of every workspace you find.')

        result = run_agent(client, task)

        # The model called the Fabric tool ..
        called_tools = []

        for call in result.tool_calls:
            called_tools.append(call.tool_name)

        assert Fabric_Tool_Name in called_tools, result.messages

        # .. and both of the tenant's workspaces made it into the final answer.
        assert Fabric_Workspace_Sales in result.final_text, result.final_text
        assert Fabric_Workspace_Finance in result.final_text, result.final_text

# ################################################################################################################################
# ################################################################################################################################

class TestPowerAutomateAgentEndToEnd:
    """ A real model discovers the Power Automate tool through MCP and reads
    the simulated environment's flows with it.
    """

# ################################################################################################################################

    def test_agent_lists_flows(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = MCPClient(zato_server['power_automate_mcp_url'], auth=zato_server['auth'])

        task = (
            'List the Power Automate flows through the Power Automate tool - '
            'the method is list_flows and it needs no arguments - '
            'and tell me the display names of every flow you find.')

        result = run_agent(client, task)

        # The model called the Power Automate tool ..
        called_tools = []

        for call in result.tool_calls:
            called_tools.append(call.tool_name)

        assert Power_Automate_Tool_Name in called_tools, result.messages

        # .. and the environment's first flow made it into the final answer.
        assert Power_Automate_Flow_Invoice in result.final_text, result.final_text

# ################################################################################################################################
# ################################################################################################################################
