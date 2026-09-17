# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explain service end to end for an outgoing LLM connection - a real quickstart server with an LLM connection of its
# own, imported through enmasse, pointing at a live provider simulator that answers every completion with a 429, real
# calls through the connection from inside the server, one real sweep, and the explained alert read off the server's own
# databases and received by a real SMTP receiver. The second proof has the simulator answer with completions cut short by
# the token limit - each a 200 with `length` as its finish reason - and reads the explanation of the truncations, with
# the completions named in its message. The explanation itself keeps going through the suite's Ollama connection.

# stdlib
import os
from http.client import OK, TOO_MANY_REQUESTS
from time import sleep, time

# SQLAlchemy
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.evidence import Heading_Object
from zato.common.alerting.explain.settings_info import Label_Alerts, On
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.api import Alerting
from zato.common.audit_log.api import AuditEvent, AuditSource, event_attr_table, event_table
from zato.common.audit_log.common import LLMAttr, LLMFinish
from zato.common.defaults import default_cluster_id
from zato.common.test.client import AdminClient

# Test helpers
from live_config import LiveServer
from live_enmasse import deactivate_document, import_document
from live_trace import Channel_Explain, Channel_Outgoing, Received, Sent, separator, trace
from llm_test_server import Input_Tokens, Output_Tokens
from test_explain_live import _assert_sound_explanation, _email_to, _trace_delivery
from test_explain_live_channel import _new_admin_client, _new_notification_config, _point_smtp_at_receiver, \
     _server_audit_engine, unwrap as _unwrap
from test_explain_live_outgoing import _status_separator, _wrapper_wait_step, _wrapper_wait_timeout

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strdict

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveOutgoingLLMStatusCodes:

    def test_an_llm_outgoing_connections_rate_limits_are_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        llm_test_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        client = _new_admin_client()

        # The server's own notification connection delivers to the receiver ..
        _point_smtp_at_receiver(smtp_receiver)

        # .. the provider answers every completion with a 429, the way a provider answers past its rate limit ..
        llm_test_server.configure(_completions_path, respond_raw=(TOO_MANY_REQUESTS, _rate_limited_body))

        # .. and the connection points at it, with a status code threshold four calls go past.
        address = llm_test_server.url(_address_path)
        outgoing_document = _create_llm_outgoing(_limited_name, address)

        # The sweep explains through the LLM connection and mails from the address below
        notification_config = _new_notification_config()

        # Real calls through the connection, from inside the server, each answered with the 429
        _produce_rate_limits(client)

        # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
        trace(Channel_Outgoing, Sent, f'invoke {Alerting.Service} with {notification_config}')
        _ = client.invoke(Alerting.Service, notification_config)

        # Each call is on record under the connection's name, the 429 as its status line and the model as its attribute ..
        responses = _get_llm_responses(_limited_name)
        _trace_responses(responses)

        assert len(responses) == _call_count

        for row in responses:
            assert row['status'] == _rate_limited_status, row
            assert row['outcome'] == 'error', row
            assert row['attrs'] == {LLMAttr.Model: _model}, row

        # .. the rate limits fired the status codes rule, because a 429 is among the codes the connection alerts on ..
        explanations = _get_stored_llm_explanations(_limited_name)
        by_rule = _by_rule(explanations)

        assert _status_codes_rule in by_rule, sorted(by_rule)
        assert _truncations_rule not in by_rule, sorted(by_rule)

        explained = by_rule[_status_codes_rule]
        evidence = explained['evidence']

        # .. its Object is the connection's own, read from the generic connection row, with where the calls go
        # and which model they ask ..
        assert Heading_Object in evidence
        assert f'Name: {_limited_name}' in evidence
        assert 'Type: LLM' in evidence
        assert f'Address: {address}' in evidence
        assert f'Model: {_model}' in evidence
        assert f'{Label_Alerts}: {On}' in evidence

        # .. the failures are the rate limits, grouped under the status line and the model every row names ..
        assert _rate_limited_group in evidence

        _assert_sound_explanation(explained, _rate_limit_words)

        # .. and the explained alert reached the mailbox.
        _assert_delivered(smtp_receiver, explained)

        deactivate_document(outgoing_document)

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveOutgoingLLMTruncations:

    def test_an_llm_outgoing_connections_truncated_completions_are_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        llm_test_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        client = _new_admin_client()

        # The server's own notification connection delivers to the receiver ..
        _point_smtp_at_receiver(smtp_receiver)

        # .. the provider answers every completion with a 200 whose finish reason is `length` - it ran out of
        # max tokens, so the reply reads fine but is incomplete ..
        llm_test_server.configure(_completions_path, respond_raw=(OK, _truncated_body))

        # .. and the connection points at it, with a truncations threshold four calls go past.
        address = llm_test_server.url(_address_path)
        outgoing_document = _create_llm_outgoing(_truncated_name, address)

        # The sweep explains through the LLM connection and mails from the address below
        notification_config = _new_notification_config()

        # Real calls through the connection, from inside the server, each coming back cut short
        _produce_truncations(client)

        # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
        trace(Channel_Outgoing, Sent, f'invoke {Alerting.Service} with {notification_config}')
        _ = client.invoke(Alerting.Service, notification_config)

        # Each call is on record as an OK row under `200 OK` with the model, the finish reason and the two token counts ..
        responses = _get_llm_responses(_truncated_name)
        _trace_responses(responses)

        assert len(responses) == _call_count

        for row in responses:
            assert row['status'] == _status_ok, row
            assert row['outcome'] == 'ok', row
            assert row['attrs'][LLMAttr.Model] == _model, row
            assert row['attrs'][LLMAttr.Finish_Reason] == LLMFinish.Length, row
            assert row['attrs'][LLMAttr.Input_Tokens] == str(Input_Tokens), row
            assert row['attrs'][LLMAttr.Output_Tokens] == str(Output_Tokens), row

        # .. the truncations fired their own rule and none of the failure ones, because every call came back OK ..
        explanations = _get_stored_llm_explanations(_truncated_name)
        by_rule = _by_rule(explanations)

        assert _truncations_rule in by_rule, sorted(by_rule)
        assert _status_codes_rule not in by_rule, sorted(by_rule)

        explained = by_rule[_truncations_rule]
        evidence = explained['evidence']

        # .. the alert's message names how many completions were cut short ..
        assert f'{_call_count} truncated completions' in explained['message'], explained['message']

        # .. its Object is the connection's own ..
        assert Heading_Object in evidence
        assert f'Name: {_truncated_name}' in evidence
        assert 'Type: LLM' in evidence
        assert f'Model: {_model}' in evidence

        # .. the failures are the truncated completions - 200 rows told apart by their finish reason, with the model
        # and the cost of each ..
        assert _truncated_group in evidence

        _assert_sound_explanation(explained, _truncation_words)

        # .. and the explained alert reached the mailbox.
        _assert_delivered(smtp_receiver, explained)

        deactivate_document(outgoing_document)

# ################################################################################################################################
# ################################################################################################################################

# How many calls each proof makes through its connection - one more than the thresholds below ask for
_call_count = 4
_status_code_threshold = 3
_truncations_threshold = 3

# The rules the two proofs fire
_status_codes_rule = 'Status_Codes'
_truncations_rule = 'Truncated_Completions'

# The provider simulator - the connection's address is its OpenAI-shaped base path and the completions path is what
# the connection's calls reach under it
_address_path = '/v1'
_completions_path = '/v1/chat/completions'

# The model the connections ask - an OpenAI one, so the connections speak the simulator's OpenAI protocol -
# and the key they send, which the simulator never checks
_model = 'gpt-4o-mini'
_api_key = 'explain-live-key'

# The connections of the two proofs
_limited_name = 'explain.live.outgoing.llm'
_truncated_name = 'explain.live.outgoing.llm.truncated'

# What the rate-limited calls come back with and the status line they are written under
_rate_limited_status = '429 Too Many Requests'
_rate_limited_body = {'error': {'message': 'Rate limit reached for requests', 'type': 'rate_limit_error'}}

# What a completion that came back is written under
_status_ok = '200 OK'

# The completion the provider cut short - a full OpenAI body whose finish reason is `length`
_truncated_body = {
    'id': 'chatcmpl-explain-live',
    'object': 'chat.completion',
    'created': 1700000000,
    'model': _model,
    'choices': [{
        'index': 0,
        'message': {'role': 'assistant', 'content': 'The quarterly report begins with an overview of'},
        'finish_reason': 'length',
    }],
    'usage': {
        'prompt_tokens': Input_Tokens,
        'completion_tokens': Output_Tokens,
        'total_tokens': Input_Tokens + Output_Tokens,
    },
}

# What the failures of each explanation are grouped under - the status line and the attributes every row names
_rate_limited_group = _rate_limited_status + _status_separator + f'{LLMAttr.Model}={_model}'
_truncated_group = _status_ok + _status_separator + f'{LLMAttr.Model}={_model}, {LLMAttr.Finish_Reason}={LLMFinish.Length}, ' + \
    f'{LLMAttr.Input_Tokens}={Input_Tokens}, {LLMAttr.Output_Tokens}={Output_Tokens}'

# The words a sound explanation of each failure is expected to use at least one of
_rate_limit_words = ['rate', 'limit', '429', 'quota', 'throttl', 'too many', 'provider', 'openai', 'request']
_truncation_words = ['truncat', 'cut', 'length', 'max_tokens', 'max tokens', 'token', 'limit', 'incomplete', 'short']

# ################################################################################################################################
# ################################################################################################################################

def _create_llm_outgoing(name:'str', address:'str') -> 'anydict':
    """ An LLM connection of the proof - the LLM explaining its alerts, an OpenAI model so it speaks the simulator's
    protocol, a key the simulator never checks, and thresholds low enough for four calls to fire the rules. What is
    returned is the document it went in with, for the proof to deactivate it with once it is through.
    """
    out = {
        'llm': [{
            'name': name,
            'is_active': True,
            'address': address,
            'model': _model,
            'api_key': _api_key,
            'pool_size': 1,
            'timeout': 10,
            'max_tokens': 64,
            'max_history_turns': 20,
            'chat_expiry': 86400,
            'alerts': {
                'is_active': True,
                'use_llm': True,
                'status_code_threshold': _status_code_threshold,
                'truncations': _truncations_threshold,
            },
        }],
    }

    import_document(out)

    trace(Channel_Outgoing, Sent, f'llm connection `{name}` -> {address}, model {_model}')
    separator(Channel_Outgoing)

    return out

# ################################################################################################################################

def _invoke_through(client:'AdminClient', name:'str', text:'str') -> 'anydict':
    """ One completion through the connection, from inside the server - a connection just created takes a moment
    to appear among the server's wrappers, so a call that finds nothing under the name yet is tried again.
    """
    payload = {'outconn': name, 'text': text}
    deadline = time() + _wrapper_wait_timeout

    while True:
        try:
            out = _unwrap(client.invoke(LiveServer.llm_invoke_service, payload))
        except Exception:
            if time() < deadline:
                sleep(_wrapper_wait_step)
                continue
            raise
        else:
            return out

# ################################################################################################################################

def _produce_rate_limits(client:'AdminClient') -> 'None':
    """ Real completions through the connection - each reaches the simulator that answers with a 429 and comes
    back as the error the client raised for it, named on the trace with its status.
    """
    for index in range(_call_count):

        trace(Channel_Outgoing, Sent, f'completion {index + 1} through `{_limited_name}`')

        response = _invoke_through(client, _limited_name, f'Summarise report {index + 1}')

        trace(Channel_Outgoing, Received, f'completion {index + 1}: {response["error"]}')
        separator(Channel_Outgoing)

        assert 'error' in response, response
        assert str(TOO_MANY_REQUESTS) in response['error'], response

# ################################################################################################################################

def _produce_truncations(client:'AdminClient') -> 'None':
    """ Real completions through the connection - each reaches the simulator that answers with a completion cut
    short and comes back as text with `length` as its finish reason, named on the trace with that reason.
    """
    for index in range(_call_count):

        trace(Channel_Outgoing, Sent, f'completion {index + 1} through `{_truncated_name}`')

        response = _invoke_through(client, _truncated_name, f'Write the full quarterly report {index + 1}')

        trace(Channel_Outgoing, Received, f'completion {index + 1}: finish_reason={response["finish_reason"]} ' +
            f'usage={response["usage"]} text={response["text"]!r}')
        separator(Channel_Outgoing)

        assert response['finish_reason'] == LLMFinish.Length, response
        assert response['usage']['output_tokens'] == Output_Tokens, response

# ################################################################################################################################

def _get_llm_responses(name:'str') -> 'anylist':
    """ Every response the live server received through the connection, as its audit log recorded it, each with
    the attributes the wrapper stored next to it.
    """
    engine = _server_audit_engine()

    # The server creates the table with its first audit row, so until the first call lands there is nothing to read
    if not inspect(engine).has_table(event_table.name):
        return []

    query = select(event_table).\
        where(event_table.c.source == AuditSource.LLM).\
        where(event_table.c.object_name == name).\
        where(event_table.c.event_type == AuditEvent.Response_Received).\
        order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

        for row in out:
            row['attrs'] = _get_attrs(connection, row['id'])

    return out

# ################################################################################################################################

def _get_attrs(connection:'any_', event_id:'int') -> 'strdict':
    """ The attributes of one audit row, by name.
    """
    query = select(event_attr_table.c.name, event_attr_table.c.value).where(event_attr_table.c.event_id == event_id)

    out = {}
    for name, value in connection.execute(query):
        out[name] = value

    return out

# ################################################################################################################################

def _trace_responses(responses:'anylist') -> 'None':
    """ Each call as the audit log recorded it - its status and finish reason, the way the proof reads them back.
    """
    for row in responses:
        attrs = row['attrs']
        finish_reason = attrs.get(LLMAttr.Finish_Reason, '')
        trace(Channel_Outgoing, Received, f'llm audit log: {row["event_time_iso"]} {row["status"]!r} ' +
            f'model={attrs[LLMAttr.Model]} finish_reason={finish_reason!r} duration={row["duration_ms"]}ms')

    separator(Channel_Outgoing)

# ################################################################################################################################

def _get_stored_llm_explanations(name:'str') -> 'anylist':
    """ Every explanation the live server stored for the connection, read off its own ODB - the proofs share the
    server, so each one reads the explanations of its own connection alone.
    """
    path = os.path.join(os.path.dirname(LiveServer.server_directory), 'zato.db')
    session_maker = sessionmaker(bind=create_engine(f'sqlite:///{path}'))

    store = ExplanationStore(session_maker, default_cluster_id)

    # Our response to produce
    out:'anylist' = []

    for explanation in store.get_list():
        if explanation['source'] == AuditSource.LLM:
            if explanation['object_name'] == name:
                out.append(explanation)

    for explanation in out:
        trace(Channel_Explain, Received, f'llm {explanation["rule"]}: {explanation["message"]}')
        trace(Channel_Explain, Received, f'llm {explanation["rule"]}: {explanation["explanation"]}')
        trace(Channel_Explain, Received, f'confidence: {explanation["confidence"]}, remediation: {explanation["remediation"]}')
        separator(Channel_Explain)

    return out

# ################################################################################################################################

def _by_rule(explanations:'anylist') -> 'anydict':
    """ The explanations of one connection by the rule each one explains.
    """
    out = {}

    for explanation in explanations:
        out[explanation['rule']] = explanation

    return out

# ################################################################################################################################

def _assert_delivered(smtp_receiver:'any_', explained:'anydict') -> 'None':
    """ The explained alert reached the mailbox, in an email to the default recipients.
    """
    _trace_delivery(smtp_receiver)

    bodies = []
    for received in smtp_receiver.messages:
        assert received.recipients == _email_to
        bodies.append(received.body)

    for body in bodies:
        if explained['explanation'] in body:
            break
    else:
        raise AssertionError(f'Expected an email carrying {explained["explanation"]!r}')

# ################################################################################################################################
# ################################################################################################################################
