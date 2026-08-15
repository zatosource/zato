# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from concurrent.futures import ThreadPoolExecutor

# local
import _agent
import _audit
import _constants
import _diag
import _helpers
from _client_stateless import MCPStatelessClient

# Zato
from zato.common.audit_log.api import AuditEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The task both revisions answer - the customer's city is the grounded fact of the answer
_task = f'What city does customer {_constants.Customer_ID} live in?'

# ################################################################################################################################
# ################################################################################################################################

def _make_stateless_client(zato_server:'anydict') -> 'MCPStatelessClient':

    mcp_url = zato_server['mcp_url'](_constants.Path_Main)

    out = MCPStatelessClient(mcp_url, auth=zato_server['basic_auth'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestStatelessLLM:
    """ The agent itself drives the stateless revision - whole conversations
    with no sessions anywhere, next to session-based ones on the same gateway.
    """

# ################################################################################################################################

    def test_a_whole_conversation_no_sessions(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _make_stateless_client(zato_server)
        result = _agent.run_agent_stateless(client, _task)

        # The conversation called the customer tool and answered with the city ..
        first_call = result.tool_calls[0]
        assert first_call.tool_name == _constants.Service_Customer_Get, result.tool_calls
        assert _helpers.text_contains(result.final_text, _constants.Customer_City), result.final_text

        # .. every wire request carried the stateless headers and no session header anywhere ..
        wire_requests = _diag.get_entries('mcp_request')
        assert wire_requests, 'No MCP requests were logged'

        for entry in wire_requests:
            headers = entry['payload']['headers']

            assert 'Mcp-Method' in headers, entry
            assert headers['MCP-Protocol-Version'] == _constants.Protocol_Version_Stateless, entry
            assert 'Mcp-Session-Id' not in headers, entry

        # .. and the tools/call requests named their tool in the Mcp-Name header.
        for entry in wire_requests:
            payload = entry['payload']

            if payload['body']['method'] == 'tools/call':
                assert payload['headers']['Mcp-Name'] == _constants.Service_Customer_Get, entry

        # A session-based run of the same task lands on the same grounded fact.
        session_client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_result = _agent.run_agent(session_client, _task)

        assert _helpers.text_contains(session_result.final_text, _constants.Customer_City), session_result.final_text

# ################################################################################################################################

    def test_stateless_and_session_callers_share_a_gateway(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        stateless_client = _make_stateless_client(zato_server)
        session_client = _helpers.make_client(zato_server, _constants.Path_Main)

        # Both conversations run against the same gateway at the same time ..
        with ThreadPoolExecutor(max_workers=2) as executor:

            stateless_future = executor.submit(_agent.run_agent_stateless, stateless_client, _task)
            session_future = executor.submit(_agent.run_agent, session_client, _task)

            stateless_result = stateless_future.result()
            session_result = session_future.result()

        # .. both complete with the same grounded fact ..
        assert _helpers.text_contains(stateless_result.final_text, _constants.Customer_City), stateless_result.final_text
        assert _helpers.text_contains(session_result.final_text, _constants.Customer_City), session_result.final_text

        # .. and the audit tells them apart by the session key - the session-based
        # calls carry theirs, the stateless ones carry none.
        expected_count = len(stateless_result.tool_calls) + len(session_result.tool_calls)

        events = _audit.wait_for_events(
            audit_db_path, expected_count,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        session_keys = []
        stateless_count = 0

        for event in events:

            if event['sub_key']:
                session_keys.append(event['sub_key'])
            else:
                stateless_count += 1

        assert session_keys == [session_result.session_id] * len(session_result.tool_calls), events
        assert stateless_count == len(stateless_result.tool_calls), events

# ################################################################################################################################

    def test_discovery_is_a_sufficient_tool_source(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _make_stateless_client(zato_server)
        result = _agent.run_agent_stateless(client, _task, tools_from_discover=True)

        # The tool list came from server/discover alone - the wire log has no tools/list anywhere ..
        wire_requests = _diag.get_entries('mcp_request')
        methods = []

        for entry in wire_requests:
            methods.append(entry['payload']['body']['method'])

        assert 'server/discover' in methods, methods
        assert 'tools/list' not in methods, methods

        # .. and the discovered tools carried the conversation to the same calls and the same answer.
        first_call = result.tool_calls[0]
        assert first_call.tool_name == _constants.Service_Customer_Get, result.tool_calls
        assert first_call.arguments == {'customer_id': _constants.Customer_ID}, result.tool_calls

        assert _helpers.text_contains(result.final_text, _constants.Customer_City), result.final_text

# ################################################################################################################################
# ################################################################################################################################
