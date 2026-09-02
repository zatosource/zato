# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from unittest import TestCase

# gevent
from gevent import sleep as gevent_sleep

# Zato
from zato.server.connection.mcp.connection_tools.rest import definition

# Zato - test helpers
from connection_stubs import get_tool_registry, make_gateway_wrapper, make_mcp_handler, make_rest_item, run_tools_call, \
    StubConfigManager, StubRESTWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _make_config_manager(wrapper:'any_'=None) -> 'StubConfigManager':
    """ A config manager with one REST connection called billing.
    """

    out = StubConfigManager()
    out.config_store.out_plain_http['billing'] = make_rest_item('https://example.com', '/api/billing', wrapper)

    return out

# ################################################################################################################################
# ################################################################################################################################

class RESTToolShape(TestCase):
    """ Tests for the shape of REST connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = _make_config_manager()
        wrapper = make_gateway_wrapper(config_manager, rest_connections=['billing'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'rest.billing')
        self.assertEqual(tool['description'], 'Invokes the outgoing REST connection `billing` (https://example.com/api/billing)')
        self.assertEqual(tool['inputSchema'], definition.input_schema)

        method_schema = definition.input_schema['properties']['method']
        self.assertEqual(method_schema['enum'], ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
        self.assertEqual(definition.input_schema['required'], ['method'])

# ################################################################################################################################
# ################################################################################################################################

class RESTToolInvoke(TestCase):
    """ Tests for invoking REST connection tools.
    """

# ################################################################################################################################

    def test_invoke_passes_method_params_and_data(self) -> 'None':
        """ Verifies that the wrapper's http_request receives what the tool call carried.
        """

        rest_wrapper = StubRESTWrapper(status_code=200, data={'balance': 357})
        config_manager = _make_config_manager(rest_wrapper)
        wrapper = make_gateway_wrapper(config_manager, rest_connections=['billing'])

        arguments = {
            'method': 'POST',
            'params': {'customer_id': '123'},
            'data': {'amount': 10},
        }

        response = wrapper._invoke_service('rest.billing', arguments)

        self.assertEqual(response, {'status_code': 200, 'data': {'balance': 357}})

        call = rest_wrapper.calls[0]
        method, _cid, data, params = call

        self.assertEqual(method, 'POST')
        self.assertEqual(data, {'amount': 10})
        self.assertEqual(params, {'customer_id': '123'})

# ################################################################################################################################

    def test_invoke_without_body_sends_empty_string(self) -> 'None':
        """ Verifies that a call without data sends an empty body, never None.
        """

        rest_wrapper = StubRESTWrapper(status_code=200, data='')
        config_manager = _make_config_manager(rest_wrapper)
        wrapper = make_gateway_wrapper(config_manager, rest_connections=['billing'])

        _ = wrapper._invoke_service('rest.billing', {'method': 'GET'})

        call = rest_wrapper.calls[0]
        _method, _cid, data, _params = call

        self.assertEqual(data, '')

# ################################################################################################################################
# ################################################################################################################################

class RESTToolsCall(TestCase):
    """ Tests for REST tools through the full tools/call path.
    """

# ################################################################################################################################

    def test_tools_call_success(self) -> 'None':
        """ Verifies that tools/call reaches the connection and returns its response.
        """

        rest_wrapper = StubRESTWrapper(status_code=200, data={'balance': 357})
        config_manager = _make_config_manager(rest_wrapper)
        wrapper = make_gateway_wrapper(config_manager, rest_connections=['billing'])
        handler = make_mcp_handler(wrapper)

        mcp_response = run_tools_call(handler, 'rest.billing', {'method': 'GET'})

        self.assertEqual(mcp_response.status_code, OK)

        result = mcp_response.body['result']
        self.assertNotIn('isError', result)

        text = result['content'][0]['text']
        self.assertIn('357', text)

# ################################################################################################################################

    def test_tools_call_error_is_generic(self) -> 'None':
        """ Verifies that a failing connection produces the generic refusal with isError true.
        """

        class _FailingWrapper:
            def http_request(self, method:'str', cid:'str', data:'any_'=None, params:'any_'=None) -> 'any_':
                raise Exception('Connection refused by the remote end')

        config_manager = _make_config_manager(_FailingWrapper())
        wrapper = make_gateway_wrapper(config_manager, rest_connections=['billing'])
        handler = make_mcp_handler(wrapper)

        mcp_response = run_tools_call(handler, 'rest.billing', {'method': 'GET'})

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])

        # The client never learns what actually went wrong
        text = result['content'][0]['text']
        self.assertEqual(text, 'Bad request')

# ################################################################################################################################

    def test_tools_call_timeout_is_generic(self) -> 'None':
        """ Verifies that a connection running past the gateway's timeout is cut off
        with the generic refusal and isError true.
        """

        class _SlowWrapper:
            def http_request(self, method:'str', cid:'str', data:'any_'=None, params:'any_'=None) -> 'any_':
                gevent_sleep(5)

        config_manager = _make_config_manager(_SlowWrapper())
        wrapper = make_gateway_wrapper(config_manager, rest_connections=['billing'])
        handler = make_mcp_handler(wrapper, invoke_timeout=1)

        mcp_response = run_tools_call(handler, 'rest.billing', {'method': 'GET'})

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])

        text = result['content'][0]['text']
        self.assertEqual(text, 'Bad request')

# ################################################################################################################################
# ################################################################################################################################
