# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

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

# How many invoices make a response that goes over the token cap under the default ratio
_oversized_count = '200'

# What a final answer sounds like when the model reports that something did not work
_failure_words = ('too large', 'cannot', 'could not', "couldn't", 'unable', 'fail', 'error', 'not possible')

# ################################################################################################################################
# ################################################################################################################################

def _contains_failure_word(text:'str') -> 'bool':
    """ Whether the text reports a failure in any of the usual wordings.
    """

    out = _helpers.contains_any_word(text, _failure_words)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestResponseShaping:
    """ The token cap cuts or refuses oversized responses per its mode, the activation
    threshold turns it off for small responses, and the character-per-token ratio
    moves the estimate across the cap boundary.
    """

# ################################################################################################################################

    def test_truncate_mode_cuts_and_traces(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Shaping_Truncate)
        session_id = _helpers.open_session(client)

        body = _helpers.call_tool(client, session_id, _constants.Service_Invoice_List, {'count': _oversized_count})

        # The response came back cut, not refused ..
        result = body['result']
        assert 'isError' not in result, result

        data = _helpers.get_result_data(body)
        assert len(data['invoices']) < int(_oversized_count), len(data['invoices'])

        # .. and the audit trace names both sides of the cut.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Shaping_Truncate,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event_data = events[-1]['data']

        assert event_data['was_truncated'] is True, event_data
        assert event_data['tokens_before'] > _constants.Shaping_Cap_Tokens, event_data
        assert event_data['tokens_after'] <= _constants.Shaping_Cap_Tokens, event_data

# ################################################################################################################################

    def test_a_response_under_the_threshold_passes_untouched(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        # The same cap is set here, but the activation threshold is far above
        # anything the service returns, so the cap never runs.
        client = _helpers.make_client(zato_server, _constants.Path_Shaping_Threshold)
        session_id = _helpers.open_session(client)

        body = _helpers.call_tool(client, session_id, _constants.Service_Invoice_List, {'count': _oversized_count})

        data = _helpers.get_result_data(body)
        assert len(data['invoices']) == int(_oversized_count), len(data['invoices'])

        # No shaping happened, so the audit event carries no shaping keys at all.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Shaping_Threshold,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event_data = events[-1]['data']

        assert 'was_truncated' not in event_data, event_data
        assert 'tokens_before' not in event_data, event_data
        assert 'reject_kind' not in event_data, event_data

# ################################################################################################################################

    def test_the_ratio_moves_the_estimate_across_the_cap(self, zato_server:'anydict') -> 'None':

        arguments = {'count': _oversized_count}

        # Under the wide ratio, the same payload measures as a handful of tokens and passes ..
        wide_client = _helpers.make_client(zato_server, _constants.Path_Shaping_Wide)
        wide_session = _helpers.open_session(wide_client)

        body = _helpers.call_tool(wide_client, wide_session, _constants.Service_Invoice_List, arguments)

        data = _helpers.get_result_data(body)
        assert len(data['invoices']) == int(_oversized_count), len(data['invoices'])

        # .. and under the narrow ratio, it measures as thousands of tokens and truncates.
        narrow_client = _helpers.make_client(zato_server, _constants.Path_Shaping_Narrow)
        narrow_session = _helpers.open_session(narrow_client)

        body = _helpers.call_tool(narrow_client, narrow_session, _constants.Service_Invoice_List, arguments)

        data = _helpers.get_result_data(body)
        assert len(data['invoices']) < int(_oversized_count), len(data['invoices'])

# ################################################################################################################################
# ################################################################################################################################

class TestBlockModeWithLLM:
    """ Block mode refuses an oversized response outright and the model reports
    that instead of inventing the data it never received.
    """

# ################################################################################################################################

    def test_blocked_response_is_reported_not_invented(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Shaping_Block)

        # The invoice tool takes only a count, so the task names no customer.
        task = (
            f'Use the invoice tool to list the last {_oversized_count} invoices '
            'and report their invoice numbers. If the tools cannot give you the data, say so plainly.')

        result = _agent.run_agent(client, task)

        # The gateway refused at least one invoice listing ..
        blocked_calls = []

        for call in result.tool_calls:
            if call.tool_name == _constants.Service_Invoice_List:
                if call.is_error:
                    blocked_calls.append(call)

        assert blocked_calls, result.messages
        assert 'too large' in blocked_calls[0].result_text.lower(), blocked_calls[0].result_text

        # .. the model reported the failure ..
        assert _contains_failure_word(result.final_text), result.final_text

        # .. and every invoice number its answer mentions came out of a call that actually
        # succeeded - nothing in the answer was made up to cover for the refusal.
        received_text = ''

        for call in result.tool_calls:
            if not call.is_error:
                received_text += call.result_text

        mentioned_invoices = re.findall(r'INV-2026-\d+', result.final_text)

        for invoice_id in mentioned_invoices:
            assert invoice_id in received_text, (invoice_id, result.final_text)

        # .. and the refusal is audited with its measured size and an error outcome.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Shaping_Block,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        blocked_events = []

        for event in events:
            if event['data'].get('reject_kind') == 'size':
                blocked_events.append(event)

        assert blocked_events, events

        event = blocked_events[0]
        assert event['outcome'] == AuditOutcome.Error, event
        assert event['data']['tokens_before'] > _constants.Shaping_Cap_Tokens, event['data']

# ################################################################################################################################
# ################################################################################################################################
