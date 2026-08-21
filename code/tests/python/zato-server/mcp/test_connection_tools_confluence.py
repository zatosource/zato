# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.server.connection.mcp.connection_tools.confluence import definition

# Zato - test helpers
from connection_stubs import get_tool_registry, make_gateway_wrapper, make_generic_item, make_mcp_handler, run_tools_call, \
    StubConfigManager, StubMethodClient, StubPooledWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _make_config_manager(client:'any_'=None) -> 'StubConfigManager':
    """ A config manager with one Confluence connection called wiki.
    """

    confluence_wrapper = StubPooledWrapper(client)

    out = StubConfigManager()
    out.cloud_confluence['wiki'] = make_generic_item(conn=confluence_wrapper, address='https://example.atlassian.net')

    return out

# ################################################################################################################################
# ################################################################################################################################

class ConfluenceToolShape(TestCase):
    """ Tests for the shape of Confluence connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = _make_config_manager()
        wrapper = make_gateway_wrapper(config_manager, confluence_connections=['wiki'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'confluence.wiki')
        self.assertEqual(tool['description'], 'Invokes the Confluence connection `wiki` (https://example.atlassian.net)')
        self.assertEqual(tool['inputSchema'], definition.input_schema)

        method_schema = definition.input_schema['properties']['method']
        self.assertEqual(
            method_schema['enum'],
            ['get_page_by_id', 'get_page_by_title', 'create_page', 'update_page', 'cql', 'get_all_spaces'])
        self.assertEqual(definition.input_schema['required'], ['method'])

# ################################################################################################################################
# ################################################################################################################################

class ConfluenceToolInvoke(TestCase):
    """ Tests for invoking Confluence connection tools.
    """

# ################################################################################################################################

    def test_invoke_calls_client_method(self) -> 'None':
        """ Verifies that the requested method runs on a pooled client with the call's arguments.
        """

        client = StubMethodClient({'get_page_by_id': {'id': '12345', 'title': 'Runbook'}})
        config_manager = _make_config_manager(client)
        wrapper = make_gateway_wrapper(config_manager, confluence_connections=['wiki'])

        arguments = {
            'method': 'get_page_by_id',
            'arguments': {'page_id': '12345'},
        }

        response = wrapper._invoke_service('confluence.wiki', arguments)

        self.assertEqual(response, {'id': '12345', 'title': 'Runbook'})

        method, _args, kwargs = client.calls[0]
        self.assertEqual(method, 'get_page_by_id')
        self.assertEqual(kwargs, {'page_id': '12345'})

# ################################################################################################################################

    def test_invoke_refuses_unknown_method(self) -> 'None':
        """ Verifies that a method outside the table is refused before a client is borrowed.
        """

        client = StubMethodClient({})
        config_manager = _make_config_manager(client)
        wrapper = make_gateway_wrapper(config_manager, confluence_connections=['wiki'])

        with self.assertRaises(Exception) as ctx:
            _ = wrapper._invoke_service('confluence.wiki', {'method': 'remove_page'})

        self.assertIn('remove_page', str(ctx.exception))
        self.assertEqual(client.calls, [])

# ################################################################################################################################
# ################################################################################################################################

class ConfluenceToolsCall(TestCase):
    """ Tests for Confluence tools through the full tools/call path.
    """

# ################################################################################################################################

    def test_tools_call_error_is_generic(self) -> 'None':
        """ Verifies that a refused method produces the generic refusal with isError true.
        """

        client = StubMethodClient({})
        config_manager = _make_config_manager(client)
        wrapper = make_gateway_wrapper(config_manager, confluence_connections=['wiki'])
        handler = make_mcp_handler(wrapper)

        mcp_response = run_tools_call(handler, 'confluence.wiki', {'method': 'remove_page'})

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])

        text = result['content'][0]['text']
        self.assertEqual(text, 'Bad request')

# ################################################################################################################################
# ################################################################################################################################
