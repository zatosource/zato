# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
import _agent
import _audit
import _constants
import _helpers
import _markers

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# What a final answer sounds like when the model reports that something did not work
_failure_words = ('cannot', 'could not', "couldn't", 'unable', 'fail', 'error', 'not possible', 'was not', 'no result')

# ################################################################################################################################
# ################################################################################################################################

def _contains_failure_word(text:'str') -> 'bool':
    """ Whether the text reports a failure in any of the usual wordings.
    """

    text = text.lower()

    for word in _failure_words:
        if word in text:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestInputValidation:
    """ A gateway with input validation on refuses arguments that do not match the tool's
    schema before the service ever runs - and one with validation off passes them through.
    """

# ################################################################################################################################

    def test_missing_required_field_is_refused_before_the_service_runs(self, zato_server:'anydict') -> 'None':

        marker_path = zato_server['marker_path']
        audit_db_path = zato_server['audit_db_path']

        count_before = _markers.count_invocations(marker_path, _constants.Service_Customer_Get)
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Validate)
        session_id = _helpers.open_session(client)

        # A call without the required field is invalid params ..
        body = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get, {})

        assert body['error']['code'] == _constants.Error_Invalid_Params, body
        assert 'customer_id' in body['error']['message'], body

        # .. the audit outcome is an error ..
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Validate,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        assert events[-1]['outcome'] == AuditOutcome.Error, events

        # .. and the service never ran.
        count_after = _markers.count_invocations(marker_path, _constants.Service_Customer_Get)
        assert count_after == count_before, (count_before, count_after)

# ################################################################################################################################

    def test_wrong_type_is_refused_before_the_service_runs(self, zato_server:'anydict') -> 'None':

        marker_path = zato_server['marker_path']

        count_before = _markers.count_invocations(marker_path, _constants.Service_Customer_Get)

        client = _helpers.make_client(zato_server, _constants.Path_Validate)
        session_id = _helpers.open_session(client)

        # The schema says the field is a string, so a number is invalid params ..
        body = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get, {'customer_id': 123})

        assert body['error']['code'] == _constants.Error_Invalid_Params, body

        # .. and the service never ran.
        count_after = _markers.count_invocations(marker_path, _constants.Service_Customer_Get)
        assert count_after == count_before, (count_before, count_after)

# ################################################################################################################################

    def test_the_same_bad_call_reaches_the_service_without_validation(self, zato_server:'anydict') -> 'None':

        marker_path = zato_server['marker_path']

        count_before = _markers.count_invocations(marker_path, _constants.Service_Customer_Get)

        # The main gateway has validation off, so the same call goes through to the service.
        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        _ = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get, {})

        count_after = _markers.count_invocations(marker_path, _constants.Service_Customer_Get)
        assert count_after == count_before + 1, (count_before, count_after)

# ################################################################################################################################

    def test_unknown_tool_returns_the_proper_error_and_is_audited(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        unknown_tool = 'crm.no.such.tool'
        body = _helpers.call_tool(client, session_id, unknown_tool, {})

        assert body['error']['code'] == _constants.Error_Method_Not_Found, body

        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event
        assert event['endpoint'] == unknown_tool, event

# ################################################################################################################################
# ################################################################################################################################

class TestValidationWithLLM:
    """ The model's own arguments pass validation and, when the gateway does refuse a call,
    the model reacts to the error instead of making a result up.
    """

# ################################################################################################################################

    def test_llm_arguments_pass_validation(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Validate)

        task = f'What is the name of customer {_constants.Customer_ID}? Use the tools to find out.'

        result = _agent.run_agent(client, task)

        # The model called the tool and no call was refused for invalid arguments ..
        assert result.tool_calls, result.messages

        for call in result.tool_calls:
            assert not call.is_error, (call.tool_name, call.arguments, call.result_text)

        # .. and the answer carries what the service returned.
        assert _constants.Customer_Name in result.final_text, result.final_text

# ################################################################################################################################

    def test_llm_reacts_to_invalid_params_instead_of_fabricating(
        self,
        zato_server:'anydict',
        ollama:'anydict',
        ) -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Validate)

        # The first customer call loses its required field on the way to the gateway,
        # so the model genuinely receives an invalid-params error mid-conversation.
        state = {'was_dropped': False}

        def drop_first_customer_field(tool_name:'str', arguments:'anydict') -> 'anydict':

            if tool_name == _constants.Service_Customer_Get:
                if not state['was_dropped']:
                    state['was_dropped'] = True
                    return {}

            return arguments

        task = f'What is the name of customer {_constants.Customer_ID}? Use the tools to find out.'

        result = _agent.run_agent(client, task, transform_arguments=drop_first_customer_field)

        # The error genuinely reached the model ..
        assert state['was_dropped'], result.messages

        error_calls = []
        success_calls = []

        for call in result.tool_calls:
            if call.tool_name == _constants.Service_Customer_Get:
                if call.is_error:
                    error_calls.append(call)
                else:
                    success_calls.append(call)

        assert error_calls, result.messages

        # .. and the model either retried with correct arguments and answered from the real
        # result, or reported the failure - what it never does is invent the customer's name.
        if success_calls:
            assert _constants.Customer_Name in result.final_text, result.final_text
        else:
            assert _constants.Customer_Name not in result.final_text, result.final_text
            assert _contains_failure_word(result.final_text), result.final_text

# ################################################################################################################################

    def test_llm_reports_a_service_error(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        task = (
            f'Cancel order {_constants.Order_ID_Broken} for me. If it does not work, '
            'say so plainly and do not pretend it worked.')

        result = _agent.run_agent(client, task)

        # The cancel tool ran and reported an error ..
        cancel_calls = []

        for call in result.tool_calls:
            if call.tool_name == _constants.Service_Order_Cancel:
                cancel_calls.append(call)

        assert cancel_calls, result.messages
        assert cancel_calls[0].is_error, cancel_calls[0].result_text

        # .. the model reported the failure instead of claiming success ..
        assert _contains_failure_word(result.final_text), result.final_text

        # .. and the audit log has the error outcome for the call - all of this
        # conversation's calls have landed once their count matches the transcript.
        events = _audit.wait_for_events(
            audit_db_path, len(result.tool_calls),
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        cancel_events = []

        for event in events:
            if event['endpoint'] == _constants.Service_Order_Cancel:
                cancel_events.append(event)

        assert cancel_events, events
        assert cancel_events[0]['outcome'] == AuditOutcome.Error, cancel_events
