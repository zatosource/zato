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
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_params, _mcp_protocol_version
from zato.server.connection.mcp.session import MCPSessionManager
from zato.server.connection.mcp.validate import validate_arguments

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, callable_, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# The tool every handler-level test invokes
_test_tool_name = 'crm.get-customer'

# The schema of that tool - the same shape io_to_json_schema generates
# from a service with required and optional input, including a nested model.
_test_schema = {
    'type': 'object',
    'properties': {
        'customer_id': {'type': 'string'},
        'include_history': {'type': 'boolean'},
        'max_rows': {'type': 'integer'},
        'score': {'type': 'number'},
        'tags': {'type': 'array', 'items': {'type': 'string'}},
        'address': {
            'type': 'object',
            'properties': {
                'city': {'type': 'string'},
                'postcode': {'type': 'string'},
            },
            'required': ['city'],
        },
    },
    'required': ['customer_id'],
}

# A schema of a service with no declared input at all
_empty_schema = {'type': 'object'}

# ################################################################################################################################
# ################################################################################################################################

class ValidateArguments(TestCase):
    """ Tests for the pure validator - each case is a schema plus arguments and the expected outcome.
    """

    def test_valid_arguments_pass(self) -> 'None':
        arguments = {
            'customer_id': 'CRM-001',
            'include_history': True,
            'max_rows': 50,
            'score': 3.5,
            'tags': ['vip', 'invoicing'],
            'address': {'city': 'Warsaw', 'postcode': '00-001'},
        }

        self.assertIsNone(validate_arguments(arguments, _test_schema))

    def test_required_field_alone_passes(self) -> 'None':
        self.assertIsNone(validate_arguments({'customer_id': 'CRM-001'}, _test_schema))

    def test_missing_required_field_is_named(self) -> 'None':
        error = validate_arguments({'include_history': True}, _test_schema)
        self.assertEqual(error, 'Missing required parameter: `customer_id`')

    def test_unknown_field_is_named(self) -> 'None':
        error = validate_arguments({'customer_id': 'CRM-001', 'colour': 'blue'}, _test_schema)
        self.assertEqual(error, 'Unknown parameter: `colour`')

    def test_wrong_type_is_named(self) -> 'None':
        error = validate_arguments({'customer_id': 123}, _test_schema)
        self.assertEqual(error, 'Invalid type for `customer_id`: expected string')

    def test_a_bool_is_not_an_integer(self) -> 'None':
        error = validate_arguments({'customer_id': 'CRM-001', 'max_rows': True}, _test_schema)
        self.assertEqual(error, 'Invalid type for `max_rows`: expected integer')

    def test_an_integer_is_a_valid_number(self) -> 'None':
        self.assertIsNone(validate_arguments({'customer_id': 'CRM-001', 'score': 4}, _test_schema))

    def test_a_null_never_matches(self) -> 'None':
        error = validate_arguments({'customer_id': 'CRM-001', 'include_history': None}, _test_schema)
        self.assertEqual(error, 'Invalid type for `include_history`: expected boolean')

    def test_array_elements_are_validated_with_their_index(self) -> 'None':
        error = validate_arguments({'customer_id': 'CRM-001', 'tags': ['vip', 123]}, _test_schema)
        self.assertEqual(error, 'Invalid type for `tags[1]`: expected string')

    def test_nested_objects_are_validated_with_a_dotted_path(self) -> 'None':

        error = validate_arguments({'customer_id': 'CRM-001', 'address': {'postcode': '00-001'}}, _test_schema)
        self.assertEqual(error, 'Missing required parameter: `address.city`')

        error = validate_arguments({'customer_id': 'CRM-001', 'address': {'city': 'Warsaw', 'region': 'MZ'}}, _test_schema)
        self.assertEqual(error, 'Unknown parameter: `address.region`')

        error = validate_arguments({'customer_id': 'CRM-001', 'address': {'city': 123}}, _test_schema)
        self.assertEqual(error, 'Invalid type for `address.city`: expected string')

    def test_non_object_arguments_are_refused(self) -> 'None':
        error = validate_arguments(['customer_id'], _test_schema)
        self.assertEqual(error, 'Invalid arguments: expected an object')

    def test_a_schema_with_no_properties_accepts_anything(self) -> 'None':
        self.assertIsNone(validate_arguments({'anything': 'goes', 'depth': {'here': 'too'}}, _empty_schema))
        self.assertIsNone(validate_arguments({}, _empty_schema))

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ Mock tool registry that allows the one tool the tests invoke and serves its schema.
    """
    def get_tools(self) -> 'anylist':
        return []

    def get_tools_page(self, cursor:'strnone' = None) -> 'tuple':
        return [], None

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        return service_name == _test_tool_name

    def get_tool_schema(self, service_name:'str') -> 'stranydict':
        return _test_schema

# ################################################################################################################################
# ################################################################################################################################

def _make_handler(invoke_func:'callable_', validate_input:'bool') -> 'MCPHandler':
    """ Creates an MCPHandler with input validation on or off and every shaping stage disabled.
    """

    registry = _MockToolRegistry()
    session_manager = MCPSessionManager()

    safeguard_config = build_safeguard_config({})
    token_cap_config = build_token_cap_config({})

    out = MCPHandler(registry, invoke_func, session_manager, safeguard_config, token_cap_config, validate_input) # pyright: ignore[reportArgumentType]
    return out

# ################################################################################################################################

def _call_tool(handler:'MCPHandler', arguments:'anydict') -> 'stranydict':
    """ Establishes a session and runs one tools/call through the full raw-request path,
    returning the whole JSON-RPC response body.
    """

    session_manager = handler.session_manager
    session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

    request = {
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'id': 1,
        'params': {'name': _test_tool_name, 'arguments': arguments},
    }
    raw = dumps(request)

    mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

    assert mcp_response.status_code == OK

    out = mcp_response.body
    return out

# ################################################################################################################################
# ################################################################################################################################

class ValidationInToolsCall(TestCase):
    """ Tests for validation enforcement in the tools/call path.
    """

    def test_invalid_arguments_return_invalid_params_and_never_invoke(self) -> 'None':

        invoked = []

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            invoked.append(service_name)
            return {}

        handler = _make_handler(invoke_func, True)
        body = _call_tool(handler, {'include_history': True})

        error = body['error']
        self.assertEqual(error['code'], _error_invalid_params)
        self.assertEqual(error['message'], 'Missing required parameter: `customer_id`')

        self.assertEqual(invoked, [])

    def test_valid_arguments_invoke_the_service(self) -> 'None':

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            return {'echoed': payload}

        handler = _make_handler(invoke_func, True)
        body = _call_tool(handler, {'customer_id': 'CRM-001', 'max_rows': 10})

        result = body['result']
        self.assertNotIn('isError', result)

        content = result['content']
        response = loads(content[0]['text'])
        self.assertEqual(response, {'echoed': {'customer_id': 'CRM-001', 'max_rows': 10}})

    def test_validation_off_lets_anything_through(self) -> 'None':

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            return {'echoed': payload}

        handler = _make_handler(invoke_func, False)
        body = _call_tool(handler, {'no_such_field': 123})

        result = body['result']
        self.assertNotIn('isError', result)

        content = result['content']
        response = loads(content[0]['text'])
        self.assertEqual(response, {'echoed': {'no_such_field': 123}})

# ################################################################################################################################
# ################################################################################################################################
