# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from http.client import NOT_FOUND, OK

# local
import _agent
import _audit
import _constants
import _diag
import _helpers

# Zato
from zato.common.api import MCP
from zato.common.audit_log.api import AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# How many tool calls the long conversation makes
_long_call_count = 22

# How many characters the large-but-accepted argument carries
_large_argument_size = 200_000

# An argument of this many characters is past the published request bound
_oversized_argument_size = MCP.Max_Request_Size + 100_000

# How long to wait until the idle TTL has passed, in seconds
_past_ttl_seconds = _constants.Session_TTL_Seconds + 1

# How long to wait until the reaper has provably swept, in seconds
_past_sweep_seconds = _constants.Session_TTL_Seconds + _constants.Reaper_Interval_Seconds + 2

# What the server logs when the reaper removes expired sessions
_reaper_log_marker = 'Reaper removed'

# ################################################################################################################################
# ################################################################################################################################

class TestConversationsAtScale:
    """ Long conversations, large arguments, non-ASCII data, the session cap
    and the idle TTL, each at the scale a real agent reaches.
    """

# ################################################################################################################################

    def test_a_long_conversation_holds_together(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # Every call of the long conversation succeeds on the one session ..
        for call_index in range(_long_call_count):

            arguments = {'order_id': f'{_constants.Order_ID}-{call_index}'}
            body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, arguments)

            data = _helpers.get_result_data(body)
            assert data['status'] == _constants.Order_Status, body

        # .. the audit trail has every event in order, each with a CID of its own ..
        events = _audit.wait_for_events(
            audit_db_path, _long_call_count,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        session_events = []

        for event in events:
            if event['sub_key'] == session_id:
                session_events.append(event)

        assert len(session_events) == _long_call_count, session_events

        cids = set()
        previous_id = 0

        for event in session_events:
            assert event['outcome'] == AuditOutcome.OK, event
            assert event['id'] > previous_id, session_events

            previous_id = event['id']
            cids.add(event['cid'])

        assert len(cids) == _long_call_count, cids

        # .. and the wire log carries the whole conversation - the initialize round trip
        # plus one request per call.
        wire_requests = _diag.get_entries('mcp_request')
        assert len(wire_requests) == _long_call_count + 1, len(wire_requests)

# ################################################################################################################################

    def test_large_arguments_have_defined_behavior(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # An argument of substantial size passes end to end ..
        large_order_id = 'ORD-' + 'A' * _large_argument_size

        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, {'order_id': large_order_id})

        data = _helpers.get_result_data(body)
        assert data['order_id'] == large_order_id, data['order_id']

        # .. with its request size audited ..
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event_data = events[-1]['data']
        assert event_data['request_size'] > _large_argument_size, event_data

        # .. while one past the published request bound is refused with a proper
        # JSON-RPC error rather than a broken connection.
        oversized_order_id = 'ORD-' + 'A' * _oversized_argument_size

        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, {'order_id': oversized_order_id})

        error = body['error']
        assert error['code'] == _constants.Error_Invalid_Request, body

# ################################################################################################################################

    def test_non_ascii_data_survives_the_whole_path(self, zato_server:'anydict') -> 'None':

        # The Greek record comes through the tools and the final answer intact ..
        client = _helpers.make_client(zato_server, _constants.Path_Main)

        task = f'Get the record of customer {_constants.Customer_ID_Greek} and report the name and city exactly as returned.'
        result = _agent.run_agent(client, task)

        result_text = result.tool_calls[0].result_text
        assert _constants.Customer_Name_Greek in result_text, result_text

        assert _helpers.text_contains(result.final_text, _constants.Customer_Name_Greek), result.final_text
        assert _helpers.text_contains(result.final_text, _constants.Customer_City_Greek), result.final_text

        # .. and so does the Japanese one.
        client = _helpers.make_client(zato_server, _constants.Path_Main)

        task = f'Get the record of customer {_constants.Customer_ID_Japanese} and report the name and city exactly as returned.'
        result = _agent.run_agent(client, task)

        result_text = result.tool_calls[0].result_text
        assert _constants.Customer_Name_Japanese in result_text, result_text

        assert _helpers.text_contains(result.final_text, _constants.Customer_Name_Japanese), result.final_text
        assert _helpers.text_contains(result.final_text, _constants.Customer_City_Japanese), result.final_text

# ################################################################################################################################

    def test_the_session_cap_holds_under_live_agents(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Sessions)

        # The cap fills with sessions, the first of which keeps a conversation going ..
        first_session_id = _helpers.open_session(client)
        session_ids = [first_session_id]

        for _ in range(_constants.Session_Cap - 1):
            session_ids.append(_helpers.open_session(client))

        # .. the next initialize is refused ..
        response = _helpers.initialize_response(client)
        body = response.json()
        assert 'error' in body, body

        # .. conversations on existing sessions keep working ..
        body = _helpers.call_tool(client, first_session_id, _constants.Service_Order_Status,
            {'order_id': _constants.Order_ID})

        data = _helpers.get_result_data(body)
        assert data['status'] == _constants.Order_Status, body

        # .. and deleting one session frees room immediately.
        delete_response = client.delete_session(session_ids[-1])
        assert delete_response.ok, delete_response.text

        session_ids[-1] = _helpers.open_session(client)

        # The gateway goes back to its idle state for the other tests.
        for session_id in session_ids:
            _ = client.delete_session(session_id)

# ################################################################################################################################

    def test_idle_sessions_expire_live(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_TTL)

        # A session used within its TTL keeps working ..
        session_id = _helpers.open_session(client)

        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status,
            {'order_id': _constants.Order_ID})

        data = _helpers.get_result_data(body)
        assert data['status'] == _constants.Order_Status, body

        # .. one left idle past the TTL is refused on its next call ..
        time.sleep(_past_ttl_seconds)

        response = client.jsonrpc('tools/list', session_id=session_id)
        assert response.status_code != OK, response.text

        # .. and the reaper's sweep is what removes an idle session from the store -
        # the server reports the removal, and a DELETE finds nothing left.
        swept_session_id = _helpers.open_session(client)

        server_log_path = zato_server['server_log_path']
        log_offset = os.path.getsize(server_log_path)

        time.sleep(_past_sweep_seconds)

        with open(server_log_path) as server_log:
            _ = server_log.seek(log_offset)
            new_log_text = server_log.read()

        assert _reaper_log_marker in new_log_text, new_log_text
        assert _constants.Gateway_TTL in new_log_text, new_log_text

        delete_response = client.delete_session(swept_session_id)
        assert delete_response.status_code == NOT_FOUND, delete_response.text

# ################################################################################################################################
# ################################################################################################################################
