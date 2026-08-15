# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# local
import _agent
import _audit
import _constants
import _helpers

# Zato
from zato.common.audit_log.api import AuditEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The argument the enabled gateway adds to every tool's schema
_filter_key = 'response_filter'

# The expression the tests project invoice totals with
_totals_expression = 'invoices.total'

# What a final answer sounds like when the model reports that something did not work
_failure_words = ('cannot', 'could not', "couldn't", 'unable', 'fail', 'error', 'not possible')

# ################################################################################################################################
# ################################################################################################################################

class TestClientFilterAdvertisement:
    """ The response_filter argument is advertised on every tool of the enabled gateway
    and on none of a disabled one.
    """

# ################################################################################################################################

    def test_every_tool_of_the_enabled_gateway_advertises_the_filter(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Filters)
        session_id = _helpers.open_session(client)

        tools = _helpers.list_tools(client, session_id)
        assert tools, tools

        for tool in tools:
            properties = tool['inputSchema']['properties']
            assert _filter_key in properties, tool

            # The filter is never required - it stays the caller's own choice
            required = tool['inputSchema']['required']
            assert _filter_key not in required, tool

# ################################################################################################################################

    def test_no_tool_of_a_disabled_gateway_advertises_the_filter(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        tools = _helpers.list_tools(client, session_id)
        assert tools, tools

        for tool in tools:
            properties = tool['inputSchema']['properties']
            assert _filter_key not in properties, tool

# ################################################################################################################################
# ################################################################################################################################

class TestClientFilterApplication:
    """ A filter reshapes the response on the way out, an invalid one is the caller's error,
    and a disabled gateway knows nothing of the argument at all.
    """

# ################################################################################################################################

    def test_a_valid_filter_reshapes_the_response_and_is_traced(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Filters)
        session_id = _helpers.open_session(client)

        arguments = {'count': '3', _filter_key: _totals_expression}
        body = _helpers.call_tool(client, session_id, _constants.Service_Invoice_List, arguments)

        # The result is the projection, not the whole document ..
        data = _helpers.get_result_data(body)
        assert data == [101, 102, 103], data

        # .. and the audit event records the expression that was applied.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Filters,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event_data = events[-1]['data']
        assert event_data['client_filter'] == _totals_expression, event_data

# ################################################################################################################################

    def test_an_invalid_expression_is_invalid_params(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Filters)
        session_id = _helpers.open_session(client)

        arguments = {'count': '3', _filter_key: 'this ( is not JSONata ]'}
        body = _helpers.call_tool(client, session_id, _constants.Service_Invoice_List, arguments)

        assert body['error']['code'] == _constants.Error_Invalid_Params, body

# ################################################################################################################################

    def test_the_disabled_gateway_refuses_the_argument_under_validation(self, zato_server:'anydict') -> 'None':

        # The validating gateway has client filters off, so the argument is simply unknown there
        client = _helpers.make_client(zato_server, _constants.Path_Validate)
        session_id = _helpers.open_session(client)

        arguments = {'count': '3', _filter_key: _totals_expression}
        body = _helpers.call_tool(client, session_id, _constants.Service_Invoice_List, arguments)

        assert body['error']['code'] == _constants.Error_Invalid_Params, body
        assert _filter_key in body['error']['message'], body

# ################################################################################################################################
# ################################################################################################################################

class TestClientFiltersWithLLM:
    """ The model, told the tools accept a JSONata response filter, uses one on its own -
    and reports an error it caused with a broken one.
    """

# ################################################################################################################################

    def test_llm_passes_a_filter_and_gets_the_filtered_shape(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Filters)

        system_text = (
            'Every tool accepts an optional response_filter argument - a JSONata expression '
            'applied to the tool response before it is returned. When only part of a response '
            'is needed, pass a response_filter instead of reading the whole document. '
            f'For example, to get only invoice totals, pass response_filter set to "{_totals_expression}".')

        task = 'What are the totals of the last 3 invoices? Give me just the amounts.'

        result = _agent.run_agent(client, task, system_text=system_text)

        # The transcript shows the filter travelling with the call ..
        filtered_calls = []

        for call in result.tool_calls:
            if call.tool_name == _constants.Service_Invoice_List:
                if _filter_key in call.arguments:
                    filtered_calls.append(call)

        assert filtered_calls, result.messages

        # .. the tool result the model saw is the filtered shape ..
        filtered_shape = loads(filtered_calls[0].result_text)
        assert filtered_shape == [101, 102, 103], filtered_calls[0].result_text

        # .. the answer names the totals ..
        assert '101' in result.final_text, result.final_text
        assert '102' in result.final_text, result.final_text
        assert '103' in result.final_text, result.final_text

        # .. and the audit data records the filter that was applied.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Filters,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        traced_filters = []

        for event in events:
            if 'client_filter' in event['data']:
                traced_filters.append(event['data']['client_filter'])

        assert traced_filters, events

# ################################################################################################################################

    def test_llm_reports_an_error_from_a_broken_filter(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Filters)

        # The model's own filter is replaced with a broken one on the way to the gateway,
        # so the invalid-params error genuinely reaches the model.
        state = {'was_broken': False}

        def break_the_filter(tool_name:'str', arguments:'anydict') -> 'anydict':

            if tool_name == _constants.Service_Invoice_List:
                if not state['was_broken']:
                    state['was_broken'] = True
                    arguments = dict(arguments)
                    arguments[_filter_key] = 'this ( is not JSONata ]'

            return arguments

        system_text = (
            'Every tool accepts an optional response_filter argument - a JSONata expression '
            'applied to the tool response before it is returned.')

        task = (
            'What are the totals of the last 3 invoices? If a tool call fails, '
            'you may retry once without a response_filter, and if it still fails, say so plainly.')

        result = _agent.run_agent(client, task, system_text=system_text, transform_arguments=break_the_filter)

        # The broken filter genuinely went out and came back as an error the model saw
        assert state['was_broken'], result.messages

        error_calls = []
        success_calls = []

        for call in result.tool_calls:
            if call.is_error:
                error_calls.append(call)
            else:
                success_calls.append(call)

        assert error_calls, result.messages
        assert _filter_key in error_calls[0].result_text, error_calls[0].result_text

        # The model either retried and answered from the real totals, or reported the failure.
        if success_calls:
            assert '101' in result.final_text, result.final_text
        else:
            assert _helpers.contains_any_word(result.final_text, _failure_words), result.final_text

# ################################################################################################################################
# ################################################################################################################################
