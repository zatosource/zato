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
from zato.common.util.truncate.tokens import build_token_cap_config, Size_Cap_Mode_Block
from zato.server.connection.mcp.handler import MCPHandler, _mcp_protocol_version
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, callable_, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# The tool every test invokes
_test_tool_name = 'crm.get-customer'

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ Mock tool registry that allows the one tool the tests invoke.
    """
    def get_tools(self) -> 'anylist':
        return []

    def get_tools_page(self, cursor:'strnone' = None) -> 'tuple':
        return [], None

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        return service_name == _test_tool_name

# ################################################################################################################################
# ################################################################################################################################

def _make_handler(invoke_func:'callable_', gateway_config:'stranydict') -> 'MCPHandler':
    """ Creates an MCPHandler whose shaping configs are built from a flat gateway config,
    the same way the gateway wrapper builds them from opaque configuration at runtime.
    """

    registry = _MockToolRegistry()
    session_manager = MCPSessionManager()

    safeguard_config = build_safeguard_config(gateway_config)
    token_cap_config = build_token_cap_config(gateway_config)

    out = MCPHandler(registry, invoke_func, session_manager, safeguard_config, token_cap_config) # pyright: ignore[reportArgumentType]
    return out

# ################################################################################################################################

def _call_tool(handler:'MCPHandler', arguments:'anydict') -> 'stranydict':
    """ Establishes a session and runs one tools/call through the full raw-request path,
    returning the result object of the JSON-RPC response.
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

    body = mcp_response.body

    out = body['result']
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
# ################################################################################################################################

class SafeguardsInToolsCall(TestCase):

    def test_no_shaping_config_passes_the_response_through(self) -> 'None':
        """ With every stage off, a response with nulls and whitespace is delivered as it is.
        """

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            return {'customer': 'Customer  name', 'middle_name': None}

        handler = _make_handler(invoke_func, {})
        result = _call_tool(handler, {})

        self.assertNotIn('isError', result)

        response = loads(_get_text(result))
        self.assertEqual(response, {'customer': 'Customer  name', 'middle_name': None})

    def test_strip_nulls_removes_null_keys_from_the_response(self) -> 'None':
        """ With strip_nulls on, null keys disappear before the response is serialized.
        """

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            return {'customer': 'Customer name here', 'middle_name': None, 'fax': None}

        handler = _make_handler(invoke_func, {'safeguards_strip_nulls': True})
        result = _call_tool(handler, {})

        self.assertNotIn('isError', result)

        response = loads(_get_text(result))
        self.assertEqual(response, {'customer': 'Customer name here'})

    def test_unicode_reject_mode_refuses_a_response_with_smuggled_characters(self) -> 'None':
        """ With unicode normalization in reject mode, zero-width characters refuse the response
        and the client learns the reject kind, never the content.
        """

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            return {'note': 'Approved\u200b by the head office'}

        gateway_config = {
            'safeguards_normalize_unicode': True,
            'safeguards_unicode_mode': 'reject',
        }

        handler = _make_handler(invoke_func, gateway_config)
        result = _call_tool(handler, {})

        self.assertTrue(result['isError'])
        self.assertEqual(_get_text(result), 'Response rejected: unicode')

    def test_unicode_clean_mode_delivers_the_cleaned_response(self) -> 'None':
        """ With unicode normalization in clean mode, the smuggled characters are removed
        and the response is delivered.
        """

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            return {'note': 'Approved\u200b by the head office'}

        gateway_config = {
            'safeguards_normalize_unicode': True,
            'safeguards_unicode_mode': 'clean',
        }

        handler = _make_handler(invoke_func, gateway_config)
        result = _call_tool(handler, {})

        self.assertNotIn('isError', result)

        response = loads(_get_text(result))
        self.assertEqual(response, {'note': 'Approved by the head office'})

# ################################################################################################################################
# ################################################################################################################################

class TokenCapInToolsCall(TestCase):

    def test_block_mode_refuses_an_oversized_response(self) -> 'None':
        """ With a small cap in block mode, an oversized response is refused
        with a message naming the size and the cap.
        """

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            rows = []
            for index in range(500):
                rows.append({'id': f'inv-{index:05}', 'customer': 'Customer name here'})
            return {'rows': rows}

        gateway_config = {
            'max_response_size': 10,
            'size_cap_mode': Size_Cap_Mode_Block,
        }

        handler = _make_handler(invoke_func, gateway_config)
        result = _call_tool(handler, {})

        self.assertTrue(result['isError'])

        text = _get_text(result)
        self.assertIn('Response too large:', text)
        self.assertIn('cap is 10', text)

    def test_truncate_mode_delivers_a_trimmed_response(self) -> 'None':
        """ With a cap in truncate mode, an oversized response is trimmed to fit
        and the scalar fields survive.
        """

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            rows = []
            for index in range(2000):
                rows.append({'id': f'inv-{index:05}', 'customer': 'Customer name here'})
            return {'status': 'ok', 'rows': rows}

        gateway_config = {
            'max_response_size': 2048,
        }

        handler = _make_handler(invoke_func, gateway_config)
        result = _call_tool(handler, {})

        self.assertNotIn('isError', result)

        response = loads(_get_text(result))
        self.assertEqual(response['status'], 'ok')
        self.assertLess(len(response['rows']), 2000)

    def test_response_below_the_threshold_skips_the_cap(self) -> 'None':
        """ With an activation threshold above the response size, the cap never runs.
        """

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            return {'status': 'ok'}

        gateway_config = {
            'max_response_size': 1,
            'min_size_threshold': 1000,
            'size_cap_mode': Size_Cap_Mode_Block,
        }

        handler = _make_handler(invoke_func, gateway_config)
        result = _call_tool(handler, {})

        self.assertNotIn('isError', result)

        response = loads(_get_text(result))
        self.assertEqual(response, {'status': 'ok'})

# ################################################################################################################################
# ################################################################################################################################

class CombinedShapingInToolsCall(TestCase):

    def test_safeguards_run_before_the_cap(self) -> 'None':
        """ Null stripping can bring a response under the cap - the cleaned size is what the cap sees.
        """

        def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
            response:'anydict' = {'customer': 'Customer name here'}
            for index in range(500):
                response[f'unused_field_{index:05}'] = None
            return response

        gateway_config = {
            'safeguards_strip_nulls': True,
            'max_response_size': 100,
            'size_cap_mode': Size_Cap_Mode_Block,
        }

        handler = _make_handler(invoke_func, gateway_config)
        result = _call_tool(handler, {})

        self.assertNotIn('isError', result)

        response = loads(_get_text(result))
        self.assertEqual(response, {'customer': 'Customer name here'})

# ################################################################################################################################
# ################################################################################################################################
