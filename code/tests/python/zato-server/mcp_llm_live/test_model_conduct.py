# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# local
import _agent
import _audit
import _constants
import _diag
import _helpers

# Zato
from zato.common.audit_log.api import AuditEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The turn bound of the hopeless-task conversation - low so the bound itself is what ends it
_hopeless_max_turns = 3

# What the final answer of a failed cancellation may not claim
_word_of_success = 'cancelled successfully'

# The words a plain failure answer carries at least one of
_failure_words = ('cannot', 'could not', 'unable', 'fail', 'error', 'not possible', 'not be')

# The raw PII values of the customer record that tokenization must keep away from the model -
# the broken-checksum IMEI is absent because validation deliberately leaves it in place
_raw_pii_values = (
    _constants.Customer_Email,
    _constants.Customer_IMEI_Compact,
    _constants.Customer_IMEI_Dashed,
    _constants.Customer_IMEI_Spaced,
    _constants.Customer_IPv4,
)

# The prefix every PII replacement of the international land carries
_pii_replacement_prefix = 'REPLACED_INTL_'

# The same customer question in three wordings
_paraphrased_tasks = (
    'What city does customer CRM-1001 live in?',
    'Look up the town of residence of the customer whose id is CRM-1001.',
    'CRM-1001 - which city is on file for this customer?',
)

# ################################################################################################################################
# ################################################################################################################################

class TestModelConduct:
    """ What the conversation itself proves about the model's behavior,
    asserted from the wire logs of each test's own traffic.
    """

# ################################################################################################################################

    def test_replaced_data_is_all_the_model_ever_sees(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_PII)

        task = 'Fetch the record of customer CRM-1001 and summarize the contact details you received.'
        result = _agent.run_agent(client, task)

        # Every chat request the conversation sent carries replacements only ..
        chat_requests = _diag.get_entries('chat_request')
        assert chat_requests, 'No chat requests were logged'

        for entry in chat_requests:
            request_text = dumps(entry['payload'])

            for raw_value in _raw_pii_values:
                assert raw_value not in request_text, raw_value

        # .. at least one of them carries the replacements themselves ..
        all_requests_text = dumps(chat_requests)
        assert _pii_replacement_prefix in all_requests_text, all_requests_text

        # .. and the final answer is as free of the raw values as the requests were.
        for raw_value in _raw_pii_values:
            assert raw_value not in result.final_text, result.final_text

# ################################################################################################################################

    def test_the_turn_cap_ends_a_hopeless_task_cleanly(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        task = f'Cancel order {_constants.Order_ID_Not_Cancellable}.'
        system_text = 'Never give up - if a cancellation fails, call the tool again until it succeeds.'

        result = _agent.run_agent(client, task, system_text=system_text, max_turns=_hopeless_max_turns)

        # Every cancellation attempt failed - the model may check the order's
        # status along the way and that check is allowed to succeed ..
        cancel_calls = []

        for call in result.tool_calls:
            if call.tool_name == _constants.Service_Order_Cancel:
                cancel_calls.append(call)

        assert cancel_calls, result.messages

        for call in cancel_calls:
            assert call.is_error, call

        # .. the conversation spent exactly its turn bound on tool calls before
        # the closing instruction told the model the tools were gone ..
        turn_messages = []

        for message in result.messages:

            if message['role'] == 'system' and message['content'] == _agent._finalize_instruction:
                break

            if message['role'] == 'assistant':
                turn_messages.append(message)

        assert len(turn_messages) == _hopeless_max_turns, result.messages

        for message in turn_messages:
            assert message['tool_calls'], message

        # .. and the final answer reports the failure instead of inventing a result.
        assert result.final_text, result.messages
        assert not _helpers.text_contains(result.final_text, _word_of_success), result.final_text
        assert _helpers.contains_any_word(result.final_text, _failure_words), result.final_text

# ################################################################################################################################

    def test_answers_are_grounded_in_tool_data_alone(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Conduct)

        task = 'What is the capital of Australia? You must look it up with the reference tool and answer with exactly what it returns.'
        result = _agent.run_agent(client, task)

        # The reference tool was consulted ..
        tool_names = []

        for call in result.tool_calls:
            tool_names.append(call.tool_name)

        assert _constants.Service_Fact_Get in tool_names, tool_names

        # .. and the answer repeats the tool's value, not the well-known one.
        assert _helpers.text_contains(result.final_text, _constants.Fact_Answer), result.final_text
        assert not _helpers.text_contains(result.final_text, _constants.Fact_Answer_Known), result.final_text

# ################################################################################################################################

    def test_tool_choice_is_stable_under_paraphrase(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        for task in _paraphrased_tasks:

            client = _helpers.make_client(zato_server, _constants.Path_Main)
            result = _agent.run_agent(client, task)

            # Each wording picks the customer tool with the same schema-valid arguments ..
            first_call = result.tool_calls[0]
            assert first_call.tool_name == _constants.Service_Customer_Get, (task, first_call)
            assert first_call.arguments == {'customer_id': _constants.Customer_ID}, (task, first_call)

            # .. and each answer carries the customer's city.
            assert _helpers.text_contains(result.final_text, _constants.Customer_City), (task, result.final_text)

# ################################################################################################################################

    def test_two_independent_lookups_are_answered_call_by_call(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Conduct)

        task = 'For customer CRM-1001, report both the loyalty points balance and the outstanding debt.'

        result = _agent.run_agent(client, task)

        # The model made both lookups on its own - the task is the only user turn ..
        user_messages = []

        for message in result.messages:
            if message['role'] == 'user':
                user_messages.append(message)

        assert len(user_messages) == 1, result.messages

        # .. each tool call of the transcript is answered by exactly one
        # tool message whose id matches the call ..
        call_names = {}
        replies = {}

        for message in result.messages:

            if message['role'] == 'assistant':
                if 'tool_calls' in message:
                    for tool_call in message['tool_calls']:
                        call_names[tool_call['id']] = tool_call['function']['name']

            elif message['role'] == 'tool':
                call_id = message['tool_call_id']

                assert call_id in call_names, message
                assert call_id not in replies, message

                replies[call_id] = message['content']

        assert len(call_names) >= 2, result.messages
        assert set(replies) == set(call_names), (call_names, replies)

        # .. the points reply answered the points call and the debt reply the debt call ..
        for call_id, tool_name in call_names.items():

            if tool_name.endswith('lookup'):
                assert '4180' in replies[call_id], replies

            elif tool_name.endswith('query'):
                assert '250' in replies[call_id], replies

        # .. both results made it into the answer ..
        assert _helpers.text_contains_number(result.final_text, '4180'), result.final_text
        assert _helpers.text_contains_number(result.final_text, '250'), result.final_text

        # .. and both calls are audited under this one conversation.
        events = _audit.wait_for_events(
            audit_db_path, 2,
            object_name=_constants.Gateway_Conduct,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        endpoints = []

        for event in events:
            if event['sub_key'] == result.session_id:
                endpoints.append(event['endpoint'])

        assert _constants.Service_Account_Lookup in endpoints, events
        assert _constants.Service_Account_Query in endpoints, events

# ################################################################################################################################

    def test_the_docstring_drives_the_choice(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        # The two tools have identical schemas and opaque names - the debt question
        # must pick the tool whose description talks about debt ..
        client = _helpers.make_client(zato_server, _constants.Path_Conduct)

        task = 'What is the outstanding debt of customer CRM-1001? Answer with the amount.'
        result = _agent.run_agent(client, task)

        first_call = result.tool_calls[0]
        assert first_call.tool_name == _constants.Service_Account_Query, result.tool_calls
        assert _helpers.text_contains_number(result.final_text, '250'), result.final_text

        # .. and the points question must pick the other one.
        client = _helpers.make_client(zato_server, _constants.Path_Conduct)

        task = 'How many loyalty points does customer CRM-1001 have? Answer with the number.'
        result = _agent.run_agent(client, task)

        first_call = result.tool_calls[0]
        assert first_call.tool_name == _constants.Service_Account_Lookup, result.tool_calls
        assert _helpers.text_contains_number(result.final_text, '4180'), result.final_text

# ################################################################################################################################
# ################################################################################################################################
