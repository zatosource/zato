# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from concurrent.futures import ThreadPoolExecutor
from http.client import BAD_REQUEST, NOT_FOUND, OK

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
        assert _constants.Customer_Name in result_one.final_text, result_one.final_text
        assert _constants.Order_Status in result_two.final_text, result_two.final_text

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
