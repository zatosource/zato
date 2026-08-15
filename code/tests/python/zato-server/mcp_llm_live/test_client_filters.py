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
from _client_stateless import MCPStatelessClient

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.util.message_filters.common import Max_Expression_Length

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _client import MCPClient
    from zato.common.typing_ import anydict

    MCPClient = MCPClient

# ################################################################################################################################
# ################################################################################################################################

# The argument the enabled gateway adds to every tool's schema
_filter_key = 'response_filter'

# The expression the tests project invoice totals with
_totals_expression = 'invoices.total'

# What a final answer sounds like when the model reports that something did not work
_failure_words = ('cannot', 'could not', "couldn't", 'unable', 'fail', 'error', 'not possible')

# How many invoices the language tests ask for - the totals run 101 through 105
_invoice_count = '5'

# The three faces of the language - a predicate, an aggregation and an object construction
_expression_predicate = 'invoices[total > 103].invoice_id'
_expression_aggregation = '$sum(invoices.total)'
_expression_object = '{"first": invoices[0].invoice_id, "how_many": count}'

# An expression that matches nothing in the invoice document
_expression_no_match = 'invoices[total > 999]'

# A syntactically valid expression that fails at evaluation - an invoice id is no number
_expression_evaluation_error = '$number(invoices[0].invoice_id)'

# A well-formed expression padded past the engine's length cap
_expression_too_long = 'invoices.total' + ' ' * Max_Expression_Length

# ################################################################################################################################
# ################################################################################################################################

def _call_invoices(client:'MCPClient', session_id:'str', expression:'str') -> 'anydict':
    """ One invoice listing through the filters gateway with the given expression attached.
    """

    arguments = {'count': _invoice_count, _filter_key: expression}

    out = _helpers.call_tool(client, session_id, _constants.Service_Invoice_List, arguments)
    return out

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

        arguments = {'count': '3', _filter_key: 'invoices[total >'}
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
    and reports an error it caused with an invalid one.
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

    def test_llm_reports_an_error_from_an_invalid_filter(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Filters)

        # The model's own filter is replaced with an invalid one on the way to the gateway,
        # so the invalid-params error genuinely reaches the model.
        state = {'was_replaced': False}

        def replace_with_invalid_filter(tool_name:'str', arguments:'anydict') -> 'anydict':

            if tool_name == _constants.Service_Invoice_List:
                if not state['was_replaced']:
                    state['was_replaced'] = True
                    arguments = dict(arguments)
                    arguments[_filter_key] = 'invoices[total >'

            return arguments

        system_text = (
            'Every tool accepts an optional response_filter argument - a JSONata expression '
            'applied to the tool response before it is returned.')

        task = (
            'What are the totals of the last 3 invoices? If a tool call fails, '
            'you may retry once without a response_filter, and if it still fails, say so plainly.')

        result = _agent.run_agent(client, task, system_text=system_text, transform_arguments=replace_with_invalid_filter)

        # The invalid filter genuinely went out and came back as an error the model saw
        assert state['was_replaced'], result.messages

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

class TestFilterLanguage:
    """ The filter language and its edges over the wire - predicates, aggregations,
    constructions, the no-match shape, both error kinds and the length cap.
    """

# ################################################################################################################################

    def test_the_language_beyond_one_path(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Filters)
        session_id = _helpers.open_session(client)

        # The predicate returns the ids of the invoices over the amount ..
        body = _call_invoices(client, session_id, _expression_predicate)
        data = _helpers.get_result_data(body)
        assert data == ['INV-2026-0004', 'INV-2026-0005'], data

        # .. the aggregation returns the one summed number ..
        body = _call_invoices(client, session_id, _expression_aggregation)
        data = _helpers.get_result_data(body)
        assert data == 515, data

        # .. the construction returns exactly the object the expression builds ..
        body = _call_invoices(client, session_id, _expression_object)
        data = _helpers.get_result_data(body)
        assert data == {'first': 'INV-2026-0001', 'how_many': 5}, data

        # .. and each of the three is audited verbatim, in order.
        events = _audit.wait_for_events(
            audit_db_path, 3,
            object_name=_constants.Gateway_Filters,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        traced = []

        for event in events:
            if event['sub_key'] == session_id:
                traced.append(event['data']['client_filter'])

        assert traced == [_expression_predicate, _expression_aggregation, _expression_object], traced

# ################################################################################################################################

    def test_no_match_is_a_defined_result(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Filters)
        session_id = _helpers.open_session(client)

        # A filter that matches nothing returns the defined empty shape - a JSON null ..
        body = _call_invoices(client, session_id, _expression_no_match)

        text = _helpers.get_result_text(body)
        assert text == 'null', body

        # .. and the audit still records the expression.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Filters,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event_data = events[-1]['data']
        assert event_data['client_filter'] == _expression_no_match, event_data

# ################################################################################################################################

    def test_an_evaluation_error_is_invalid_params(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Filters)
        session_id = _helpers.open_session(client)

        # The expression compiles but fails against this document - the same
        # invalid-params contract a syntax error gets ..
        body = _call_invoices(client, session_id, _expression_evaluation_error)

        error = body['error']
        assert error['code'] == _constants.Error_Invalid_Params, body
        assert _filter_key in error['message'], body

        # .. audited as an error, with no filter trace because none was applied.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Filters,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event
        assert event['data']['error_code'] == _constants.Error_Invalid_Params, event
        assert 'client_filter' not in event['data'], event

# ################################################################################################################################

    def test_the_expression_length_cap_over_the_wire(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Filters)
        session_id = _helpers.open_session(client)

        # An expression past the engine's cap is refused as invalid params ..
        body = _call_invoices(client, session_id, _expression_too_long)

        error = body['error']
        assert error['code'] == _constants.Error_Invalid_Params, body
        assert 'too long' in error['message'], body

        # .. and audited as an error.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Filters,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event

# ################################################################################################################################

    def test_filters_on_the_stateless_revision(self, zato_server:'anydict') -> 'None':

        mcp_url = zato_server['mcp_url'](_constants.Path_Filters)
        client = MCPStatelessClient(mcp_url, auth=zato_server['basic_auth'])

        arguments = {'count': _invoice_count, _filter_key: _expression_predicate}
        response = client.tools_call(_constants.Service_Invoice_List, arguments)

        body = response.json()

        data = _helpers.get_result_data(body)
        assert data == ['INV-2026-0004', 'INV-2026-0005'], body

# ################################################################################################################################

    def test_filters_never_touch_error_responses(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Filters)
        session_id = _helpers.open_session(client)

        # The service raises, the filter travels with the call regardless ..
        arguments = {'order_id': _constants.Order_ID_Not_Cancellable, _filter_key: 'order_id'}
        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Cancel, arguments)

        # .. the error content comes back untouched by the filter ..
        result = body['result']
        assert result['isError'] is True, body

        text = _helpers.get_result_text(body)
        assert text == 'Bad request', body

        # .. and the audit event carries no filter trace.
        events = _audit.wait_for_events(
            audit_db_path, 1,
            object_name=_constants.Gateway_Filters,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        event = events[-1]
        assert event['outcome'] == AuditOutcome.Error, event
        assert 'client_filter' not in event['data'], event

# ################################################################################################################################

    def test_one_session_many_filters(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Filters)
        session_id = _helpers.open_session(client)

        # Each call of the one session passes an expression of its own ..
        expressions = (_totals_expression, _expression_predicate, _expression_aggregation)
        expected = ([101, 102, 103, 104, 105], ['INV-2026-0004', 'INV-2026-0005'], 515)

        for expression, expected_data in zip(expressions, expected):

            body = _call_invoices(client, session_id, expression)
            data = _helpers.get_result_data(body)

            assert data == expected_data, (expression, data)

        # .. and each audit event of the session records its own filter verbatim, in order.
        events = _audit.wait_for_events(
            audit_db_path, len(expressions),
            object_name=_constants.Gateway_Filters,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        traced = []

        for event in events:
            if event['sub_key'] == session_id:
                traced.append(event['data']['client_filter'])

        assert traced == list(expressions), traced

# ################################################################################################################################
# ################################################################################################################################

class TestModelComposedFilters:
    """ The model writes the predicate expression itself once it knows the response schema.
    """

# ################################################################################################################################

    def test_the_model_composes_a_real_filter(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Filters)

        system_text = (
            'Every tool accepts an optional response_filter argument - a JSONata expression '
            'applied to the tool response before it is returned. The invoice tool responds with '
            '{"count": n, "invoices": [{"invoice_id", "customer_id", "total", "currency", "notes"}]}. '
            'When only part of a response is needed, write a response_filter yourself, '
            'e.g. a predicate like invoices[total > 100].invoice_id.')

        task = (
            'List the last 5 invoices and give me only the ids of those whose total is over 103. '
            'Use a response_filter so the tool returns just those ids.')

        result = _agent.run_agent(client, task, system_text=system_text)

        # The transcript shows a filter the model wrote itself ..
        composed_calls = []

        for call in result.tool_calls:
            if call.tool_name == _constants.Service_Invoice_List:
                if _filter_key in call.arguments and not call.is_error:
                    composed_calls.append(call)

        assert composed_calls, result.messages

        last_call = composed_calls[-1]
        assert 'total' in last_call.arguments[_filter_key], last_call.arguments

        # .. the tool result the model saw is the filtered subset ..
        filtered_text = last_call.result_text

        assert 'INV-2026-0004' in filtered_text, filtered_text
        assert 'INV-2026-0005' in filtered_text, filtered_text
        assert 'INV-2026-0001' not in filtered_text, filtered_text

        # .. and the answer names the matching ids alone.
        assert _helpers.text_contains(result.final_text, 'INV-2026-0004'), result.final_text
        assert _helpers.text_contains(result.final_text, 'INV-2026-0005'), result.final_text
        assert not _helpers.text_contains(result.final_text, 'INV-2026-0001'), result.final_text

# ################################################################################################################################
# ################################################################################################################################
