# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from unittest import TestCase

# Zato
from zato.common.json_internal import dumps, loads
from zato.common.test import _test_sec_def_id
from zato.common.typing_ import cast_
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.common import MCPResponse
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_params, _mcp_protocol_version
from zato.server.connection.mcp.prompts import SkillPrompts
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# The tool every test invokes
_test_tool_name = 'crm.invoice.list'

# The schema the mock registry declares for the tool - one required string field
_test_tool_schema:'stranydict' = {
    'type': 'object',
    'properties': {
        'customer_id': {'type': 'string'},
    },
    'required': ['customer_id'],
}

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ Mock tool registry with one tool that has a declared input schema.
    """
    def get_tools(self) -> 'anylist':
        out = [
            {
                'name': _test_tool_name,
                'description': 'Returns invoices of one customer',
                'inputSchema': _test_tool_schema,
            },
        ]

        return out

    def get_tools_page(self, cursor:'strnone' = None) -> 'anytuple':
        tools = self.get_tools()

        out = (tools, None)
        return out

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        out = service_name == _test_tool_name
        return out

    def get_tool_schema(self, service_name:'str') -> 'stranydict':
        return _test_tool_schema

# ################################################################################################################################
# ################################################################################################################################

def _make_handler(
    invoke_func:'callable_',
    gateway_config:'stranydict',
    validate_input:'bool' = False,
    allow_client_filters:'bool' = True,
    ) -> 'MCPHandler':
    """ Creates an MCPHandler the way the gateway wrapper builds one at runtime,
    with client filters allowed unless a test says otherwise.
    """

    # The mock stands in for the real registry, which the handler only ever duck-types against
    registry = cast_('any_', _MockToolRegistry())
    session_manager = MCPSessionManager()

    safeguard_config = build_safeguard_config(gateway_config)
    token_cap_config = build_token_cap_config(gateway_config)

    out = MCPHandler(registry, invoke_func, session_manager, safeguard_config, token_cap_config, validate_input,
        SkillPrompts('', []), allow_client_filters)
    return out

# ################################################################################################################################

def _run_method(handler:'MCPHandler', method:'str', params:'anydict') -> 'MCPResponse':
    """ Establishes a session and runs one request through the full raw-request path.
    """

    session_manager = handler.session_manager
    session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

    request = {
        'jsonrpc': '2.0',
        'method': method,
        'id': 1,
        'params': params,
    }
    raw = dumps(request)

    out = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)
    return out

# ################################################################################################################################

def _get_text(result:'stranydict') -> 'str':
    """ Extracts the text of the first content element of a tools/call result.
    """

    content = result['content']
    first_content = content[0]

    out = first_content['text']
    return out

# ################################################################################################################################

def _invoke_invoices(service_name:'str', payload:'any_') -> 'anydict':
    """ The service every filter test calls - a fixed set of invoices with amounts.
    """

    out = {
        'total_count': 3,
        'rows': [
            {'invoice_id': 'inv-00001', 'amount': 100},
            {'invoice_id': 'inv-00002', 'amount': 250},
            {'invoice_id': 'inv-00003', 'amount': 75},
        ],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class ResponseFilterInToolsList(TestCase):

    def test_enabled_gateway_advertises_response_filter(self) -> 'None':
        """ With client filters allowed, every tool's schema advertises the optional
        response_filter property next to the tool's own fields.
        """

        handler = _make_handler(_invoke_invoices, {})
        mcp_response = _run_method(handler, 'tools/list', {})

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        tools = body['result']['tools']
        tool = tools[0]

        properties = tool['inputSchema']['properties']

        self.assertIn('response_filter', properties)
        self.assertIn('customer_id', properties)
        self.assertEqual(properties['response_filter']['type'], 'string')

    def test_disabled_gateway_says_nothing_of_response_filter(self) -> 'None':
        """ Without client filters, the schemas carry only the tools' own fields.
        """

        handler = _make_handler(_invoke_invoices, {}, allow_client_filters=False)
        mcp_response = _run_method(handler, 'tools/list', {})

        body = mcp_response.body
        tools = body['result']['tools']
        tool = tools[0]

        properties = tool['inputSchema']['properties']

        self.assertNotIn('response_filter', properties)

    def test_the_registry_schema_is_never_mutated(self) -> 'None':
        """ Advertising the filter works on a copy - the cached schema that validation
        reads stays without the response_filter property.
        """

        handler = _make_handler(_invoke_invoices, {})
        _ = _run_method(handler, 'tools/list', {})

        self.assertNotIn('response_filter', _test_tool_schema['properties'])

# ################################################################################################################################
# ################################################################################################################################

class ResponseFilterInToolsCall(TestCase):

    def test_filter_shapes_the_response_and_lands_in_the_trace(self) -> 'None':
        """ A valid JSONata expression reshapes the response and the trace records
        the expression that was applied.
        """

        expression = 'rows.amount'
        params = {
            'name': _test_tool_name,
            'arguments': {'customer_id': 'abc-123', 'response_filter': expression},
        }

        handler = _make_handler(_invoke_invoices, {})
        mcp_response = _run_method(handler, 'tools/call', params)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']

        self.assertNotIn('isError', result)

        response = loads(_get_text(result))
        self.assertEqual(response, [100, 250, 75])

        trace = mcp_response.trace
        self.assertIsNotNone(trace)

        if trace:
            self.assertEqual(trace['client_filter'], expression)

    def test_a_call_without_a_filter_leaves_no_trace(self) -> 'None':
        """ On an enabled gateway, a call that passes no filter is delivered whole
        and the trace stays empty.
        """

        params = {
            'name': _test_tool_name,
            'arguments': {'customer_id': 'abc-123'},
        }

        handler = _make_handler(_invoke_invoices, {})
        mcp_response = _run_method(handler, 'tools/call', params)

        body = mcp_response.body
        result = body['result']

        response = loads(_get_text(result))
        self.assertEqual(response['total_count'], 3)

        self.assertIsNone(mcp_response.trace)

    def test_invalid_expression_is_invalid_params(self) -> 'None':
        """ An expression that does not compile is the caller's own mistake
        and comes back as a JSON-RPC invalid-params error.
        """

        params = {
            'name': _test_tool_name,
            'arguments': {'customer_id': 'abc-123', 'response_filter': 'rows.amount)('},
        }

        handler = _make_handler(_invoke_invoices, {})
        mcp_response = _run_method(handler, 'tools/call', params)

        body = mcp_response.body
        error = body['error']

        self.assertEqual(error['code'], _error_invalid_params)
        self.assertIn('response_filter', error['message'])

    def test_a_filter_that_is_not_a_string_is_invalid_params(self) -> 'None':
        """ A filter of any type other than string is refused the same way a broken one is.
        """

        params = {
            'name': _test_tool_name,
            'arguments': {'customer_id': 'abc-123', 'response_filter': 123},
        }

        handler = _make_handler(_invoke_invoices, {})
        mcp_response = _run_method(handler, 'tools/call', params)

        body = mcp_response.body
        error = body['error']

        self.assertEqual(error['code'], _error_invalid_params)
        self.assertIn('expected a string', error['message'])

    def test_filter_runs_after_safeguards(self) -> 'None':
        """ The filter sees the cleaned value - a key that null stripping removed
        is not there for the expression to read.
        """

        def invoke_func(service_name:'str', payload:'any_') -> 'anydict':
            out = {'name': 'Renata Brixen', 'city': 'Bruntal', 'fax': None}
            return out

        params = {
            'name': _test_tool_name,
            'arguments': {'customer_id': 'abc-123', 'response_filter': '$keys($)'},
        }

        gateway_config = {'safeguards_strip_nulls': True}

        handler = _make_handler(invoke_func, gateway_config)
        mcp_response = _run_method(handler, 'tools/call', params)

        body = mcp_response.body
        result = body['result']

        response = loads(_get_text(result))
        self.assertEqual(response, ['name', 'city'])

    def test_validation_never_sees_the_filter_on_an_enabled_gateway(self) -> 'None':
        """ With both validation and client filters on, the filter is taken out
        before validation runs, so the tool's own schema still matches.
        """

        expression = 'total_count'
        params = {
            'name': _test_tool_name,
            'arguments': {'customer_id': 'abc-123', 'response_filter': expression},
        }

        handler = _make_handler(_invoke_invoices, {}, validate_input=True)
        mcp_response = _run_method(handler, 'tools/call', params)

        body = mcp_response.body
        result = body['result']

        self.assertNotIn('isError', result)

        response = loads(_get_text(result))
        self.assertEqual(response, 3)

    def test_disabled_gateway_refuses_the_filter_as_unknown_parameter(self) -> 'None':
        """ Without client filters, response_filter is a parameter like any other
        and a validating gateway refuses it as unknown.
        """

        params = {
            'name': _test_tool_name,
            'arguments': {'customer_id': 'abc-123', 'response_filter': 'total_count'},
        }

        handler = _make_handler(_invoke_invoices, {}, validate_input=True, allow_client_filters=False)
        mcp_response = _run_method(handler, 'tools/call', params)

        body = mcp_response.body
        error = body['error']

        self.assertEqual(error['code'], _error_invalid_params)
        self.assertIn('Unknown parameter', error['message'])
        self.assertIn('response_filter', error['message'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from unittest import main

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
