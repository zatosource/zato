# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Data masking in the MCP tools/call pipeline - its position before PII removal,
# the agent filter and the token cap, and the counter it leaves in the audit trace.

# stdlib
from http.client import OK
from unittest import TestCase

# Zato
from zato.common.json_internal import dumps, loads
from zato.common.test import _test_identity
from zato.common.typing_ import cast_
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.safeguards.masking import Masked_Value
from zato.common.util.truncate.tokens import build_token_cap_config, Size_Cap_Mode_Block
from zato.server.connection.mcp.handler import MCPHandler, _mcp_protocol_version
from zato.server.connection.mcp.prompts import SkillPrompts
from zato.server.connection.mcp.session import MCPSessionManager
from zato.server.connection.mcp.tools_call import serialize_service_response

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# The tool every test invokes
_test_tool_name = 'crm.customer.get'

# The value the masked fields hold before masking
_test_iban = 'DE89370400440532013000'

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ Mock tool registry that allows the one tool the tests invoke.
    """
    def get_tools(self) -> 'anylist':
        return []

    def get_tools_page(self, cursor:'strnone' = None) -> 'anytuple':
        return [], None

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        out = service_name == _test_tool_name
        return out

    def get_tool_schema(self, service_name:'str') -> 'stranydict':
        return {'type': 'object', 'properties': {}}

# ################################################################################################################################
# ################################################################################################################################

def _invoke_customer(service_name:'str', payload:'any_') -> 'anydict':
    """ The service every test calls - a customer with two accounts.
    """
    out = {
        'customer_name': 'Jane Example',
        'contact': 'jane@example.com',
        'accounts': [
            {'IBAN': _test_iban, 'amount': 100},
            {'Iban': _test_iban, 'amount': 250},
        ],
    }

    return out

# ################################################################################################################################

def _make_handler(gateway_config:'stranydict', invoke_func:'callable_'=_invoke_customer) -> 'MCPHandler':
    """ Creates an MCPHandler the way the gateway wrapper builds one, with agent filters allowed.
    """
    registry = cast_('any_', _MockToolRegistry())
    session_manager = MCPSessionManager()

    safeguard_config = build_safeguard_config(gateway_config)
    token_cap_config = build_token_cap_config(gateway_config)

    out = MCPHandler(registry, invoke_func, session_manager, safeguard_config, token_cap_config, False,
        SkillPrompts('', []), True)
    return out

# ################################################################################################################################

def _call_tool(handler:'MCPHandler', arguments:'anydict') -> 'stranydict':
    """ Runs one tools/call through the full raw-request path and returns the JSON-RPC result.
    """
    session_id = handler.session_manager.create(_mcp_protocol_version, _test_identity)

    request = {
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'id': 1,
        'params': {'name': _test_tool_name, 'arguments': arguments},
    }

    response = handler.handle_raw_request(dumps(request), _test_identity, session_id=session_id)
    assert response.status_code == OK

    out = response.body['result']
    return out

# ################################################################################################################################

def _get_text(result:'stranydict') -> 'str':
    out = result['content'][0]['text']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMaskingInToolsCall(TestCase):

    def test_a_set_masks_its_fields_in_any_case(self) -> 'None':

        handler = _make_handler({'safeguards_masking_sets': ['banking']})
        result = _call_tool(handler, {})

        self.assertNotIn('isError', result)

        response = loads(_get_text(result))

        self.assertEqual(response['accounts'][0]['IBAN'], Masked_Value)
        self.assertEqual(response['accounts'][1]['Iban'], Masked_Value)
        self.assertEqual(response['accounts'][0]['amount'], 100)
        self.assertNotIn(_test_iban, _get_text(result))

    def test_an_excluded_field_is_delivered(self) -> 'None':

        handler = _make_handler({'safeguards_masking_sets': ['banking'], 'safeguards_masking_excluded': ['iban']})
        result = _call_tool(handler, {})

        response = loads(_get_text(result))
        self.assertEqual(response['accounts'][0]['IBAN'], _test_iban)

    def test_custom_fields_switched_off_are_delivered(self) -> 'None':

        gateway_config = {
            'safeguards_masking_custom_fields': ['customer_name'],
            'safeguards_masking_custom_enabled': False,
        }

        handler = _make_handler(gateway_config)
        result = _call_tool(handler, {})

        response = loads(_get_text(result))
        self.assertEqual(response['customer_name'], 'Jane Example')

    def test_masking_runs_before_pii_removal(self) -> 'None':

        gateway_config = {
            'safeguards_masking_custom_fields': ['contact'],
            'safeguards_pii_enabled': True,
            'safeguards_pii_detectors': ['email'],
        }

        handler = _make_handler(gateway_config)
        trace:'stranydict' = {}

        text = serialize_service_response(handler, {'contact': 'jane@example.com', 'note': 'jane@example.com'}, trace)
        response = loads(text)

        # The masked field holds the masking value, not a PII replacement ..
        self.assertEqual(response['contact'], Masked_Value)

        # .. and PII removal found only the value masking left in place.
        self.assertNotIn('jane@example.com', response['note'])
        self.assertEqual(trace['fields_masked'], 1)
        self.assertEqual(trace['pii_removed'], {'email': 1})

    def test_masking_runs_before_the_agent_filter(self) -> 'None':

        handler = _make_handler({'safeguards_masking_sets': ['banking']})
        result = _call_tool(handler, {'response_filter': 'accounts.(IBAN ? IBAN : Iban)'})

        self.assertNotIn('isError', result)

        response = loads(_get_text(result))
        self.assertEqual(response, [Masked_Value, Masked_Value])

    def test_masking_runs_before_the_token_cap(self) -> 'None':

        gateway_config = {
            'safeguards_masking_custom_fields': ['document'],
            'max_response_size': 50,
            'size_cap_mode': Size_Cap_Mode_Block,
        }

        handler = _make_handler(gateway_config)
        trace:'stranydict' = {}

        # The document alone would be over the cap, the masked document is well under it.
        text = serialize_service_response(handler, {'document': 'x' * 10_000}, trace)

        self.assertEqual(loads(text), {'document': Masked_Value})
        self.assertNotIn('reject_kind', trace)

    def test_the_trace_counts_the_masked_fields(self) -> 'None':

        handler = _make_handler({'safeguards_masking_sets': ['banking']})
        trace:'stranydict' = {}

        _ = serialize_service_response(handler, _invoke_customer(_test_tool_name, {}), trace)

        self.assertEqual(trace['fields_masked'], 2)

    def test_the_trace_is_silent_when_nothing_matched(self) -> 'None':

        handler = _make_handler({'safeguards_masking_custom_fields': ['no_such_field']})
        trace:'stranydict' = {}

        _ = serialize_service_response(handler, {'name': 'Jane'}, trace)

        self.assertNotIn('fields_masked', trace)

    def test_no_masking_configuration_delivers_everything(self) -> 'None':

        handler = _make_handler({})
        result = _call_tool(handler, {})

        response = loads(_get_text(result))
        self.assertEqual(response, _invoke_customer(_test_tool_name, {}))

# ################################################################################################################################
# ################################################################################################################################
