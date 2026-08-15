# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from concurrent.futures import ThreadPoolExecutor
from http.client import BAD_REQUEST, NO_CONTENT, NOT_FOUND, OK
from json import dumps

# requests
import requests

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.test import rand_string
from zato.server.connection.mcp.audit import Method_Unknown

# local
import _agent
import _audit
import _constants
import _helpers
from _client_stateless import MCPStatelessClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# A protocol revision no gateway speaks
_unsupported_version = '1999-01-01'

# The notification the MCP handshake defines - a message without an id
_notification_method = 'notifications/initialized'

# How deeply the nested-arguments test nests them
_nesting_depth = 100

# Timeout in seconds for the requests this module sends without the shared client
_request_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

class TestProtocolNegotiation:
    """ Initialize negotiates the session revision and refuses a version the gateway does not speak.
    """

# ################################################################################################################################

    def test_initialize_negotiates_the_supported_version(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        response = _helpers.initialize_response(client)
        result = response.json()['result']

        assert result['protocolVersion'] == _constants.Protocol_Version_Sessions, result
        assert response.headers['Mcp-Session-Id'], response.headers

# ################################################################################################################################

    def test_an_unsupported_version_is_refused(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        headers = {'MCP-Protocol-Version': _unsupported_version}
        response = _helpers.initialize_response(client, extra_headers=headers)

        body = response.json()
        assert body['error']['code'] == _constants.Error_Unsupported_Protocol_Version, body

        # The error names every version the gateway does speak ..
        message = body['error']['message']
        assert _constants.Protocol_Version_Sessions in message, body
        assert _constants.Protocol_Version_Stateless in message, body

        # .. and no session was created for the refused initialize.
        assert 'Mcp-Session-Id' not in response.headers, response.headers

# ################################################################################################################################
# ################################################################################################################################

class TestSessionLifecycle:
    """ The session issued on initialize gates every later call and DELETE ends it.
    """

# ################################################################################################################################

    def test_the_session_gates_every_call(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # With the session, the call works ..
        tools = _helpers.list_tools(client, session_id)
        assert tools, tools

        # .. and without one, the same call is a protocol error.
        response = client.jsonrpc('tools/list')
        assert response.status_code == BAD_REQUEST, response.text

# ################################################################################################################################

    def test_ping_answers_on_a_live_session(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        response = client.jsonrpc('ping', session_id=session_id)
        body = response.json()

        assert response.status_code == OK, response.text
        assert body['result'] == {}, body

# ################################################################################################################################

    def test_delete_ends_the_session(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # The DELETE succeeds ..
        response = client.delete_session(session_id)
        assert response.status_code == OK, response.text

        # .. and the old session no longer opens any door.
        response = client.jsonrpc('tools/list', session_id=session_id)
        assert response.status_code == BAD_REQUEST, response.text

# ################################################################################################################################

    def test_deleting_an_unknown_session_is_not_found(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        response = client.delete_session('no-such-session')
        assert response.status_code == NOT_FOUND, response.text

# ################################################################################################################################
# ################################################################################################################################

class TestStatelessRevision:
    """ The stateless revision works against the same gateways the agents use -
    each request is self-contained and there are no sessions at all.
    """

# ################################################################################################################################

    def test_discover_advertises_both_revisions(self, zato_server:'anydict') -> 'None':

        mcp_url = zato_server['mcp_url'](_constants.Path_Main)
        client = MCPStatelessClient(mcp_url, auth=zato_server['basic_auth'])

        response = client.discover()
        result = response.json()['result']

        versions = result['protocolVersions']
        assert _constants.Protocol_Version_Sessions in versions, result
        assert _constants.Protocol_Version_Stateless in versions, result

# ################################################################################################################################

    def test_stateless_tools_list_and_call(self, zato_server:'anydict') -> 'None':

        mcp_url = zato_server['mcp_url'](_constants.Path_Main)
        client = MCPStatelessClient(mcp_url, auth=zato_server['basic_auth'])

        # tools/list needs no session and carries its cache hints ..
        response = client.tools_list()
        result = response.json()['result']

        tool_names = _helpers.get_tool_names(result['tools'])
        assert sorted(tool_names) == sorted(_constants.Service_List_CRM), tool_names
        assert result['resultType'] == 'complete', result

        # .. and tools/call runs the service the same way the session revision does.
        response = client.tools_call(_constants.Service_Order_Status, {'order_id': _constants.Order_ID})
        result = response.json()['result']

        text = result['content'][0]['text']
        assert _constants.Order_Status in text, result

# ################################################################################################################################
# ################################################################################################################################

class TestConcurrentSessions:
    """ Two agents on one gateway at the same time keep their sessions,
    transcripts and audit trails apart.
    """

# ################################################################################################################################

    def test_concurrent_agents_do_not_share_state(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client_one = _helpers.make_client(zato_server, _constants.Path_Main)
        client_two = _helpers.make_client(zato_server, _constants.Path_Main)

        task_one = f'What is the name of customer {_constants.Customer_ID}? Use the tools.'
        task_two = f'What is the delivery status of order {_constants.Order_ID}? Use the tools.'

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_one = executor.submit(_agent.run_agent, client_one, task_one)
            future_two = executor.submit(_agent.run_agent, client_two, task_two)

            result_one = future_one.result()
            result_two = future_two.result()

        # Each conversation ran in its own session ..
        assert result_one.session_id != result_two.session_id, (result_one.session_id, result_two.session_id)

        # .. each answered its own question from its own tools ..
        assert _helpers.text_contains(result_one.final_text, _constants.Customer_Name), result_one.final_text
        assert _helpers.text_contains(result_two.final_text, _constants.Order_Status), result_two.final_text

        # .. and in the audit trail, every event belongs to exactly one of the two sessions,
        # with no CID ever appearing under both.
        total_calls = len(result_one.tool_calls) + len(result_two.tool_calls)
        _ = _audit.wait_for_events(audit_db_path, total_calls, object_name=_constants.Gateway_Main, min_id=min_id)

        events = _audit.read_events(audit_db_path, object_name=_constants.Gateway_Main, min_id=min_id)

        cids_one = set()
        cids_two = set()

        for event in events:

            if event['sub_key'] == result_one.session_id:
                cids_one.add(event['cid'])

            if event['sub_key'] == result_two.session_id:
                cids_two.add(event['cid'])

        assert cids_one, events
        assert cids_two, events
        assert not (cids_one & cids_two), (cids_one, cids_two)

# ################################################################################################################################
# ################################################################################################################################

class TestMalformedRequests:
    """ Requests outside the protocol's shape each have one defined refusal or outcome -
    nothing malformed ever crashes the gateway or slips through half-processed.
    """

# ################################################################################################################################

    def test_a_batch_array_is_refused_whole(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # A JSON-RPC batch - a top-level array - gets one error for the whole body ..
        messages = [
            {'jsonrpc': '2.0', 'method': 'tools/list', 'id': 1},
            {'jsonrpc': '2.0', 'method': 'ping', 'id': 2},
        ]
        response = client.jsonrpc_array_body(messages, session_id=session_id)

        body = response.json()
        assert response.status_code == OK, response.text
        assert body['error']['code'] == _constants.Error_Invalid_Request, body

        # .. no element of it was executed - the session still works afterwards ..
        tools = _helpers.list_tools(client, session_id)
        assert tools, tools

        # .. and one audit event records the refusal under the unknown-method marker.
        events = _audit.wait_for_events(
            audit_db_path, 1, object_name=_constants.Gateway_Main, event_type=Method_Unknown, min_id=min_id)

        assert events[-1]['outcome'] == AuditOutcome.Error, events

# ################################################################################################################################

    def test_a_notification_returns_no_body(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # A request without an id is a notification - it gets no JSON-RPC body at all ..
        notification = {'jsonrpc': '2.0', 'method': _notification_method, 'params': {}}
        response = client.jsonrpc_raw(dumps(notification).encode('utf8'), session_id=session_id)

        assert response.status_code == NO_CONTENT, response.text
        assert response.text == '', response.text

        # .. the session stays valid ..
        tools = _helpers.list_tools(client, session_id)
        assert tools, tools

        # .. and the audit event carries the literal method name.
        events = _audit.wait_for_events(
            audit_db_path, 1, object_name=_constants.Gateway_Main, event_type=_notification_method, min_id=min_id)

        assert events[-1]['outcome'] == AuditOutcome.OK, events

# ################################################################################################################################

    def test_ids_of_every_shape_echo_back(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # A string id, an explicit null id, a float id and a very large integer id
        # each come back exactly as they went in.
        request_ids = ['req-abc', None, 1.5, 10 ** 18]

        for request_id in request_ids:

            response = client.jsonrpc('ping', request_id=request_id, session_id=session_id)
            body = response.json()

            assert response.status_code == OK, response.text
            assert 'result' in body, body
            assert body['id'] == request_id, body

# ################################################################################################################################

    def test_a_duplicate_key_keeps_the_last_value(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # The same key twice inside arguments - the last value is the one the service sees ..
        arguments = '{"order_id": "' + _constants.Order_ID_Not_Cancellable + '", "order_id": "' + _constants.Order_ID + '"}'
        params = '{"name": "' + _constants.Service_Order_Status + '", "arguments": ' + arguments + '}'
        raw_body = '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": ' + params + '}'

        response = client.jsonrpc_raw(raw_body.encode('utf8'), session_id=session_id)

        body = response.json()
        assert response.status_code == OK, response.text

        # .. which the response proves by echoing it back.
        data = _helpers.get_result_data(body)
        assert data['order_id'] == _constants.Order_ID, data

# ################################################################################################################################

    def test_deeply_nested_arguments_are_served(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # Arguments nested a hundred levels deep parse and dispatch like any others ..
        nested:'object' = 'bottom'

        for _ in range(_nesting_depth):
            nested = {'level': nested}

        arguments = {'order_id': _constants.Order_ID, 'context': nested}
        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, arguments)

        # .. and the call itself succeeds the way a flat one does.
        data = _helpers.get_result_data(body)
        assert data['order_id'] == _constants.Order_ID, data
        assert data['status'] == _constants.Order_Status, data

# ################################################################################################################################
# ################################################################################################################################

class TestInvalidCursors:
    """ Cursors are opaque and issued by the gateway itself - anything else refuses cleanly.
    """

# ################################################################################################################################

    def test_invalid_cursors_are_invalid_params(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # A garbage cursor, an empty-string cursor and one of another gateway's shape -
        # a foreign token with a valid-looking index - each refuse the same way.
        cursors = ['no-such-cursor', '', '0123abcd.100']

        for cursor in cursors:

            response = client.jsonrpc('tools/list', params={'cursor': cursor}, session_id=session_id)
            body = response.json()

            assert response.status_code == OK, response.text
            assert body['error']['code'] == _constants.Error_Invalid_Params, body

        # Every refusal landed in the audit log with the error outcome.
        events = _audit.wait_for_events(
            audit_db_path, len(cursors), object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_List, min_id=min_id)

        for event in events:
            assert event['outcome'] == AuditOutcome.Error, events

# ################################################################################################################################
# ################################################################################################################################

class TestHTTPLayer:
    """ The HTTP layer's own refusals and tolerances - content types and encodings.
    """

# ################################################################################################################################

    def test_a_missing_content_type_is_served(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # The body decides, not the header - a request without any content type still serves ..
        raw_body = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})
        headers = {'Mcp-Session-Id': session_id}

        mcp_url = zato_server['mcp_url'](_constants.Path_Main)
        response = requests.post(
            mcp_url, data=raw_body, headers=headers, auth=zato_server['basic_auth'], timeout=_request_timeout)

        body = response.json()
        assert response.status_code == OK, response.text
        assert body['result'] == {}, body

# ################################################################################################################################

    def test_a_non_json_content_type_is_served(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # .. the same for a content type that says the body is not JSON at all.
        raw_body = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})
        headers = {'Mcp-Session-Id': session_id, 'Content-Type': 'text/plain'}

        mcp_url = zato_server['mcp_url'](_constants.Path_Main)
        response = requests.post(
            mcp_url, data=raw_body, headers=headers, auth=zato_server['basic_auth'], timeout=_request_timeout)

        body = response.json()
        assert response.status_code == OK, response.text
        assert body['result'] == {}, body

# ################################################################################################################################

    def test_a_non_utf8_body_is_a_parse_error(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # Bytes that are not UTF-8 at all cannot parse and refuse as a parse error ..
        raw_body = b'\xff\xfe{"jsonrpc": "2.0"}'
        response = client.jsonrpc_raw(raw_body, session_id=session_id)

        body = response.json()
        assert response.status_code == OK, response.text
        assert body['error']['code'] == _constants.Error_Parse, body

        # .. audited under the unknown-method marker with the error outcome.
        events = _audit.wait_for_events(
            audit_db_path, 1, object_name=_constants.Gateway_Main, event_type=Method_Unknown, min_id=min_id)

        assert events[-1]['outcome'] == AuditOutcome.Error, events

# ################################################################################################################################
# ################################################################################################################################

class TestRequestValueRendering:
    """ Request-supplied names render as single bounded lines wherever a log or an error
    message embeds them - the audit log is the one place that keeps the raw value.
    """

# ################################################################################################################################

    def test_a_notification_method_renders_on_one_log_line(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        server_log_path = zato_server['server_log_path']

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        min_id = _audit.last_event_id(audit_db_path)
        log_offset = os.path.getsize(server_log_path)

        # The method name carries line breaks and a distinctive trailer ..
        trailer = 'orders.note.' + rand_string()
        method = f'orders/refresh\r\n{trailer}'

        notification = {'jsonrpc': '2.0', 'method': method, 'params': {}}
        response = client.jsonrpc_raw(dumps(notification).encode('utf8'), session_id=session_id)

        assert response.status_code == NO_CONTENT, response.text

        # .. the audit event keeps the method exactly as it was sent ..
        events = _audit.wait_for_events(
            audit_db_path, 1, object_name=_constants.Gateway_Main, event_type=method, min_id=min_id)

        assert events[-1]['outcome'] == AuditOutcome.OK, events

        # .. and in the server log the whole method sits inside the notification's own line -
        # the trailer never opens a line of its own.
        new_log_text = _helpers.read_new_log_text(server_log_path, log_offset)
        assert trailer in new_log_text, new_log_text

        for line in new_log_text.splitlines():
            if trailer in line:
                assert 'Received notification' in line, line

# ################################################################################################################################

    def test_an_unknown_method_is_reported_on_one_line(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        trailer = 'orders.note.' + rand_string()
        method = f'orders/refresh\r\n{trailer}'

        response = client.jsonrpc(method, session_id=session_id)
        body = response.json()

        assert body['error']['code'] == _constants.Error_Method_Not_Found, body

        # The message names the method on one line - the line breaks became spaces
        message = body['error']['message']

        assert '\r' not in message, body
        assert '\n' not in message, body
        assert trailer in message, body

# ################################################################################################################################

    def test_an_over_long_method_is_described_by_its_length(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        method = 'orders.' + 'a' * 400

        response = client.jsonrpc(method, session_id=session_id)
        body = response.json()

        assert body['error']['code'] == _constants.Error_Method_Not_Found, body

        # The message describes the name by its length instead of embedding it
        message = body['error']['message']

        assert method not in message, body
        assert f'(value of {len(method)} characters)' in message, body

# ################################################################################################################################

    def test_a_protocol_version_mismatch_names_no_header_value(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # The header disagrees with the session's negotiated version ..
        headers = {'MCP-Protocol-Version': _unsupported_version}
        response = client.jsonrpc('ping', session_id=session_id, extra_headers=headers)

        assert response.status_code == BAD_REQUEST, response.text

        # .. and the error names neither the header's value nor the negotiated one.
        message = response.json()['error']['message']

        assert _unsupported_version not in message, message
        assert _constants.Protocol_Version_Sessions not in message, message

# ################################################################################################################################

    def test_an_unsupported_version_names_only_supported_versions(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        headers = {'MCP-Protocol-Version': _unsupported_version}
        response = _helpers.initialize_response(client, extra_headers=headers)

        body = response.json()
        assert body['error']['code'] == _constants.Error_Unsupported_Protocol_Version, body

        # The supported versions are named, the requested one is not
        message = body['error']['message']

        assert _constants.Protocol_Version_Sessions in message, body
        assert _constants.Protocol_Version_Stateless in message, body
        assert _unsupported_version not in message, body

# ################################################################################################################################

    def test_a_session_id_with_a_tab_renders_as_plain_text(self, zato_server:'anydict') -> 'None':

        server_log_path = zato_server['server_log_path']
        log_offset = os.path.getsize(server_log_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        # A tab is the one control character an HTTP header value can carry -
        # the session id is unknown, so the request is refused ..
        trailer = 'orders.note.' + rand_string()
        session_id = f'mcp00000000\t{trailer}'

        response = client.jsonrpc('tools/list', session_id=session_id)
        assert response.status_code == BAD_REQUEST, response.text

        # .. and the log renders the id as plain text on the refusal's own line.
        new_log_text = _helpers.read_new_log_text(server_log_path, log_offset)
        assert trailer in new_log_text, new_log_text

        for line in new_log_text.splitlines():
            if trailer in line:
                assert 'Invalid or expired session' in line, line
                assert '\t' not in line, line

# ################################################################################################################################

    def test_a_stateless_header_mismatch_names_no_values(self, zato_server:'anydict') -> 'None':

        mcp_url = zato_server['mcp_url'](_constants.Path_Main)
        client = MCPStatelessClient(mcp_url, auth=zato_server['basic_auth'])

        # The Mcp-Method header says one thing and the body another ..
        response = client.jsonrpc('tools/list', mcp_method_header='ping')

        body = response.json()
        assert body['error']['code'] == _constants.Error_Header_Mismatch, body

        # .. and the error names neither of the two values.
        message = body['error']['message']

        assert 'ping' not in message, body
        assert 'tools/list' not in message, body

# ################################################################################################################################
# ################################################################################################################################
