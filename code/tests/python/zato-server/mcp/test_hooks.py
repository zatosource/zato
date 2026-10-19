# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The request and response hooks of MCPHandler - what each sees, what each may replace,
# how each refuses a message and which replies pass through the response hook.

# stdlib
from http.client import ACCEPTED, OK
from unittest import TestCase

# Zato
from zato.common.api import MCP
from zato.common.json_internal import dumps, loads
from zato.common.test import _test_identity, _test_public_name
from zato.common.typing_ import cast_
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.common import _error_request_rejected, _error_response_rejected, \
    _message_request_rejected, _message_response_rejected
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_request, _error_parse, _mcp_protocol_version
from zato.server.connection.mcp.prompts import SkillPrompts
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_, stranydict, strnone
    from zato.server.connection.mcp.common import MCPResponse

# ################################################################################################################################
# ################################################################################################################################

# The tools the registry allows
_test_tool_name  = 'crm.customer.get'
_other_tool_name = 'crm.customer.list'

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ Mock tool registry that allows the two tools the tests invoke.
    """
    def get_tools(self) -> 'anylist':
        return []

    def get_tools_page(self, cursor:'strnone' = None) -> 'anytuple':
        return [], None

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        out = service_name in (_test_tool_name, _other_tool_name)
        return out

    def get_tool_schema(self, service_name:'str') -> 'stranydict':
        return {'type': 'object', 'properties': {}}

# ################################################################################################################################
# ################################################################################################################################

class _Recorder:
    """ Hook functions that record every call and pass the message or the body through unchanged.
    """
    def __init__(self) -> 'None':
        self.requests:'anylist' = []
        self.responses:'anylist' = []

    def request_hook(self, identity:'str', message:'anydict') -> 'anydict':
        self.requests.append((identity, message))
        return message

    def response_hook(self, message:'any_', body:'anydict') -> 'anydict':
        self.responses.append((message, body))
        return body

# ################################################################################################################################
# ################################################################################################################################

def _invoke_echo(service_name:'str', payload:'any_') -> 'anydict':
    """ The service every test calls - it names itself and echoes its input.
    """
    out = {'service': service_name, 'input': payload}
    return out

# ################################################################################################################################

def _make_handler(
    request_hook_func:'callable_ | None' = None,
    response_hook_func:'callable_ | None' = None,
    ) -> 'MCPHandler':
    """ Creates an MCPHandler with every response stage off and the given hooks.
    """
    registry = cast_('any_', _MockToolRegistry())
    session_manager = MCPSessionManager()

    safeguard_config = build_safeguard_config({})
    token_cap_config = build_token_cap_config({})

    out = MCPHandler(registry, _invoke_echo, session_manager, safeguard_config, token_cap_config, False,
        SkillPrompts('', []), _test_public_name, False, MCP.Default_Invoke_Timeout, request_hook_func, response_hook_func)
    return out

# ################################################################################################################################

def _tools_call(tool_name:'str', arguments:'anydict', request_id:'any_' = 1) -> 'anydict':
    out = {
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'id': request_id,
        'params': {'name': tool_name, 'arguments': arguments},
    }
    return out

# ################################################################################################################################

def _send(handler:'MCPHandler', message:'any_') -> 'MCPResponse':
    """ Sends one message through the session-based revision, with a valid session.
    """
    session_id = handler.session_manager.create(_mcp_protocol_version, _test_identity)

    if isinstance(message, bytes):
        raw = message
    else:
        raw = dumps(message)

    out = handler.handle_raw_request(raw, _test_identity, session_id=session_id)
    return out

# ################################################################################################################################

def _send_stateless(handler:'MCPHandler', message:'anydict') -> 'MCPResponse':
    """ Sends one message through the stateless revision, with no session.
    """
    params = message['params']

    out = handler.handle_raw_request(
        dumps(message), _test_identity,
        protocol_version_header=MCP.Protocol_Version_Stateless,
        mcp_method_header=message['method'],
        mcp_name_header=params['name'],
    )

    return out

# ################################################################################################################################

def _result_payload(response:'MCPResponse') -> 'anydict':
    """ The service response a tools/call result carries.
    """
    text = response.body['result']['content'][0]['text']

    out = loads(text)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRequestHook(TestCase):

    def test_the_hook_sees_the_identity_and_the_message(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(request_hook_func=recorder.request_hook)

        message = _tools_call(_test_tool_name, {'customer_id': 'c-1'})
        response = _send(handler, message)

        self.assertEqual(response.status_code, OK)
        self.assertEqual(recorder.requests, [(_test_identity, message)])
        self.assertEqual(_result_payload(response), {'service': _test_tool_name, 'input': {'customer_id': 'c-1'}})

    def test_the_hook_sees_every_method(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(request_hook_func=recorder.request_hook)

        _ = _send(handler, {'jsonrpc': '2.0', 'method': 'tools/list', 'id': 1})
        _ = _send(handler, _tools_call(_test_tool_name, {}, 2))

        methods = [message['method'] for _, message in recorder.requests]
        self.assertEqual(methods, ['tools/list', 'tools/call'])

    def test_a_replaced_message_is_the_one_processed(self) -> 'None':

        def request_hook(identity:'str', message:'anydict') -> 'anydict':
            out = _tools_call(_other_tool_name, {'replaced': True}, message['id'])
            return out

        handler = _make_handler(request_hook_func=request_hook)
        response = _send(handler, _tools_call(_test_tool_name, {}))

        self.assertEqual(response.status_code, OK)
        self.assertEqual(_result_payload(response), {'service': _other_tool_name, 'input': {'replaced': True}})

    def test_a_refused_message_is_a_json_rpc_error(self) -> 'None':

        invoked:'anylist' = []

        def request_hook(identity:'str', message:'anydict') -> 'anydict':
            raise Exception('Refused by policy')

        def invoke_func(service_name:'str', payload:'any_') -> 'None':
            invoked.append(service_name)

        handler = _make_handler(request_hook_func=request_hook)
        handler.invoke_func = invoke_func

        response = _send(handler, _tools_call(_test_tool_name, {}, 7))

        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.body['id'], 7)
        self.assertEqual(response.body['error']['code'], _error_request_rejected)
        self.assertEqual(response.body['error']['message'], _message_request_rejected)
        self.assertEqual(invoked, [])

    def test_the_refusal_never_reveals_the_reason(self) -> 'None':

        def request_hook(identity:'str', message:'anydict') -> 'anydict':
            raise Exception('Internal policy detail')

        handler = _make_handler(request_hook_func=request_hook)
        response = _send(handler, _tools_call(_test_tool_name, {}))

        self.assertNotIn('Internal policy detail', dumps(response.body))

    def test_a_stateless_message_passes_the_hook(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(request_hook_func=recorder.request_hook)

        response = _send_stateless(handler, _tools_call(_test_tool_name, {'customer_id': 'c-2'}))

        self.assertEqual(response.status_code, OK)
        self.assertEqual(len(recorder.requests), 1)
        self.assertEqual(_result_payload(response)['input'], {'customer_id': 'c-2'})

    def test_a_batch_never_reaches_the_hook(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(request_hook_func=recorder.request_hook)

        response = _send(handler, [_tools_call(_test_tool_name, {}, 1), _tools_call(_test_tool_name, {}, 2)])

        self.assertEqual(response.body['error']['code'], _error_invalid_request)
        self.assertEqual(recorder.requests, [])

    def test_no_hook_leaves_the_message_alone(self) -> 'None':

        handler = _make_handler()
        response = _send(handler, _tools_call(_test_tool_name, {'customer_id': 'c-3'}))

        self.assertEqual(_result_payload(response)['input'], {'customer_id': 'c-3'})

# ################################################################################################################################
# ################################################################################################################################

class TestResponseHook(TestCase):

    def test_the_hook_sees_the_message_and_the_reply(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(response_hook_func=recorder.response_hook)

        message = _tools_call(_test_tool_name, {'customer_id': 'c-1'})
        response = _send(handler, message)

        self.assertEqual(len(recorder.responses), 1)

        seen_message, seen_body = recorder.responses[0]

        self.assertEqual(seen_message, message)
        self.assertIs(seen_body, response.body)

    def test_the_hook_sees_the_replaced_message(self) -> 'None':

        replaced = _tools_call(_other_tool_name, {}, 1)

        def request_hook(identity:'str', message:'anydict') -> 'anydict':
            return replaced

        recorder = _Recorder()
        handler = _make_handler(request_hook, recorder.response_hook)

        _ = _send(handler, _tools_call(_test_tool_name, {}))

        self.assertEqual(recorder.responses[0][0], replaced)

    def test_a_replaced_reply_is_the_one_sent(self) -> 'None':

        def response_hook(message:'anydict', body:'anydict') -> 'anydict':
            out = {'jsonrpc': '2.0', 'id': body['id'], 'result': {'content': [{'type': 'text', 'text': '{"replaced": true}'}]}}
            return out

        handler = _make_handler(response_hook_func=response_hook)
        response = _send(handler, _tools_call(_test_tool_name, {}))

        self.assertEqual(_result_payload(response), {'replaced': True})

    def test_a_refused_reply_is_a_json_rpc_error(self) -> 'None':

        def response_hook(message:'anydict', body:'anydict') -> 'anydict':
            raise Exception('Reply refused')

        handler = _make_handler(response_hook_func=response_hook)
        response = _send(handler, _tools_call(_test_tool_name, {}, 9))

        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.body['id'], 9)
        self.assertEqual(response.body['error']['code'], _error_response_rejected)
        self.assertEqual(response.body['error']['message'], _message_response_rejected)

    def test_a_request_refusal_passes_the_response_hook(self) -> 'None':

        def request_hook(identity:'str', message:'anydict') -> 'anydict':
            raise Exception('Refused')

        recorder = _Recorder()
        handler = _make_handler(request_hook, recorder.response_hook)

        response = _send(handler, _tools_call(_test_tool_name, {}))

        self.assertEqual(len(recorder.responses), 1)

        seen_message, seen_body = recorder.responses[0]

        self.assertIsNone(seen_message)
        self.assertEqual(seen_body['error']['code'], _error_request_rejected)
        self.assertIs(seen_body, response.body)

    def test_a_parse_error_passes_the_response_hook(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(response_hook_func=recorder.response_hook)

        response = _send(handler, b'{not json')

        self.assertEqual(response.body['error']['code'], _error_parse)
        self.assertEqual(len(recorder.responses), 1)
        self.assertIsNone(recorder.responses[0][0])

    def test_a_batch_rejection_passes_the_response_hook(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(response_hook_func=recorder.response_hook)

        response = _send(handler, [_tools_call(_test_tool_name, {})])

        self.assertEqual(response.body['error']['code'], _error_invalid_request)
        self.assertEqual(len(recorder.responses), 1)

    def test_a_missing_session_passes_the_response_hook(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(response_hook_func=recorder.response_hook)

        response = handler.handle_raw_request(dumps(_tools_call(_test_tool_name, {})), _test_identity)

        self.assertIn('error', response.body)
        self.assertEqual(len(recorder.responses), 1)

    def test_a_notification_has_no_response_hook_call(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(recorder.request_hook, recorder.response_hook)

        response = _send(handler, {'jsonrpc': '2.0', 'method': 'notifications/initialized'})

        self.assertEqual(response.status_code, ACCEPTED)
        self.assertIsNone(response.body)
        self.assertEqual(len(recorder.requests), 1)
        self.assertEqual(recorder.responses, [])

    def test_a_stateless_reply_passes_the_hook(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(response_hook_func=recorder.response_hook)

        response = _send_stateless(handler, _tools_call(_test_tool_name, {}))

        self.assertEqual(len(recorder.responses), 1)
        self.assertIs(recorder.responses[0][1], response.body)

    def test_an_initialize_reply_passes_the_hook(self) -> 'None':

        recorder = _Recorder()
        handler = _make_handler(response_hook_func=recorder.response_hook)

        params = {
            'protocolVersion': _mcp_protocol_version,
            'capabilities': {},
            'clientInfo': {'name': 'test', 'version': '1.0'},
        }

        message = {'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': params}
        response = handler.handle_raw_request(dumps(message), _test_identity)

        self.assertIn('result', response.body)
        self.assertEqual(recorder.responses[0][0]['method'], 'initialize')

# ################################################################################################################################
# ################################################################################################################################
