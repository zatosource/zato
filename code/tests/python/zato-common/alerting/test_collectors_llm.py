# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The LLM collectors - the tokens a connection's calls used add up per connection with the split into input and output,
# a call outside the window adds nothing, a completion cut short lands in the truncations and a refused one in the
# refusals while a plain stop counts nothing, and the outgoing status collector reads an LLM row's 429 into the status
# counts and its timeout into the connection failures with nothing LLM-specific in it.

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.collectors import collect_facts, collect_llm_completion_facts, collect_llm_token_facts, \
    collect_outgoing_status_facts, Measure_Refusals, Measure_Tokens, Measure_Truncations, Window_Seconds_By_Measure_Key
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, AuditSource
from zato.common.audit_log.calls import record_remote_call
from zato.common.audit_log.common import LLMAttr, LLMFinish, TransportStatus
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import stranydict
    datetime = datetime
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-alerting-server'

# The connections the tests seed calls for
_conn_name = 'support.assistant'
_other_conn_name = 'billing.assistant'

# The provider the connections call and the model they ask
_address = 'https://api.openai.com/v1'
_model = 'gpt-4o'

# The window the measures cover in these tests, in seconds
_window_seconds = 3600

# The status line a completion that came back is written under and the one a rate-limited call is
_status_ok = '200 OK'
_status_rate_limited = '429 Too Many Requests'

# ################################################################################################################################
# ################################################################################################################################

def _backdate(event_id:'int', event_time:'datetime') -> 'None':
    """ Moves one stored event back in time.
    """
    engine = get_audit_engine()

    statement = update(event_table)
    statement = statement.where(event_table.c.id == event_id)
    statement = statement.values(event_time_iso=event_time.isoformat())

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def _seed_completion(
    audit_log:'AuditLog',
    *,
    object_name:'str' = _conn_name,
    finish_reason:'str' = LLMFinish.Stop,
    input_tokens:'int' = 100,
    output_tokens:'int' = 50,
    ) -> 'int':
    """ Stores the one row a completion that came back leaves behind - an OK row with the model, the finish reason
    and the two token counts as its attrs, the way the LLM wrapper writes it. Returns the row's id.
    """
    attrs = {
        LLMAttr.Model: _model,
        LLMAttr.Finish_Reason: finish_reason,
        LLMAttr.Input_Tokens: input_tokens,
        LLMAttr.Output_Tokens: output_tokens,
    }

    record_remote_call(audit_log, AuditSource.LLM, object_name, is_ok=True, duration_ms=1200, status=_status_ok,
        endpoint=_address, attrs=attrs)

    out = _newest_event_id()
    return out

# ################################################################################################################################

def _seed_failure(audit_log:'AuditLog', status:'str', *, object_name:'str' = _conn_name) -> 'None':
    """ Stores the one row a call that failed leaves behind - an Error row under the provider's status line or the
    transport status, with the model alone for its attrs, since a failed call has no usage to report.
    """
    attrs = {LLMAttr.Model: _model}

    record_remote_call(audit_log, AuditSource.LLM, object_name, is_ok=False, duration_ms=300, status=status,
        endpoint=_address, attrs=attrs)

# ################################################################################################################################

def _newest_event_id() -> 'int':
    """ The id of the newest row stored.
    """
    engine = get_audit_engine()

    with engine.connect() as connection:
        out = connection.execute(event_table.select().order_by(event_table.c.id.desc()).limit(1)).fetchone()[0]

    return out

# ################################################################################################################################

def _fact_of(facts:'list', object_name:'str') -> 'stranydict':
    """ The one fact of an LLM connection among the facts collected.
    """
    for fact in facts:
        if fact['source'] == AuditSource.LLM:
            if fact['object_name'] == object_name:
                return fact

    raise AssertionError(f'No fact for {object_name} in {facts}')

# ################################################################################################################################
# ################################################################################################################################

class TestTokens:

    def test_the_tokens_of_every_call_add_up_with_their_split(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_completion(audit_log)
        _ = _seed_completion(audit_log)
        _ = _seed_completion(audit_log)

        fact = _fact_of(collect_llm_token_facts(engine, _window_seconds, now), _conn_name)

        assert fact['source'] == AuditSource.LLM
        assert fact['token_count'] == 450
        assert fact['input_token_count'] == 300
        assert fact['output_token_count'] == 150
        assert fact['window_seconds'] == _window_seconds

    def test_a_call_outside_the_window_adds_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_completion(audit_log)
        old_id = _seed_completion(audit_log, input_tokens=5000, output_tokens=5000)
        _backdate(old_id, now - timedelta(seconds=_window_seconds + 60))

        fact = _fact_of(collect_llm_token_facts(engine, _window_seconds, now), _conn_name)

        assert fact['token_count'] == 150

    def test_a_connection_with_no_usage_emits_no_token_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failure(audit_log, _status_rate_limited)
        _seed_failure(audit_log, TransportStatus.Timeout)

        assert collect_llm_token_facts(engine, _window_seconds, now) == []

    def test_each_connection_gets_its_own_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_completion(audit_log)
        _ = _seed_completion(audit_log, object_name=_other_conn_name, input_tokens=10, output_tokens=1)

        facts = collect_llm_token_facts(engine, _window_seconds, now)

        assert _fact_of(facts, _conn_name)['token_count'] == 150
        assert _fact_of(facts, _other_conn_name)['token_count'] == 11

    def test_another_source_asked_for_is_not_measured(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_completion(audit_log)

        assert collect_llm_token_facts(engine, _window_seconds, now, source=AuditSource.REST_Outgoing) == []

        facts = collect_llm_token_facts(engine, _window_seconds, now, source=AuditSource.LLM, object_name=_conn_name)

        assert len(facts) == 1
        assert facts[0]['object_name'] == _conn_name

# ################################################################################################################################
# ################################################################################################################################

class TestCompletions:

    def test_truncations_and_refusals_are_counted_and_a_stop_counts_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_completion(audit_log, finish_reason=LLMFinish.Length)
        _ = _seed_completion(audit_log, finish_reason=LLMFinish.Length)
        _ = _seed_completion(audit_log, finish_reason=LLMFinish.Refusal)
        _ = _seed_completion(audit_log, finish_reason=LLMFinish.Stop)
        _ = _seed_completion(audit_log, finish_reason=LLMFinish.Tool_Use)

        fact = _fact_of(collect_llm_completion_facts(engine, _window_seconds, now), _conn_name)

        assert fact['truncation_count'] == 2
        assert fact['refusal_count'] == 1
        assert fact['window_seconds'] == _window_seconds

    def test_a_connection_that_only_stopped_emits_no_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_completion(audit_log)
        _ = _seed_completion(audit_log)

        assert collect_llm_completion_facts(engine, _window_seconds, now) == []

    def test_a_refusal_written_as_an_error_row_is_counted_too(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A Gemini prompt block - an Error row with a refusal for its finish reason and no usage
        attrs = {LLMAttr.Model: _model, LLMAttr.Finish_Reason: LLMFinish.Refusal}
        record_remote_call(audit_log, AuditSource.LLM, _conn_name, is_ok=False, duration_ms=300, status=_status_ok,
            endpoint=_address, attrs=attrs)

        fact = _fact_of(collect_llm_completion_facts(engine, _window_seconds, now), _conn_name)

        assert fact['refusal_count'] == 1
        assert fact['truncation_count'] == 0

    def test_completions_outside_the_window_are_not_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_completion(audit_log, finish_reason=LLMFinish.Length)
        old_id = _seed_completion(audit_log, finish_reason=LLMFinish.Length)
        _backdate(old_id, now - timedelta(seconds=_window_seconds + 60))

        fact = _fact_of(collect_llm_completion_facts(engine, _window_seconds, now), _conn_name)

        assert fact['truncation_count'] == 1

# ################################################################################################################################
# ################################################################################################################################

class TestStatusAndFailures:

    def test_a_429_lands_in_the_status_counts(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failure(audit_log, _status_rate_limited)
        _seed_failure(audit_log, _status_rate_limited)
        _ = _seed_completion(audit_log)

        fact = _fact_of(collect_outgoing_status_facts(engine, _window_seconds, now), _conn_name)

        assert fact['status_counts'] == {'429': 2, '200': 1}
        assert fact['connection_failure_count'] == 0

    def test_a_timeout_lands_in_the_connection_failures(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failure(audit_log, TransportStatus.Timeout)
        _seed_failure(audit_log, TransportStatus.Connection_Error)

        fact = _fact_of(collect_outgoing_status_facts(engine, _window_seconds, now), _conn_name)

        assert fact['connection_failure_count'] == 2
        assert fact['status_counts'] == {}

# ################################################################################################################################
# ################################################################################################################################

class TestMerged:

    def test_the_merged_fact_carries_every_llm_measure_with_its_window(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_completion(audit_log, finish_reason=LLMFinish.Length)
        _ = _seed_completion(audit_log, finish_reason=LLMFinish.Refusal)
        _ = _seed_completion(audit_log)

        facts = collect_facts(engine, {}, AuditSource.LLM, now, window_seconds=_window_seconds)
        fact = _fact_of(facts, _conn_name)

        assert fact['token_count'] == 450
        assert fact['truncation_count'] == 1
        assert fact['refusal_count'] == 1
        assert fact['total_count'] == 3
        assert fact['error_count'] == 0

        windows = fact[Window_Seconds_By_Measure_Key]

        assert windows[Measure_Tokens] == _window_seconds
        assert windows[Measure_Truncations] == _window_seconds
        assert windows[Measure_Refusals] == _window_seconds

# ################################################################################################################################
# ################################################################################################################################
