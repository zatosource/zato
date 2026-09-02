# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.server.connection.mcp.connection_tools.sap import definition

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
    """ A config manager with one SAP connection called erp.
    """

    sap_wrapper = StubPooledWrapper(client)

    out = StubConfigManager()
    out.outconn_sap['erp'] = make_generic_item(conn=sap_wrapper, address='https://sap.example.com/odata')

    return out

# ################################################################################################################################
# ################################################################################################################################

class SAPToolShape(TestCase):
    """ Tests for the shape of SAP connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = _make_config_manager()
        wrapper = make_gateway_wrapper(config_manager, sap_connections=['erp'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'sap.erp')
        self.assertEqual(tool['description'], 'Invokes the SAP connection `erp` (https://sap.example.com/odata) through OData')
        self.assertEqual(tool['inputSchema'], definition.input_schema)

        operation_schema = definition.input_schema['properties']['operation']
        self.assertEqual(
            operation_schema['enum'],
            ['read', 'get', 'create', 'update', 'delete', 'call_function', 'call_action', 'count'])
        self.assertEqual(definition.input_schema['required'], ['operation', 'entity_set'])

# ################################################################################################################################
# ################################################################################################################################

class SAPToolInvoke(TestCase):
    """ Tests for invoking SAP connection tools.
    """

# ################################################################################################################################

    def test_invoke_read(self) -> 'None':
        """ Verifies that a read runs against the entity set with the call's arguments.
        """

        client = StubMethodClient({'read': [{'CustomerId': '123'}]})
        config_manager = _make_config_manager(client)
        wrapper = make_gateway_wrapper(config_manager, sap_connections=['erp'])

        arguments = {
            'operation': 'read',
            'entity_set': 'Customers',
            'arguments': {'top': 10},
        }

        response = wrapper._invoke_service('sap.erp', arguments)

        self.assertEqual(response, [{'CustomerId': '123'}])

        method, args, kwargs = client.calls[0]
        self.assertEqual(method, 'read')
        self.assertEqual(args, ('Customers',))
        self.assertEqual(kwargs, {'top': 10})

# ################################################################################################################################

    def test_invoke_get_passes_key_positionally(self) -> 'None':
        """ Verifies that a get pops the key out of the arguments and passes it positionally.
        """

        client = StubMethodClient({'get': {'CustomerId': '123'}})
        config_manager = _make_config_manager(client)
        wrapper = make_gateway_wrapper(config_manager, sap_connections=['erp'])

        arguments = {
            'operation': 'get',
            'entity_set': 'Customers',
            'arguments': {'key': '123'},
        }

        response = wrapper._invoke_service('sap.erp', arguments)

        self.assertEqual(response, {'CustomerId': '123'})

        method, args, kwargs = client.calls[0]
        self.assertEqual(method, 'get')
        self.assertEqual(args, ('Customers', '123'))
        self.assertEqual(kwargs, {})

# ################################################################################################################################

    def test_invoke_refuses_unknown_operation(self) -> 'None':
        """ Verifies that an operation outside the table is refused.
        """

        client = StubMethodClient({})
        config_manager = _make_config_manager(client)
        wrapper = make_gateway_wrapper(config_manager, sap_connections=['erp'])

        arguments = {
            'operation': 'drop_everything',
            'entity_set': 'Customers',
        }

        with self.assertRaises(Exception) as ctx:
            _ = wrapper._invoke_service('sap.erp', arguments)

        self.assertIn('drop_everything', str(ctx.exception))
        self.assertEqual(client.calls, [])

# ################################################################################################################################
# ################################################################################################################################

class SAPToolsCall(TestCase):
    """ Tests for SAP tools through the full tools/call path.
    """

# ################################################################################################################################

    def test_tools_call_error_is_generic(self) -> 'None':
        """ Verifies that a refused operation produces the generic refusal with isError true.
        """

        client = StubMethodClient({})
        config_manager = _make_config_manager(client)
        wrapper = make_gateway_wrapper(config_manager, sap_connections=['erp'])
        handler = make_mcp_handler(wrapper)

        mcp_response = run_tools_call(handler, 'sap.erp', {'operation': 'drop_everything', 'entity_set': 'Customers'})

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])

        text = result['content'][0]['text']
        self.assertEqual(text, 'Bad request')

# ################################################################################################################################
# ################################################################################################################################
