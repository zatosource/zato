# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import FORBIDDEN

# local
import _agent
import _audit
import _constants
import _helpers

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# How many invoices make a response the block-mode gateway refuses
_oversized_count = '200'

# ################################################################################################################################
# ################################################################################################################################

class TestAuditCompleteness:
    """ One full conversation produces the complete event set and every kind of failure
    lands with an error outcome.
    """

# ################################################################################################################################

    def test_one_conversation_produces_the_complete_event_set(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Skills)

        task = f'What is the name of customer {_constants.Customer_ID}? Use the tools.'

        result = _agent.run_agent(client, task)
        assert result.tool_calls, result.messages

        # The host also reads the gateway's prompts within the same session,
        # the way a real host discovers the skills it may use
        session_id = result.session_id

        _ = client.jsonrpc('prompts/list', session_id=session_id)

        params = {'name': _constants.Skill_House_Style}
        _ = client.jsonrpc('prompts/get', params=params, session_id=session_id)

        # The whole conversation is initialize, tools/list, every tools/call and both prompt reads
        expected_count = 4 + len(result.tool_calls)

        _ = _audit.wait_for_events(
            audit_db_path, expected_count, object_name=_constants.Gateway_Skills, min_id=min_id)

        all_events = _audit.read_events(audit_db_path, object_name=_constants.Gateway_Skills, min_id=min_id)

        # Only this conversation's session matters - other tests may run around this one
        events = []

        for event in all_events:
            if event['sub_key'] == session_id:
                events.append(event)

        event_types = []

        for event in events:
            event_types.append(event['event_type'])

        # The event set is complete and in order
        expected_types = [
            AuditEvent.MCP_Initialize,
            AuditEvent.MCP_Tools_List,
        ]

        for _call in result.tool_calls:
            expected_types.append(AuditEvent.MCP_Tools_Call)

        expected_types.append(AuditEvent.MCP_Prompts_List)
        expected_types.append(AuditEvent.MCP_Prompts_Get)

        assert event_types == expected_types, (event_types, expected_types)

        # Every event carries a unique CID, a size, a duration and the right outcome
        cids = set()

        for event in events:

            assert event['cid'], event
            cids.add(event['cid'])

            assert event['size'] > 0, event
            assert event['data']['duration_ms'] >= 0, event
            assert event['outcome'] == AuditOutcome.OK, event
            assert event['ext_client_id'] == _constants.Sec_Basic, event

        assert len(cids) == len(events), (cids, events)

# ################################################################################################################################

    def test_every_kind_of_failure_lands_with_an_error_outcome(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']

        # Bad credentials on the main gateway ..
        min_id = _audit.last_event_id(audit_db_path)

        username, password = zato_server['basic_auth']
        wrong_auth = (username, 'wrong-' + password)
        rejected_client = _helpers.make_client(zato_server, _constants.Path_Main, auth=wrong_auth)

        response = _helpers.initialize_response(rejected_client)
        assert response.status_code == FORBIDDEN, response.text

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.Auth_Failed,
            min_id=min_id)

        assert events[-1]['outcome'] == AuditOutcome.Error, events

        # .. invalid params on the validating gateway ..
        min_id = _audit.last_event_id(audit_db_path)

        validate_client = _helpers.make_client(zato_server, _constants.Path_Validate)
        validate_session = _helpers.open_session(validate_client)

        body = _helpers.call_tool(validate_client, validate_session, _constants.Service_Customer_Get, {})
        assert body['error']['code'] == _constants.Error_Invalid_Params, body

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Validate,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        assert events[-1]['outcome'] == AuditOutcome.Error, events

        # .. a service exception on the main gateway ..
        min_id = _audit.last_event_id(audit_db_path)

        main_client = _helpers.make_client(zato_server, _constants.Path_Main)
        main_session = _helpers.open_session(main_client)

        body = _helpers.call_tool(main_client, main_session, _constants.Service_Order_Cancel,
            {'order_id': _constants.Order_ID_Broken})
        assert body['result']['isError'] is True, body

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        assert events[-1]['outcome'] == AuditOutcome.Error, events

        # .. and a blocked response on the block-mode gateway.
        min_id = _audit.last_event_id(audit_db_path)

        block_client = _helpers.make_client(zato_server, _constants.Path_Shaping_Block)
        block_session = _helpers.open_session(block_client)

        body = _helpers.call_tool(block_client, block_session, _constants.Service_Invoice_List,
            {'count': _oversized_count})
        assert body['result']['isError'] is True, body

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Shaping_Block,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event
        assert event['data']['reject_kind'] == 'size', event['data']

# ################################################################################################################################
# ################################################################################################################################
