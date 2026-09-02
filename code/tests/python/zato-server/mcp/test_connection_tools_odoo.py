# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.server.connection.mcp.connection_tools.odoo import definition

# Zato - test helpers
from connection_stubs import get_tool_registry, make_gateway_wrapper, make_mcp_handler, make_odoo_item, run_tools_call, \
    StubConfigManager, StubMethodClient, StubOdooClient, StubPooledWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _make_config_manager(wrapper:'any_'=None) -> 'StubConfigManager':
    """ A config manager with one Odoo connection called erp.
    """

    out = StubConfigManager()
    out.config_store.out_odoo['erp'] = make_odoo_item('odoo.example.com', 'production', 'jsonrpc', wrapper)

    return out

# ################################################################################################################################
# ################################################################################################################################

class OdooToolShape(TestCase):
    """ Tests for the shape of Odoo connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = _make_config_manager()
        wrapper = make_gateway_wrapper(config_manager, odoo_connections=['erp'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'odoo.erp')
        self.assertEqual(
            tool['description'],
            'Invokes the Odoo connection `erp` (jsonrpc at odoo.example.com, database production)')
        self.assertEqual(tool['inputSchema'], definition.input_schema)

        method_schema = definition.input_schema['properties']['method']
        self.assertEqual(method_schema['enum'], ['search', 'read', 'search_read', 'create', 'write'])
        self.assertEqual(definition.input_schema['required'], ['model', 'method'])

# ################################################################################################################################
# ################################################################################################################################

class OdooToolInvoke(TestCase):
    """ Tests for invoking Odoo connection tools.
    """

# ################################################################################################################################

    def test_invoke_calls_model_method(self) -> 'None':
        """ Verifies that the requested model method runs with the call's arguments.
        """

        model = StubMethodClient({'search_read': [{'id': 1, 'name': 'Partner'}]})
        client = StubOdooClient(model)
        odoo_wrapper = StubPooledWrapper(client)

        config_manager = _make_config_manager(odoo_wrapper)
        wrapper = make_gateway_wrapper(config_manager, odoo_connections=['erp'])

        arguments = {
            'model': 'res.partner',
            'method': 'search_read',
            'arguments': {'domain': [['is_company', '=', True]], 'fields': ['name']},
        }

        response = wrapper._invoke_service('odoo.erp', arguments)

        self.assertEqual(response, [{'id': 1, 'name': 'Partner'}])
        self.assertEqual(client.models_requested, ['res.partner'])

        method, _args, kwargs = model.calls[0]
        self.assertEqual(method, 'search_read')
        self.assertEqual(kwargs, {'domain': [['is_company', '=', True]], 'fields': ['name']})

# ################################################################################################################################

    def test_invoke_refuses_unknown_method(self) -> 'None':
        """ Verifies that a method outside the table is refused before a client is borrowed.
        """

        model = StubMethodClient({})
        client = StubOdooClient(model)
        odoo_wrapper = StubPooledWrapper(client)

        config_manager = _make_config_manager(odoo_wrapper)
        wrapper = make_gateway_wrapper(config_manager, odoo_connections=['erp'])

        arguments = {
            'model': 'res.partner',
            'method': 'unlink',
        }

        with self.assertRaises(Exception) as ctx:
            _ = wrapper._invoke_service('odoo.erp', arguments)

        self.assertIn('unlink', str(ctx.exception))
        self.assertEqual(client.models_requested, [])

# ################################################################################################################################
# ################################################################################################################################

class OdooToolsCall(TestCase):
    """ Tests for Odoo tools through the full tools/call path.
    """

# ################################################################################################################################

    def test_tools_call_error_is_generic(self) -> 'None':
        """ Verifies that a refused method produces the generic refusal with isError true.
        """

        model = StubMethodClient({})
        client = StubOdooClient(model)
        odoo_wrapper = StubPooledWrapper(client)

        config_manager = _make_config_manager(odoo_wrapper)
        wrapper = make_gateway_wrapper(config_manager, odoo_connections=['erp'])
        handler = make_mcp_handler(wrapper)

        mcp_response = run_tools_call(handler, 'odoo.erp', {'model': 'res.partner', 'method': 'unlink'})

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])

        text = result['content'][0]['text']
        self.assertEqual(text, 'Bad request')

# ################################################################################################################################
# ################################################################################################################################
