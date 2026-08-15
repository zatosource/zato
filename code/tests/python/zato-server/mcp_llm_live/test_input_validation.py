# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# local
import _agent
import _audit
import _constants
import _enmasse
import _helpers
import _markers
from _helpers import wait_until as _wait_until

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# What a final answer sounds like when the model reports that something did not work
_failure_words = ('cannot', 'could not', "couldn't", 'unable', 'fail', 'error', 'not possible', 'was not', 'no result')

# An argument no schema of the suite declares, with a value a caller could plausibly send
_unknown_key   = 'delivery_notes'
_unknown_value = 'Leave at the front desk'

# The format the report service falls back to when the caller names none
_default_report_format = 'summary'

# ################################################################################################################################
# ################################################################################################################################

def _contains_failure_word(text:'str') -> 'bool':
    """ Whether the text reports a failure in any of the usual wordings.
    """

    out = _helpers.contains_any_word(text, _failure_words)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _call_customer(zato_server:'anydict', url_path:'str', arguments:'anydict') -> 'anydict':
    """ One customer call through the given gateway on a fresh session,
    returning the whole response body.
    """

    client = _helpers.make_client(zato_server, url_path)
    session_id = _helpers.open_session(client)

    out = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get, arguments)
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

        # The main gateway has validation off, so a wrong-type call reaches the service
        # and the service itself runs. A missing required field would still be refused
        # by the service's own input contract.
        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        _ = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get, {'customer_id': 123})

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
        assert _helpers.text_contains(result.final_text, _constants.Customer_Name), result.final_text

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
            assert _helpers.text_contains(result.final_text, _constants.Customer_Name), result.final_text
        else:
            assert not _helpers.text_contains(result.final_text, _constants.Customer_Name), result.final_text
            assert _contains_failure_word(result.final_text), result.final_text

# ################################################################################################################################

    def test_llm_reports_a_service_error(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        task = (
            f'Cancel order {_constants.Order_ID_Not_Cancellable} for me. If it does not work, '
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

# ################################################################################################################################
# ################################################################################################################################

class TestValidationOptions:
    """ Input validation beyond the missing field and the wrong type - unknown parameters,
    the same calls with validation off, optional fields and the live toggle.
    """

# ################################################################################################################################

    def test_an_unknown_parameter_is_refused(self, zato_server:'anydict') -> 'None':

        marker_path = zato_server['marker_path']
        audit_db_path = zato_server['audit_db_path']

        count_before = _markers.count_invocations(marker_path, _constants.Service_Customer_Get)
        min_id = _audit.last_event_id(audit_db_path)

        # A call with a field the schema does not declare is invalid params, naming the field ..
        arguments = {'customer_id': _constants.Customer_ID, _unknown_key: _unknown_value}
        body = _call_customer(zato_server, _constants.Path_Validate, arguments)

        assert body['error']['code'] == _constants.Error_Invalid_Params, body
        assert _unknown_key in body['error']['message'], body

        # .. audited as an error ..
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

    def test_the_same_calls_with_validation_off(self, zato_server:'anydict') -> 'None':

        marker_path = zato_server['marker_path']
        audit_db_path = zato_server['audit_db_path']

        # The unknown-parameter call reaches the service with the extra argument intact ..
        count_before = _markers.count_invocations(marker_path, _constants.Service_Customer_Get)

        arguments = {'customer_id': _constants.Customer_ID, _unknown_key: _unknown_value}
        body = _call_customer(zato_server, _constants.Path_Main, arguments)

        data = _helpers.get_result_data(body)
        assert data['name'] == _constants.Customer_Name, body

        count_after = _markers.count_invocations(marker_path, _constants.Service_Customer_Get)
        assert count_after == count_before + 1, (count_before, count_after)

        # .. while the missing-field call fails under the service's own input contract -
        # a service error, not a validation one ..
        min_id = _audit.last_event_id(audit_db_path)

        body = _call_customer(zato_server, _constants.Path_Main, {})

        result = body['result']
        assert result['isError'] is True, body

        # .. and the audit records the difference - an error outcome with no
        # JSON-RPC error code, unlike a validation refusal.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event
        assert 'error_code' not in event['data'], event

# ################################################################################################################################

    def test_optional_fields_pass_by_omission(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Validate)
        session_id = _helpers.open_session(client)

        # The call omits the optional format field and passes validation ..
        arguments = {'customer_id': _constants.Customer_ID}
        body = _helpers.call_tool(client, session_id, _constants.Service_Report_Build, arguments)

        # .. and the service saw its own declared default.
        data = _helpers.get_result_data(body)

        assert data['customer_id'] == _constants.Customer_ID, body
        assert data['format'] == _default_report_format, body

# ################################################################################################################################

    def test_the_toggle_is_live(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        # The missing-field call is refused while validation is on ..
        body = _call_customer(zato_server, _constants.Path_Validate, {})
        assert body['error']['code'] == _constants.Error_Invalid_Params, body

        try:
            # .. one re-import turns validation off and the same call
            # now reaches the service, failing under its own contract ..
            overrides = {_constants.Gateway_Validate: {'validate_input': False}}
            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            def call_reaches_the_service() -> 'bool':
                body = _call_customer(zato_server, _constants.Path_Validate, {})

                if 'error' in body:
                    return False

                out = 'isError' in body['result']
                return out

            _wait_until(call_reaches_the_service, 'validation off reached enforcement')

        finally:
            # .. and turning it back on refuses the call again - both ways, no restart.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def call_is_refused() -> 'bool':
                body = _call_customer(zato_server, _constants.Path_Validate, {})

                if 'error' not in body:
                    return False

                out = body['error']['code'] == _constants.Error_Invalid_Params
                return out

            _wait_until(call_is_refused, 'validation on came back')

# ################################################################################################################################
# ################################################################################################################################

class TestNameRenderingInErrors:
    """ Tool and argument names from the request render as single lines in error messages
    and in the log - the audit log is the one place that keeps the raw value.
    """

# ################################################################################################################################

    def test_a_tool_name_with_line_breaks_is_reported_on_one_line(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        # The tool name carries line breaks and a distinctive trailer ..
        trailer = 'crm.note.' + rand_string()
        tool_name = f'crm.orders\r\n{trailer}'

        body = _helpers.call_tool(client, session_id, tool_name, {})

        assert body['error']['code'] == _constants.Error_Method_Not_Found, body

        # .. the error names the tool on one line - the line breaks became spaces ..
        message = body['error']['message']

        assert '\r' not in message, body
        assert '\n' not in message, body
        assert trailer in message, body

        # .. and the audit event keeps the name exactly as it was sent.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event
        assert event['endpoint'] == tool_name, event

# ################################################################################################################################

    def test_an_argument_name_with_line_breaks_is_reported_on_one_line(self, zato_server:'anydict') -> 'None':

        server_log_path = zato_server['server_log_path']

        client = _helpers.make_client(zato_server, _constants.Path_Validate)
        session_id = _helpers.open_session(client)

        log_offset = os.path.getsize(server_log_path)

        # The unknown argument's name carries line breaks and a distinctive trailer ..
        trailer = 'crm.note.' + rand_string()
        argument_name = f'delivery_notes\r\n{trailer}'

        arguments = {'customer_id': _constants.Customer_ID, argument_name: _unknown_value}
        body = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get, arguments)

        assert body['error']['code'] == _constants.Error_Invalid_Params, body

        # .. the error names the argument on one line ..
        message = body['error']['message']

        assert 'Unknown parameter' in message, body
        assert '\r' not in message, body
        assert '\n' not in message, body
        assert trailer in message, body

        # .. and in the server log the name sits inside the refusal's own line -
        # the trailer never opens a line of its own.
        new_log_text = _helpers.read_new_log_text(server_log_path, log_offset)
        assert trailer in new_log_text, new_log_text

        for line in new_log_text.splitlines():
            if trailer in line:
                assert 'Invalid arguments' in line, line

# ################################################################################################################################
# ################################################################################################################################
