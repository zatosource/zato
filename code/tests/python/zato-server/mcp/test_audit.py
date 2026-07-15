# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.json_internal import dumps, loads
from zato.common.test import _test_sec_def_id
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.audit import build_audit_event, Method_Batch, Method_Session_Delete, Method_Unknown
from zato.server.connection.mcp.handler import MCPHandler, _mcp_protocol_version
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# What every builder test uses unless it overrides a field
_gateway_name = 'demo.mcp'
_sec_def_name = 'test.mcp.auth'
_cid = 'test-cid-123'
_session_id = 'mcp0123456789'
_remote_address = '10.20.30.40'

# ################################################################################################################################
# ################################################################################################################################

def _build(**overrides:'any_') -> 'stranydict':
    """ Calls build_audit_event with defaults that each test overrides as needed.
    """

    kwargs:'stranydict' = {
        'gateway_name': _gateway_name,
        'sec_def_name': _sec_def_name,
        'cid': _cid,
        'method': 'tools/call',
        'tool_name': 'crm.get-customer',
        'session_id': _session_id,
        'remote_address': _remote_address,
        'response_body': {'jsonrpc': '2.0', 'id': 1, 'result': {'content': []}},
        'response_size': 512,
        'status_code': 200,
        'duration_ms': 12.345,
        'request_size': 256,
    }
    kwargs.update(overrides)

    out = build_audit_event(**kwargs)
    return out

# ################################################################################################################################
# ################################################################################################################################

class BuildAuditEvent(TestCase):
    """ Tests for the published column mapping of the MCP audit log.
    """

    def test_tools_call_maps_every_column(self) -> 'None':

        event = _build()

        self.assertEqual(event['source'], AuditSource.MCP)
        self.assertEqual(event['event_type'], AuditEvent.MCP_Tools_Call)
        self.assertEqual(event['object_name'], _gateway_name)
        self.assertEqual(event['cid'], _cid)
        self.assertEqual(event['endpoint'], 'crm.get-customer')
        self.assertEqual(event['ext_client_id'], _sec_def_name)
        self.assertEqual(event['sub_key'], _session_id)
        self.assertEqual(event['size'], 512)
        self.assertEqual(event['outcome'], AuditOutcome.OK)

        data = loads(event['data'])
        self.assertEqual(data, {
            'remote_address': _remote_address,
            'method': 'tools/call',
            'duration_ms': 12.35,
            'request_size': 256,
        })

    def test_each_method_maps_to_its_event_type(self) -> 'None':

        cases = {
            'initialize': AuditEvent.MCP_Initialize,
            'tools/list': AuditEvent.MCP_Tools_List,
            'tools/call': AuditEvent.MCP_Tools_Call,
            Method_Batch: AuditEvent.MCP_Batch,
            Method_Session_Delete: AuditEvent.MCP_Session_Delete,
        }

        for method, expected_event_type in cases.items():
            event = _build(method=method)
            self.assertEqual(event['event_type'], expected_event_type)

    def test_methods_outside_the_set_audit_as_their_literal_name(self) -> 'None':

        event = _build(method='ping')
        self.assertEqual(event['event_type'], 'ping')

        event = _build(method='notifications/initialized')
        self.assertEqual(event['event_type'], 'notifications/initialized')

    def test_an_unparseable_request_audits_as_unknown(self) -> 'None':

        event = _build(method=None)
        self.assertEqual(event['event_type'], Method_Unknown)

        data = loads(event['data'])
        self.assertEqual(data['method'], Method_Unknown)

    def test_no_tool_name_and_no_session_map_to_empty_columns(self) -> 'None':

        event = _build(method='tools/list', tool_name=None, session_id=None)

        self.assertEqual(event['endpoint'], '')
        self.assertEqual(event['sub_key'], '')

    def test_a_jsonrpc_error_body_means_the_error_outcome(self) -> 'None':

        body = {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32602, 'message': 'Unknown parameter: `colour`'}}
        event = _build(response_body=body)

        self.assertEqual(event['outcome'], AuditOutcome.Error)

        data = loads(event['data'])
        self.assertEqual(data['error_code'], -32602)
        self.assertEqual(data['error_message'], 'Unknown parameter: `colour`')

    def test_a_non_2xx_status_means_the_error_outcome(self) -> 'None':

        event = _build(response_body=None, status_code=400)
        self.assertEqual(event['outcome'], AuditOutcome.Error)

        # There was no JSON-RPC error object, so no error fields appear in data
        data = loads(event['data'])
        self.assertNotIn('error_code', data)
        self.assertNotIn('error_message', data)

    def test_a_batch_with_one_erroring_element_means_the_error_outcome(self) -> 'None':

        body = [
            {'jsonrpc': '2.0', 'id': 1, 'result': {}},
            {'jsonrpc': '2.0', 'id': 2, 'error': {'code': -32601, 'message': 'Method not found: `nope`'}},
        ]
        event = _build(method=Method_Batch, response_body=body)

        self.assertEqual(event['outcome'], AuditOutcome.Error)

        data = loads(event['data'])
        self.assertEqual(data['error_code'], -32601)

    def test_a_batch_with_no_errors_means_the_ok_outcome(self) -> 'None':

        body = [
            {'jsonrpc': '2.0', 'id': 1, 'result': {}},
            {'jsonrpc': '2.0', 'id': 2, 'result': {}},
        ]
        event = _build(method=Method_Batch, response_body=body)

        self.assertEqual(event['outcome'], AuditOutcome.OK)

    def test_the_payload_is_never_included(self) -> 'None':

        secret = 'PESEL 02070803628 must never reach the audit log'
        body = {'jsonrpc': '2.0', 'id': 1, 'result': {'content': [{'type': 'text', 'text': secret}]}}

        event = _build(response_body=body)

        self.assertNotIn(secret, event['data'])
        self.assertNotIn('02070803628', event['data'])

# ################################################################################################################################
# ################################################################################################################################

# The tool the response-metadata tests invoke
_test_tool_name = 'crm.get-customer'

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

def _make_handler() -> 'MCPHandler':
    """ Creates an MCPHandler with every shaping stage and input validation off.
    """

    def invoke_func(service_name:'str', payload:'anydict') -> 'anydict':
        return {}

    registry = _MockToolRegistry()
    session_manager = MCPSessionManager()

    safeguard_config = build_safeguard_config({})
    token_cap_config = build_token_cap_config({})

    out = MCPHandler(registry, invoke_func, session_manager, safeguard_config, token_cap_config, False) # pyright: ignore[reportArgumentType]
    return out

# ################################################################################################################################
# ################################################################################################################################

class ResponseMetadata(TestCase):
    """ Tests that handle_raw_request records the method and tool name on MCPResponse,
    so the endpoint can audit without re-parsing the raw body.
    """

    def test_tools_call_records_method_and_tool_name(self) -> 'None':

        handler = _make_handler()
        session_id = handler.session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        request = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'id': 1,
            'params': {'name': _test_tool_name, 'arguments': {}},
        }

        mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.method, 'tools/call')
        self.assertEqual(mcp_response.tool_name, _test_tool_name)

    def test_other_methods_record_the_method_without_a_tool_name(self) -> 'None':

        handler = _make_handler()
        session_id = handler.session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        request = {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
        mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.method, 'ping')
        self.assertIsNone(mcp_response.tool_name)

    def test_a_batch_records_the_batch_marker(self) -> 'None':

        handler = _make_handler()
        session_id = handler.session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        request = [
            {'jsonrpc': '2.0', 'method': 'ping', 'id': 1},
            {'jsonrpc': '2.0', 'method': 'ping', 'id': 2},
        ]
        mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.method, Method_Batch)

    def test_an_unparseable_request_records_no_method(self) -> 'None':

        handler = _make_handler()
        mcp_response = handler.handle_raw_request(b'this is not json', _test_sec_def_id)

        self.assertIsNone(mcp_response.method)
        self.assertIsNone(mcp_response.tool_name)

# ################################################################################################################################
# ################################################################################################################################
