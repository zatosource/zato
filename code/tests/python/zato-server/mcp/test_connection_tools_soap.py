# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.soap.message import XMLMessage
from zato.server.connection.mcp.connection_tools.soap import definition

# Zato - test helpers
from connection_stubs import get_tool_registry, make_gateway_wrapper, make_mcp_handler, make_soap_item, run_tools_call, \
    StubConfigManager, StubSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _make_config_manager(wrapper:'any_'=None) -> 'StubConfigManager':
    """ A config manager with one SOAP connection called billing.
    """

    out = StubConfigManager()
    out.config_store.out_soap['billing'] = make_soap_item(
        'https://example.com', '/soap/billing', 'urn:get-balance', wrapper)

    return out

# ################################################################################################################################
# ################################################################################################################################

class SOAPToolShape(TestCase):
    """ Tests for the shape of SOAP connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = _make_config_manager()
        wrapper = make_gateway_wrapper(config_manager, soap_connections=['billing'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'soap.billing')
        self.assertEqual(
            tool['description'],
            'Invokes the outgoing SOAP connection `billing` (https://example.com/soap/billing, action: urn:get-balance)')
        self.assertEqual(tool['inputSchema'], definition.input_schema)

        properties = definition.input_schema['properties']
        self.assertIn('operation', properties)
        self.assertIn('message', properties)

# ################################################################################################################################
# ################################################################################################################################

class SOAPToolInvoke(TestCase):
    """ Tests for invoking SOAP connection tools.
    """

# ################################################################################################################################

    def test_invoke_passes_operation_and_message(self) -> 'None':
        """ Verifies that the wrapper's invoke receives the operation and message.
        """

        soap_wrapper = StubSOAPWrapper(response={'balance': 357})
        config_manager = _make_config_manager(soap_wrapper)
        wrapper = make_gateway_wrapper(config_manager, soap_connections=['billing'])

        arguments = {
            'operation': 'GetBalance',
            'message': {'CustomerId': '123'},
        }

        response = wrapper._invoke_service('soap.billing', arguments)

        self.assertEqual(response, {'balance': 357})

        call = soap_wrapper.calls[0]
        _cid, operation, message = call

        self.assertEqual(operation, 'GetBalance')
        self.assertEqual(message, {'CustomerId': '123'})

# ################################################################################################################################

    def test_invoke_converts_xml_message_response(self) -> 'None':
        """ Verifies that a dot-accessed XML response travels back as a plain dict.
        """

        xml_response = XMLMessage()
        xml_response.Balance = 357

        soap_wrapper = StubSOAPWrapper(response=xml_response)
        config_manager = _make_config_manager(soap_wrapper)
        wrapper = make_gateway_wrapper(config_manager, soap_connections=['billing'])

        response = wrapper._invoke_service('soap.billing', {'operation': 'GetBalance'})

        self.assertEqual(response, {'Balance': 357})

# ################################################################################################################################
# ################################################################################################################################

class SOAPToolsCall(TestCase):
    """ Tests for SOAP tools through the full tools/call path.
    """

# ################################################################################################################################

    def test_tools_call_error_is_generic(self) -> 'None':
        """ Verifies that a failing connection produces the generic refusal with isError true.
        """

        class _FailingWrapper:
            def invoke(self, cid:'str', operation:'str', message:'any_'=None) -> 'any_':
                raise Exception('SOAP fault from the remote end')

        config_manager = _make_config_manager(_FailingWrapper())
        wrapper = make_gateway_wrapper(config_manager, soap_connections=['billing'])
        handler = make_mcp_handler(wrapper)

        mcp_response = run_tools_call(handler, 'soap.billing', {'operation': 'GetBalance'})

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])

        text = result['content'][0]['text']
        self.assertEqual(text, 'Bad request')

# ################################################################################################################################
# ################################################################################################################################
