# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.ext.bunch import Bunch
from zato.server.connection.mcp.connection_tools.es import definition

# Zato - test helpers
from connection_stubs import get_tool_registry, make_gateway_wrapper, make_generic_item, make_mcp_handler, run_tools_call, \
    StubConfigManager, StubESClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _make_config_manager(client:'any_'=None) -> 'StubConfigManager':
    """ A config manager with one Elasticsearch connection called search.
    """

    es_wrapper = Bunch()
    es_wrapper.client = client

    out = StubConfigManager()
    out.outconn_es['search'] = make_generic_item(conn=es_wrapper, address_list='https://es.example.com:9200')

    return out

# ################################################################################################################################
# ################################################################################################################################

class ESToolShape(TestCase):
    """ Tests for the shape of Elasticsearch connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = _make_config_manager()
        wrapper = make_gateway_wrapper(config_manager, es_connections=['search'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'es.search')
        self.assertEqual(tool['description'], 'Invokes the Elasticsearch connection `search` (https://es.example.com:9200)')
        self.assertEqual(tool['inputSchema'], definition.input_schema)

        method_schema = definition.input_schema['properties']['method']
        self.assertEqual(method_schema['enum'], ['search', 'get', 'index', 'delete', 'count', 'exists'])
        self.assertEqual(definition.input_schema['required'], ['method', 'index_name'])

# ################################################################################################################################
# ################################################################################################################################

class ESToolInvoke(TestCase):
    """ Tests for invoking Elasticsearch connection tools.
    """

# ################################################################################################################################

    def test_invoke_calls_client_method(self) -> 'None':
        """ Verifies that the requested method runs against the index with the call's arguments
        and that the result's plain body travels back.
        """

        client = StubESClient({'search': {'hits': {'total': {'value': 1}}}})
        config_manager = _make_config_manager(client)
        wrapper = make_gateway_wrapper(config_manager, es_connections=['search'])

        arguments = {
            'method': 'search',
            'index_name': 'invoices',
            'arguments': {'query': {'match_all': {}}},
        }

        response = wrapper._invoke_service('es.search', arguments)

        self.assertEqual(response, {'hits': {'total': {'value': 1}}})

        method, kwargs = client.calls[0]
        self.assertEqual(method, 'search')
        self.assertEqual(kwargs, {'index': 'invoices', 'query': {'match_all': {}}})

# ################################################################################################################################

    def test_invoke_refuses_unknown_method(self) -> 'None':
        """ Verifies that a method outside the table is refused.
        """

        client = StubESClient({})
        config_manager = _make_config_manager(client)
        wrapper = make_gateway_wrapper(config_manager, es_connections=['search'])

        arguments = {
            'method': 'delete_by_query',
            'index_name': 'invoices',
        }

        with self.assertRaises(Exception) as ctx:
            _ = wrapper._invoke_service('es.search', arguments)

        self.assertIn('delete_by_query', str(ctx.exception))
        self.assertEqual(client.calls, [])

# ################################################################################################################################
# ################################################################################################################################

class ESToolsCall(TestCase):
    """ Tests for Elasticsearch tools through the full tools/call path.
    """

# ################################################################################################################################

    def test_tools_call_error_is_generic(self) -> 'None':
        """ Verifies that a refused method produces the generic refusal with isError true.
        """

        client = StubESClient({})
        config_manager = _make_config_manager(client)
        wrapper = make_gateway_wrapper(config_manager, es_connections=['search'])
        handler = make_mcp_handler(wrapper)

        mcp_response = run_tools_call(handler, 'es.search', {'method': 'delete_by_query', 'index_name': 'invoices'})

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])

        text = result['content'][0]['text']
        self.assertEqual(text, 'Bad request')

# ################################################################################################################################
# ################################################################################################################################
