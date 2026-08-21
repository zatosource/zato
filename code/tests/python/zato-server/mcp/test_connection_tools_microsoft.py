# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.ext.bunch import Bunch
from zato.server.connection.mcp.connection_tools.microsoft import fabric_spec, microsoft_365_spec, \
    power_automate_spec, teams_spec

# Zato - test helpers
from connection_stubs import get_tool_registry, make_gateway_wrapper, make_generic_item, make_mcp_handler, run_tools_call, \
    StubConfigManager, StubMethodClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _make_shared_client_item(client:'any_') -> 'Bunch':
    """ One generic connection whose wrapper holds a shared client,
    the way the Microsoft wrappers hold theirs.
    """

    conn = Bunch()
    conn.shared_client = client

    out = make_generic_item(conn=conn)
    return out

# ################################################################################################################################
# ################################################################################################################################

class _StubMailMessage:
    """ One outgoing mail message under construction - records what the tool sets on it.
    """

    def __init__(self) -> 'None':
        self.to = _StubRecipients()
        self.subject = ''
        self.body = ''
        self.was_sent = False

    def send(self) -> 'bool':
        self.was_sent = True
        return True

# ################################################################################################################################

class _StubRecipients:
    """ The recipients of a stub mail message.
    """

    def __init__(self) -> 'None':
        self.addresses:'list[str]' = []

    def add(self, address:'str') -> 'None':
        self.addresses.append(address)

# ################################################################################################################################

class _StubMailbox:
    """ One user's mailbox - the message it news up is kept for assertions.
    """

    def __init__(self) -> 'None':
        self.message = _StubMailMessage()

    def new_message(self) -> '_StubMailMessage':
        out = self.message
        return out

# ################################################################################################################################

class _Stub365Client:
    """ Stands in for the Microsoft 365 client - the account surface the tool reaches into.
    """

    def __init__(self) -> 'None':
        self.mailbox_resources:'list[str]' = []
        self.mailbox_stub = _StubMailbox()

    def mailbox(self, resource:'str') -> '_StubMailbox':
        self.mailbox_resources.append(resource)

        out = self.mailbox_stub
        return out

# ################################################################################################################################

class _StubTeamsClient:
    """ Stands in for the Teams client - records every message sent.
    """

    def __init__(self) -> 'None':
        self.sent:'list[tuple]' = []

    def send(self, to:'str', text:'str') -> 'any_':
        self.sent.append((to, text))

        out = {'is_sent': True}
        return out

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365Tool(TestCase):
    """ Tests for Microsoft 365 connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_365['main'] = _make_shared_client_item(None)

        wrapper = make_gateway_wrapper(config_manager, microsoft_365_connections=['main'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'microsoft365.main')
        self.assertEqual(
            tool['description'],
            'Invokes the Microsoft 365 connection `main` - mail, calendar and directory operations')
        self.assertEqual(tool['inputSchema'], microsoft_365_spec.input_schema)

        operation_schema = microsoft_365_spec.input_schema['properties']['operation']
        self.assertEqual(operation_schema['enum'], ['send_mail', 'list_messages', 'list_calendar_events', 'list_users'])

# ################################################################################################################################

    def test_invoke_send_mail(self) -> 'None':
        """ Verifies that send_mail builds and sends one message through the user's mailbox.
        """

        client = _Stub365Client()

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_365['main'] = _make_shared_client_item(client)

        wrapper = make_gateway_wrapper(config_manager, microsoft_365_connections=['main'])

        arguments = {
            'operation': 'send_mail',
            'arguments': {
                'user': 'sender@example.com',
                'to': 'recipient@example.com',
                'subject': 'Hello',
                'body': 'Hello from the test',
            },
        }

        response = wrapper._invoke_service('microsoft365.main', arguments)

        self.assertEqual(response, {'is_sent': True})
        self.assertEqual(client.mailbox_resources, ['sender@example.com'])

        message = client.mailbox_stub.message
        self.assertTrue(message.was_sent)
        self.assertEqual(message.to.addresses, ['recipient@example.com'])
        self.assertEqual(message.subject, 'Hello')
        self.assertEqual(message.body, 'Hello from the test')

# ################################################################################################################################

    def test_invoke_refuses_unknown_operation(self) -> 'None':
        """ Verifies that an operation outside the table is refused.
        """

        client = _Stub365Client()

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_365['main'] = _make_shared_client_item(client)

        wrapper = make_gateway_wrapper(config_manager, microsoft_365_connections=['main'])

        with self.assertRaises(Exception) as ctx:
            _ = wrapper._invoke_service('microsoft365.main', {'operation': 'delete_mailbox'})

        self.assertIn('delete_mailbox', str(ctx.exception))
        self.assertEqual(client.mailbox_resources, [])

# ################################################################################################################################
# ################################################################################################################################

class TeamsTool(TestCase):
    """ Tests for Microsoft Teams connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = StubConfigManager()
        config_manager.chat_microsoft_teams['chat'] = _make_shared_client_item(None)

        wrapper = make_gateway_wrapper(config_manager, microsoft_teams_connections=['chat'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'teams.chat')
        self.assertEqual(tool['description'], 'Sends a message through the Microsoft Teams connection `chat`')
        self.assertEqual(tool['inputSchema'], teams_spec.input_schema)
        self.assertEqual(teams_spec.input_schema['required'], ['to', 'text'])

# ################################################################################################################################

    def test_invoke_sends_message(self) -> 'None':
        """ Verifies that the shared client sends what the tool call carried.
        """

        client = _StubTeamsClient()

        config_manager = StubConfigManager()
        config_manager.chat_microsoft_teams['chat'] = _make_shared_client_item(client)

        wrapper = make_gateway_wrapper(config_manager, microsoft_teams_connections=['chat'])

        response = wrapper._invoke_service('teams.chat', {'to': 'My Team/General', 'text': '<b>Hello</b>'})

        self.assertEqual(response, {'is_sent': True})
        self.assertEqual(client.sent, [('My Team/General', '<b>Hello</b>')])

# ################################################################################################################################
# ################################################################################################################################

class FabricTool(TestCase):
    """ Tests for Microsoft Fabric connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_fabric['lake'] = _make_shared_client_item(None)

        wrapper = make_gateway_wrapper(config_manager, microsoft_fabric_connections=['lake'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'fabric.lake')
        self.assertEqual(
            tool['description'],
            'Invokes the Microsoft Fabric connection `lake` - workspaces, items, jobs and OneLake')
        self.assertEqual(tool['inputSchema'], fabric_spec.input_schema)

        method_schema = fabric_spec.input_schema['properties']['method']
        self.assertIn('list_workspaces', method_schema['enum'])
        self.assertIn('onelake_read', method_schema['enum'])

# ################################################################################################################################

    def test_invoke_calls_client_method(self) -> 'None':
        """ Verifies that the requested method runs on the shared client with the call's arguments.
        """

        client = StubMethodClient({'list_items': [{'id': 'item-1'}]})

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_fabric['lake'] = _make_shared_client_item(client)

        wrapper = make_gateway_wrapper(config_manager, microsoft_fabric_connections=['lake'])

        arguments = {
            'method': 'list_items',
            'arguments': {'workspace_id': 'ws-1'},
        }

        response = wrapper._invoke_service('fabric.lake', arguments)

        self.assertEqual(response, [{'id': 'item-1'}])

        method, _args, kwargs = client.calls[0]
        self.assertEqual(method, 'list_items')
        self.assertEqual(kwargs, {'workspace_id': 'ws-1'})

# ################################################################################################################################

    def test_invoke_decodes_bytes(self) -> 'None':
        """ Verifies that a OneLake read returning bytes travels back as text.
        """

        client = StubMethodClient({'onelake_read': b'file contents'})

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_fabric['lake'] = _make_shared_client_item(client)

        wrapper = make_gateway_wrapper(config_manager, microsoft_fabric_connections=['lake'])

        arguments = {
            'method': 'onelake_read',
            'arguments': {'workspace_id': 'ws-1', 'item_id': 'item-1', 'file_path': 'Files/data.txt'},
        }

        response = wrapper._invoke_service('fabric.lake', arguments)

        self.assertEqual(response, 'file contents')

# ################################################################################################################################

    def test_invoke_refuses_unknown_method(self) -> 'None':
        """ Verifies that a method outside the table is refused.
        """

        client = StubMethodClient({})

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_fabric['lake'] = _make_shared_client_item(client)

        wrapper = make_gateway_wrapper(config_manager, microsoft_fabric_connections=['lake'])

        with self.assertRaises(Exception) as ctx:
            _ = wrapper._invoke_service('fabric.lake', {'method': 'drop_lakehouse'})

        self.assertIn('drop_lakehouse', str(ctx.exception))
        self.assertEqual(client.calls, [])

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTool(TestCase):
    """ Tests for Microsoft Power Automate connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_power_automate['flows'] = _make_shared_client_item(None)

        wrapper = make_gateway_wrapper(config_manager, microsoft_power_automate_connections=['flows'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'powerautomate.flows')
        self.assertEqual(
            tool['description'],
            'Invokes the Microsoft Power Automate connection `flows` - flows, runs and triggers')
        self.assertEqual(tool['inputSchema'], power_automate_spec.input_schema)

        method_schema = power_automate_spec.input_schema['properties']['method']
        self.assertEqual(method_schema['enum'], ['list_flows', 'get_flow', 'enable_flow', 'list_runs', 'resubmit_run', 'trigger'])

# ################################################################################################################################

    def test_invoke_calls_client_method(self) -> 'None':
        """ Verifies that the requested method runs on the shared client with the call's arguments.
        """

        client = StubMethodClient({'trigger': {'status': 'started'}})

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_power_automate['flows'] = _make_shared_client_item(client)

        wrapper = make_gateway_wrapper(config_manager, microsoft_power_automate_connections=['flows'])

        arguments = {
            'method': 'trigger',
            'arguments': {'flow_id': 'flow-1', 'payload': {'key': 'value'}},
        }

        response = wrapper._invoke_service('powerautomate.flows', arguments)

        self.assertEqual(response, {'status': 'started'})

        method, _args, kwargs = client.calls[0]
        self.assertEqual(method, 'trigger')
        self.assertEqual(kwargs, {'flow_id': 'flow-1', 'payload': {'key': 'value'}})

# ################################################################################################################################

    def test_invoke_refuses_unknown_method(self) -> 'None':
        """ Verifies that a method outside the table is refused.
        """

        client = StubMethodClient({})

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_power_automate['flows'] = _make_shared_client_item(client)

        wrapper = make_gateway_wrapper(config_manager, microsoft_power_automate_connections=['flows'])

        with self.assertRaises(Exception) as ctx:
            _ = wrapper._invoke_service('powerautomate.flows', {'method': 'delete_flow'})

        self.assertIn('delete_flow', str(ctx.exception))
        self.assertEqual(client.calls, [])

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftToolsCall(TestCase):
    """ Tests for the Microsoft tools through the full tools/call path.
    """

# ################################################################################################################################

    def test_tools_call_error_is_generic(self) -> 'None':
        """ Verifies that a refused operation produces the generic refusal with isError true.
        """

        client = _Stub365Client()

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_365['main'] = _make_shared_client_item(client)

        wrapper = make_gateway_wrapper(config_manager, microsoft_365_connections=['main'])
        handler = make_mcp_handler(wrapper)

        mcp_response = run_tools_call(handler, 'microsoft365.main', {'operation': 'delete_mailbox'})

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])

        text = result['content'][0]['text']
        self.assertEqual(text, 'Bad request')

# ################################################################################################################################

    def test_all_four_groups_on_one_gateway(self) -> 'None':
        """ Verifies that one gateway lists the tools of all four Microsoft groups side by side.
        """

        config_manager = StubConfigManager()
        config_manager.cloud_microsoft_365['main'] = _make_shared_client_item(None)
        config_manager.chat_microsoft_teams['chat'] = _make_shared_client_item(None)
        config_manager.cloud_microsoft_fabric['lake'] = _make_shared_client_item(None)
        config_manager.cloud_microsoft_power_automate['flows'] = _make_shared_client_item(None)

        wrapper = make_gateway_wrapper(
            config_manager,
            microsoft_365_connections=['main'],
            microsoft_teams_connections=['chat'],
            microsoft_fabric_connections=['lake'],
            microsoft_power_automate_connections=['flows'],
        )

        names = []

        tool_registry = get_tool_registry(wrapper)

        for tool in tool_registry.get_tools():
            names.append(tool['name'])

        self.assertEqual(names, ['fabric.lake', 'microsoft365.main', 'powerautomate.flows', 'teams.chat'])

# ################################################################################################################################
# ################################################################################################################################
