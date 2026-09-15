# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit rows the LLM wrapper leaves behind - a completion that came back is one OK row under `200 OK` with the model,
# the finish reason and the two token counts as attributes, a completion cut short is still an OK row with `length` as
# its finish reason whichever of the three providers cut it, a 429 is an error row under `429 Too Many Requests` with
# the model alone, a timeout is an error row under `timeout`, a refused connection one under `connection-error` and a
# Gemini prompt block is an error row under `200 OK` with `refusal` as its finish reason - every row the LLM collectors
# and the alerting evidence read, driven over the live provider simulator.

# stdlib
import socket
from http.client import OK, TOO_MANY_REQUESTS
from tempfile import gettempdir

# pytest
import pytest

# Redis
from redis import Redis

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditSource
from zato.common.audit_log.common import LLMAttr, LLMFinish, TransportStatus
from zato.common.ext.bunch import Bunch
from zato.common.typing_ import cast_
from zato.distlock import LockManager
from zato.server.connection.cache import CacheAPI
from zato.server.connection.llm.common import LLMError
from zato.server.generic.api.outconn_llm import OutconnLLMWrapper

# Test helpers
from llm_test_server import Input_Tokens, Output_Tokens

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdict, stranydict
    any_ = any_
    anydict = anydict
    strdict = strdict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The status lines the rows are written under
_status_ok = '200 OK'
_status_rate_limited = '429 Too Many Requests'

# The models the wrapper asks, each choosing its own protocol by its name
_openai_model = 'gpt-4o-mini'
_claude_model = 'claude-sonnet-4-5'
_gemini_model = 'gemini-2.0-flash'

# The paths the simulator answers
_openai_path = '/v1/chat/completions'
_claude_path = '/v1/messages'
_gemini_path = f'/v1beta/models/{_gemini_model}:generateContent'

# A timeout short enough for a slow provider to trip it, in seconds, and how long that provider sleeps
_short_timeout = 1
_slow_delay = 3

# ################################################################################################################################
# ################################################################################################################################

class _TestConfigManager:
    """ Carries just what the wrapper reaches for on the real config manager.
    """
    def __init__(self, cache_api:'CacheAPI') -> 'None':
        self.cache_api = cache_api
        self.generic_conn_api = {}

# ################################################################################################################################
# ################################################################################################################################

class _TestParallelServer:
    """ Carries just what the wrapper reaches for on the real parallel server.
    """
    def __init__(self, cache_api:'CacheAPI') -> 'None':
        self.name = 'test-llm-audit-server'
        self.config_manager = _TestConfigManager(cache_api)
        self.zato_lock_manager = LockManager('zato-pass-through', 'zato', cast_('any_', None))

        # A directory with no default-models.yaml, so the wrapper reads the default catalog
        self.user_conf_location = [gettempdir()]

# ################################################################################################################################
# ################################################################################################################################

def _get_wrapper(
    llm_test_server:'any_',
    redis_server:'anydict',
    conn_name:'str',
    model:'str'=_openai_model,
    address_path:'str'='/v1',
    timeout:'int'=10,
) -> 'OutconnLLMWrapper':
    """ Builds a wrapper over the provider simulator with one client ready in its queue.
    """
    config = Bunch()
    config.id = 1
    config.name = conn_name
    config.username = None
    config.is_active = True
    config.pool_size = 1
    config.queue_build_cap = 30
    config.address = llm_test_server.url(address_path)
    config.secret = 'test-key'
    config.model = model
    config.timeout = timeout
    config.max_tokens = 256
    config.max_history_turns = 20
    config.chat_expiry = 86400

    redis_client = Redis(host=redis_server['host'], port=redis_server['port'])
    cache_api = CacheAPI(redis_client)

    server = _TestParallelServer(cache_api)
    out = OutconnLLMWrapper(config, cast_('any_', server))

    # Build the one client synchronously instead of through the queue's greenlets
    out.add_client()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _rows_of(conn_name:'str') -> 'list':
    """ The audit rows a connection has written, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table).where(
        event_table.c.source == AuditSource.LLM,
        event_table.c.object_name == conn_name,
    ).order_by(event_table.c.id)

    with engine.connect() as connection:
        out = connection.execute(query).mappings().fetchall()

    return out

# ################################################################################################################################

def _attrs_of(event_id:'int') -> 'strdict':
    """ The attributes of one audit row, as stored.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.name, event_attr_table.c.value, event_attr_table.c.value_number).where(
        event_attr_table.c.event_id == event_id,
    )

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    out = {}
    for name, value, value_number in rows:
        out[name] = (value, value_number)

    return out

# ################################################################################################################################

def _the_one_row(conn_name:'str') -> 'any_':
    """ The single row a connection wrote - the tests give each scenario a connection of its own.
    """
    rows = _rows_of(conn_name)
    assert len(rows) == 1, rows

    out = rows[0]
    return out

# ################################################################################################################################

def _openai_completion(finish_reason:'str') -> 'stranydict':
    """ A full OpenAI completion body with the finish reason given.
    """
    out = {
        'id': 'chatcmpl-test-2',
        'object': 'chat.completion',
        'created': 1700000000,
        'model': _openai_model,
        'choices': [{
            'index': 0,
            'message': {'role': 'assistant', 'content': 'A reply that was'},
            'finish_reason': finish_reason,
        }],
        'usage': {
            'prompt_tokens': Input_Tokens,
            'completion_tokens': Output_Tokens,
            'total_tokens': Input_Tokens + Output_Tokens,
        },
    }
    return out

# ################################################################################################################################

def _claude_completion(stop_reason:'str') -> 'stranydict':
    """ A full Claude completion body with the stop reason given.
    """
    out = {
        'id': 'msg_test_2',
        'type': 'message',
        'role': 'assistant',
        'model': _claude_model,
        'content': [{'type': 'text', 'text': 'A reply that was'}],
        'stop_reason': stop_reason,
        'usage': {
            'input_tokens': Input_Tokens,
            'output_tokens': Output_Tokens,
        },
    }
    return out

# ################################################################################################################################

def _gemini_completion(finish_reason:'str') -> 'stranydict':
    """ A full Gemini completion body with the finish reason given.
    """
    out = {
        'candidates': [{
            'content': {'role': 'model', 'parts': [{'text': 'A reply that was'}]},
            'finishReason': finish_reason,
        }],
        'usageMetadata': {
            'promptTokenCount': Input_Tokens,
            'candidatesTokenCount': Output_Tokens,
            'totalTokenCount': Input_Tokens + Output_Tokens,
        },
    }
    return out

# ################################################################################################################################

def _closed_port() -> 'int':
    """ A port nothing listens on - bound for a moment and released.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        out = tcp_socket.getsockname()[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCompletionRows:

    def test_a_completion_is_one_ok_row_with_its_model_finish_reason_and_tokens(
        self,
        llm_test_server:'any_',
        redis_server:'anydict',
    ) -> 'None':

        conn_name = 'audit.completion'
        wrapper = _get_wrapper(llm_test_server, redis_server, conn_name)

        response = wrapper.invoke('Hello')
        assert response['finish_reason'] == LLMFinish.Stop

        row = _the_one_row(conn_name)

        # The row itself - the response event, OK, under `200 OK`, with the connection and the address it called ..
        assert row['event_type'] == AuditEvent.Response_Received
        assert row['outcome'] == 'ok'
        assert row['status'] == _status_ok
        assert row['object_name'] == conn_name
        assert row['endpoint'] == llm_test_server.url('/v1')
        assert row['duration_ms'] >= 0

        # .. and its four attributes - the model, why it stopped and what it cost, the counts stored as numbers too
        attrs = _attrs_of(row['id'])

        assert attrs[LLMAttr.Model] == (_openai_model, None)
        assert attrs[LLMAttr.Finish_Reason] == (LLMFinish.Stop, None)
        assert attrs[LLMAttr.Input_Tokens] == (str(Input_Tokens), Input_Tokens)
        assert attrs[LLMAttr.Output_Tokens] == (str(Output_Tokens), Output_Tokens)

# ################################################################################################################################

    def test_a_completion_cut_short_is_an_ok_row_with_length_as_its_finish_reason(
        self,
        llm_test_server:'any_',
        redis_server:'anydict',
    ) -> 'None':

        conn_name = 'audit.truncated'
        wrapper = _get_wrapper(llm_test_server, redis_server, conn_name)

        # The provider ran out of max_tokens and says so in the completion's finish reason
        llm_test_server.configure(_openai_path, respond_raw=(OK, _openai_completion('length')))

        response = wrapper.invoke('Write me a novel')
        assert response['finish_reason'] == LLMFinish.Length

        row = _the_one_row(conn_name)

        # A truncation is not a failure - the row is OK under `200 OK` ..
        assert row['outcome'] == 'ok'
        assert row['status'] == _status_ok

        # .. and it is the finish reason alone that tells it apart, in the vocabulary the collectors count
        attrs = _attrs_of(row['id'])
        assert attrs[LLMAttr.Finish_Reason] == (LLMFinish.Length, None)
        assert attrs[LLMAttr.Input_Tokens] == (str(Input_Tokens), Input_Tokens)

# ################################################################################################################################

    def test_each_provider_writes_a_completion_it_cut_short_as_length(
        self,
        llm_test_server:'any_',
        redis_server:'anydict',
    ) -> 'None':

        # The three providers each have their own word for running out of tokens ..
        cases = [
            ('audit.length.openai', _openai_model, '/v1', _openai_path, _openai_completion('length')),
            ('audit.length.claude', _claude_model, '', _claude_path, _claude_completion('max_tokens')),
            ('audit.length.gemini', _gemini_model, '/v1beta', _gemini_path, _gemini_completion('MAX_TOKENS')),
        ]

        for conn_name, model, address_path, path, body in cases:
            wrapper = _get_wrapper(llm_test_server, redis_server, conn_name, model, address_path)
            llm_test_server.configure(path, respond_raw=(OK, body))

            response = wrapper.invoke('Write me a novel')
            assert response['finish_reason'] == LLMFinish.Length, conn_name

            # .. and each row is written with the one word the collectors count
            row = _the_one_row(conn_name)
            attrs = _attrs_of(row['id'])

            assert row['status'] == _status_ok, conn_name
            assert attrs[LLMAttr.Model] == (model, None), conn_name
            assert attrs[LLMAttr.Finish_Reason] == (LLMFinish.Length, None), conn_name
            assert attrs[LLMAttr.Output_Tokens] == (str(Output_Tokens), Output_Tokens), conn_name

# ################################################################################################################################

    def test_a_gemini_prompt_block_is_an_error_row_under_200_with_refusal_as_its_finish_reason(
        self,
        llm_test_server:'any_',
        redis_server:'anydict',
    ) -> 'None':

        conn_name = 'audit.gemini.blocked'
        wrapper = _get_wrapper(llm_test_server, redis_server, conn_name, _gemini_model, '/v1beta')

        # Gemini answers HTTP 200 with no candidates and a block reason instead
        blocked = {'promptFeedback': {'blockReason': 'SAFETY'}}
        llm_test_server.configure(_gemini_path, respond_raw=(OK, blocked))

        with pytest.raises(LLMError) as ctx:
            _ = wrapper.invoke('Something the provider will not answer')

        assert ctx.value.finish_reason == LLMFinish.Refusal

        row = _the_one_row(conn_name)

        # The call failed from the caller's side, yet the provider did answer - so the row is an error under `200 OK` ..
        assert row['outcome'] == 'error'
        assert row['status'] == _status_ok

        # .. with the model and the refusal, and no token counts because nothing was completed
        attrs = _attrs_of(row['id'])

        assert attrs[LLMAttr.Model] == (_gemini_model, None)
        assert attrs[LLMAttr.Finish_Reason] == (LLMFinish.Refusal, None)
        assert LLMAttr.Input_Tokens not in attrs
        assert LLMAttr.Output_Tokens not in attrs

# ################################################################################################################################
# ################################################################################################################################

class TestFailureRows:

    def test_a_429_is_an_error_row_under_its_status_line_with_the_model_alone(
        self,
        llm_test_server:'any_',
        redis_server:'anydict',
    ) -> 'None':

        conn_name = 'audit.rate.limited'
        wrapper = _get_wrapper(llm_test_server, redis_server, conn_name)

        rate_limited = {'error': {'message': 'Rate limit reached', 'type': 'rate_limit_error'}}
        llm_test_server.configure(_openai_path, respond_raw=(TOO_MANY_REQUESTS, rate_limited))

        with pytest.raises(LLMError) as ctx:
            _ = wrapper.invoke('Hello')

        assert ctx.value.status_code == TOO_MANY_REQUESTS

        row = _the_one_row(conn_name)

        # An HTTP failure is written under its status line, the one the status code collector reads its 429 off ..
        assert row['event_type'] == AuditEvent.Response_Received
        assert row['outcome'] == 'error'
        assert row['status'] == _status_rate_limited

        # .. and the model is the only attribute - there is no finish reason and there are no tokens
        attrs = _attrs_of(row['id'])
        assert attrs == {LLMAttr.Model: (_openai_model, None)}

# ################################################################################################################################

    def test_a_timeout_is_an_error_row_under_its_transport_status(
        self,
        llm_test_server:'any_',
        redis_server:'anydict',
    ) -> 'None':

        conn_name = 'audit.timeout'
        wrapper = _get_wrapper(llm_test_server, redis_server, conn_name, timeout=_short_timeout)

        # The provider sleeps past the connection's timeout
        llm_test_server.configure(_openai_path, delay=_slow_delay)

        with pytest.raises(Exception):
            _ = wrapper.invoke('Hello')

        row = _the_one_row(conn_name)

        # A request that never got a response is written under its transport status, what the connection failures count ..
        assert row['outcome'] == 'error'
        assert row['status'] == TransportStatus.Timeout
        assert row['duration_ms'] >= _short_timeout * 1000

        # .. with the model alone
        attrs = _attrs_of(row['id'])
        assert attrs == {LLMAttr.Model: (_openai_model, None)}

# ################################################################################################################################

    def test_a_refused_connection_is_an_error_row_under_connection_error(
        self,
        llm_test_server:'any_',
        redis_server:'anydict',
    ) -> 'None':

        conn_name = 'audit.refused'
        wrapper = _get_wrapper(llm_test_server, redis_server, conn_name)

        # Point the one client at a port nothing listens on
        wrapper.config['address'] = f'http://127.0.0.1:{_closed_port()}/v1'
        with wrapper.client() as client:
            client.address = wrapper.config['address']

        with pytest.raises(Exception):
            _ = wrapper.invoke('Hello')

        row = _the_one_row(conn_name)

        assert row['outcome'] == 'error'
        assert row['status'] == TransportStatus.Connection_Error
        assert row['endpoint'] == wrapper.config['address']

        attrs = _attrs_of(row['id'])
        assert attrs == {LLMAttr.Model: (_openai_model, None)}

# ################################################################################################################################

    def test_every_call_leaves_exactly_one_row(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        conn_name = 'audit.one.row.each'
        wrapper = _get_wrapper(llm_test_server, redis_server, conn_name)

        # Two completions and a failure - three calls ..
        _ = wrapper.invoke('One')
        _ = wrapper.invoke('Two')

        rate_limited = {'error': {'message': 'Rate limit reached'}}
        llm_test_server.configure(_openai_path, respond_raw=(TOO_MANY_REQUESTS, rate_limited))

        with pytest.raises(LLMError):
            _ = wrapper.invoke('Three')

        # .. three rows, in order, each with its own status
        rows = _rows_of(conn_name)

        assert [row['status'] for row in rows] == [_status_ok, _status_ok, _status_rate_limited]
        assert [row['outcome'] for row in rows] == ['ok', 'ok', 'error']

# ################################################################################################################################
# ################################################################################################################################
