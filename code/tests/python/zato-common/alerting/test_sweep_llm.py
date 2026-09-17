# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The sweep over the LLM ruleset - the provider's status codes are matched against the codes in force for a connection,
# the rule's default or the connection's own, the completions cut short and the ones refused each raise their own rule
# off OK rows, the tokens of every call add up against the budget with a window of their own, and a connection with
# alerts off is skipped.

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.engine import AlertDefaults, AlertTransports
from zato.common.alerting.object_config import alert_type_llm, get_defaults as get_object_defaults, LLM_Connection_Config_Key
from zato.common.alerting.seed.rules_llm import llm_rules
from zato.common.alerting.sweep import run_sweep
from zato.common.api import Alerting
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, AuditSource
from zato.common.audit_log.calls import record_remote_call
from zato.common.audit_log.common import LLMAttr, LLMFinish, TransportStatus
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.parser import parse_data_details
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.alerting.sweep import rule_engine_rule_list, SweepResult
    from zato.common.typing_ import any_, anydict, anylist, stranydict
    any_ = any_
    anydict = anydict
    anylist = anylist
    datetime = datetime
    Engine = Engine
    rule_engine_rule_list = rule_engine_rule_list
    stranydict = stranydict
    SweepResult = SweepResult

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-sweep-llm-server'

# The ruleset the connections are judged by
_ruleset_name = 'alerts_llm'

# The connection with settings of its own and the one without any
_conn_name = 'support.assistant'
_other_conn_name = 'billing.assistant'

# The provider the connections call and the model they ask
_address = 'https://api.openai.com/v1'
_model = 'gpt-4o'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# The connection the settings route the explanations through
_llm_name = 'ops.llm'

# The status lines the rows are written under
_status_ok = '200 OK'
_status_rate_limited = '429 Too Many Requests'
_status_server_error = '503 Service Unavailable'

# How many tokens one seeded completion uses
_input_tokens = 100
_output_tokens = 50

# ################################################################################################################################
# ################################################################################################################################

class _TransportRecorder:
    """ A stand-in for the real transports, remembering everything that went out.
    """
    def __init__(self) -> 'None':
        self.emails:'anylist' = []
        self.email_connections:'anylist' = []
        self.invocations:'anylist' = []

    def make(self) -> 'AlertTransports':
        out = AlertTransports()

        def send_email(addresses:'anylist', subject:'str', body:'str', email_connection:'str'='') -> 'None':
            self.emails.append((addresses, subject, body))
            self.email_connections.append(email_connection)

        def invoke_service(service:'str', payload:'stranydict') -> 'None':
            self.invocations.append((service, payload))

        def publish(topic:'str', payload:'stranydict') -> 'None':
            pass

        def http_post(url:'str', payload:'stranydict') -> 'None':
            pass

        out.send_email = send_email
        out.invoke_service = invoke_service
        out.publish = publish
        out.http_post = http_post

        return out

# ################################################################################################################################

def _load_rules() -> 'rule_engine_rule_list':
    """ The seeded LLM rules as runtime rules, all of them active.
    """
    documents, errors = parse_data_details(llm_rules, _ruleset_name)
    assert errors == []

    loaded = load_documents(documents)

    # Our response to produce
    out = []

    for full_name in loaded.rule_names:
        out.append(loaded.manager[full_name])

    return out

# ################################################################################################################################

def _backdate(engine:'Engine', now:'datetime', seconds_back:'int') -> 'None':
    """ Moves the newest stored row back in time.
    """
    with engine.connect() as connection:
        event_id = connection.execute(event_table.select().order_by(event_table.c.id.desc()).limit(1)).fetchone()[0]

    event_time_iso = (now - timedelta(seconds=seconds_back)).isoformat()

    statement = update(event_table)
    statement = statement.where(event_table.c.id == event_id)
    statement = statement.values(event_time_iso=event_time_iso)

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def _seed_completion(audit_log:'AuditLog', engine:'Engine', now:'datetime', *, object_name:'str'=_conn_name,
    finish_reason:'str'=LLMFinish.Stop, seconds_back:'int'=0) -> 'None':
    """ Stores the one OK row a completion that came back leaves behind, with the model, the finish reason and the
    token counts as its attrs, moved back in time if asked to.
    """
    attrs = {
        LLMAttr.Model: _model,
        LLMAttr.Finish_Reason: finish_reason,
        LLMAttr.Input_Tokens: _input_tokens,
        LLMAttr.Output_Tokens: _output_tokens,
    }

    record_remote_call(audit_log, AuditSource.LLM, object_name, is_ok=True, duration_ms=1200, status=_status_ok,
        endpoint=_address, attrs=attrs)

    if seconds_back:
        _backdate(engine, now, seconds_back)

# ################################################################################################################################

def _seed_failure(audit_log:'AuditLog', engine:'Engine', now:'datetime', status:'str', *, object_name:'str'=_conn_name,
    seconds_back:'int'=0) -> 'None':
    """ Stores the one Error row a call that failed leaves behind, under the provider's status line or the transport status.
    """
    attrs = {LLMAttr.Model: _model}

    record_remote_call(audit_log, AuditSource.LLM, object_name, is_ok=False, duration_ms=300, status=status,
        endpoint=_address, attrs=attrs)

    if seconds_back:
        _backdate(engine, now, seconds_back)

# ################################################################################################################################

def _seed_failures(audit_log:'AuditLog', engine:'Engine', now:'datetime', count:'int', status:'str', *,
    object_name:'str'=_conn_name, seconds_back:'int'=0) -> 'None':
    """ Stores the given number of failed calls, each followed by one that came back, so the failures never form
    an unbroken streak and only the rules about counts and rates see them.
    """
    for _ in range(count):
        _seed_failure(audit_log, engine, now, status, object_name=object_name, seconds_back=seconds_back)
        _seed_completion(audit_log, engine, now, object_name=object_name, seconds_back=seconds_back)

# ################################################################################################################################

def _seed_completions(audit_log:'AuditLog', engine:'Engine', now:'datetime', count:'int', *,
    object_name:'str'=_conn_name, finish_reason:'str'=LLMFinish.Stop, seconds_back:'int'=0) -> 'None':
    """ Stores the given number of completions that came back with the given finish reason.
    """
    for _ in range(count):
        _seed_completion(audit_log, engine, now, object_name=object_name, finish_reason=finish_reason,
            seconds_back=seconds_back)

# ################################################################################################################################

def _new_object_settings(**values:'any_') -> 'anydict':
    """ The object settings of one LLM connection at the defaults, with the given values on top.
    The explaining LLM stays out of it unless a test asks for it, so the actions run directly and can be observed.
    """
    settings = get_object_defaults(alert_type_llm)
    settings['use_llm'] = False
    settings.update(values)

    out = {alert_type_llm: {_conn_name: settings}}
    return out

# ################################################################################################################################

def _run_sweep(engine:'Engine', audit_log:'AuditLog', now:'datetime', cid:'str',
    object_settings:'anydict | None') -> 'tuple[SweepResult, _TransportRecorder]':
    """ Runs one sweep of the seeded ruleset with the given object settings.
    """
    defaults = AlertDefaults()
    defaults.email_to = _addresses

    recorder = _TransportRecorder()
    rules = _load_rules()

    result = run_sweep(engine, rules, {}, AuditSource.LLM, recorder.make(), audit_log, cid, now,
        defaults=defaults, object_settings=object_settings)

    return result, recorder

# ################################################################################################################################

def _rule_names(result:'SweepResult') -> 'list':
    """ The names of the rules that dispatched an action, in order.
    """
    out = []
    for rule_name, _ in result.dispatched:
        out.append(rule_name)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestStatusCodes:

    def test_three_429s_fire_on_the_rules_default_codes(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three rate limits out of thirty-three calls - under the error rate's tenth, at the default threshold of three codes
        _seed_failures(audit_log, engine, now, 3, _status_rate_limited)
        _seed_completions(audit_log, engine, now, 27)

        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-codes-default', None)

        assert _rule_names(result) == ['Status_Codes']
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert '3 responses with a status the connection alerts on' in body
        assert '(429 x3)' in body

# ################################################################################################################################

    def test_the_connections_own_codes_stand_in_for_the_rules_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 3, _status_rate_limited)
        _seed_completions(audit_log, engine, now, 27)

        # The default codes count the 429s ..
        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-codes-own-1', None)
        assert _rule_names(result) == ['Status_Codes']

        # .. a connection naming the 5xx class alone does not ..
        object_settings = _new_object_settings(status_codes='5xx')
        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-codes-own-2', object_settings)
        assert result.raised_count == 0

        # .. and once it names the 429 it counts them again.
        object_settings = _new_object_settings(status_codes='429')
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-codes-own-3', object_settings)
        assert _rule_names(result) == ['Status_Codes']

        _, _, body = recorder.emails[0]
        assert '(429 x3)' in body

# ################################################################################################################################

    def test_a_5xx_counts_under_its_class(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 3, _status_server_error)
        _seed_completions(audit_log, engine, now, 27)

        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-codes-5xx', None)

        assert _rule_names(result) == ['Status_Codes']

        _, _, body = recorder.emails[0]
        assert '(503 x3)' in body

# ################################################################################################################################

    def test_three_timeouts_are_connection_failures_and_not_status_codes(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 3, TransportStatus.Timeout)
        _seed_completions(audit_log, engine, now, 27)

        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-timeouts', None)

        assert _rule_names(result) == ['Connection_Failures']

        _, _, body = recorder.emails[0]
        assert '3 timeouts or connection failures' in body
        assert 'status code' not in body

# ################################################################################################################################
# ################################################################################################################################

class TestCompletions:

    def test_three_truncations_fire_off_ok_rows(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_completions(audit_log, engine, now, 3, finish_reason=LLMFinish.Length)
        _seed_completions(audit_log, engine, now, 27)

        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-truncations', None)

        assert _rule_names(result) == ['Truncated_Completions']

        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert '3 truncated completions' in body
        assert 'refusal' not in body

# ################################################################################################################################

    def test_three_refusals_fire_off_ok_rows(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_completions(audit_log, engine, now, 3, finish_reason=LLMFinish.Refusal)
        _seed_completions(audit_log, engine, now, 27)

        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-refusals', None)

        assert _rule_names(result) == ['Refusals']

        _, _, body = recorder.emails[0]
        assert '3 refusals' in body
        assert 'truncated' not in body

# ################################################################################################################################

    def test_two_of_each_fire_nothing_at_the_default_thresholds(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_completions(audit_log, engine, now, 2, finish_reason=LLMFinish.Length)
        _seed_completions(audit_log, engine, now, 2, finish_reason=LLMFinish.Refusal)
        _seed_completions(audit_log, engine, now, 27)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-under-1', None)
        assert result.raised_count == 0

        # The connection's own thresholds of two count them both
        object_settings = _new_object_settings(truncations=2, refusals=2)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-under-2', object_settings)

        assert sorted(_rule_names(result)) == ['Refusals', 'Truncated_Completions']

# ################################################################################################################################

    def test_the_truncations_window_of_the_connection_applies_to_the_truncations_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three truncations half an hour back - outside the rule's five minutes, inside the connection's own hour
        _seed_completions(audit_log, engine, now, 3, finish_reason=LLMFinish.Length, seconds_back=1800)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-trunc-window-1', None)
        assert result.raised_count == 0

        object_settings = _new_object_settings(truncations_window=3600)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-trunc-window-2', object_settings)

        assert _rule_names(result) == ['Truncated_Completions']

        _, _, body = recorder.emails[0]
        assert '3 truncated completions over 3600s' in body

# ################################################################################################################################
# ################################################################################################################################

class TestTokenBudget:

    def test_a_sum_over_the_budget_fires_and_one_under_it_does_not(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Twenty completions of 150 tokens each - 3000 tokens, far under the default ten million
        _seed_completions(audit_log, engine, now, 20)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-budget-1', None)
        assert result.raised_count == 0

        # A connection allowing 2500 tokens a day is over its budget
        object_settings = _new_object_settings(token_budget=2500)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-budget-2', object_settings)

        assert _rule_names(result) == ['Token_Budget']

        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert '3,000 tokens (2,000 in, 1,000 out)' in body

# ################################################################################################################################

    def test_a_sum_at_the_budget_reaches_it_and_one_token_under_does_not(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_completions(audit_log, engine, now, 20)

        # A connection allowing one more than the sum is under its budget ..
        object_settings = _new_object_settings(token_budget=3001)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-budget-edge-1', object_settings)
        assert result.raised_count == 0

        # .. and one allowing exactly the sum has reached it.
        object_settings = _new_object_settings(token_budget=3000)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-budget-edge-2', object_settings)
        assert _rule_names(result) == ['Token_Budget']

# ################################################################################################################################

    def test_the_budget_window_of_the_connection_applies_to_the_tokens_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Twenty completions two hours back - inside the rule's day, outside a connection's own hour
        _seed_completions(audit_log, engine, now, 20, seconds_back=7200)

        object_settings = _new_object_settings(token_budget=2500)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-budget-window-1', object_settings)
        assert _rule_names(result) == ['Token_Budget']

        object_settings = _new_object_settings(token_budget=2500, token_budget_window=3600)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-budget-window-2', object_settings)
        assert result.raised_count == 0

# ################################################################################################################################

    def test_the_connections_own_llm_connection_rides_in_the_outcome(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_completions(audit_log, engine, now, 20)

        object_settings = _new_object_settings(token_budget=2500, use_llm=True, llm_connection=_llm_name)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-budget-llm', object_settings)

        assert _rule_names(result) == ['Token_Budget']
        assert recorder.emails == []
        assert len(recorder.invocations) == 1

        service, payload = recorder.invocations[0]
        assert service == Alerting.Service_Explain
        assert payload['source'] == AuditSource.LLM
        assert payload['object_name'] == _conn_name
        assert payload['action_config'][LLM_Connection_Config_Key] == _llm_name
        assert payload['fact']['token_count'] == 3000
        assert payload['fact']['input_token_count'] == 2000
        assert payload['fact']['output_token_count'] == 1000
        assert payload['thresholds'] == {'token_budget': 2500, 'window_seconds': 86400}

# ################################################################################################################################
# ################################################################################################################################

class TestTheOtherRules:

    def test_a_connection_with_alerts_off_is_skipped_while_another_still_raises(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_completions(audit_log, engine, now, 3, finish_reason=LLMFinish.Length)
        _seed_completions(audit_log, engine, now, 3, finish_reason=LLMFinish.Length, object_name=_other_conn_name)

        object_settings = _new_object_settings(is_active=False)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-off', object_settings)

        assert _rule_names(result) == ['Truncated_Completions']
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _other_conn_name in body
        assert _conn_name not in body

# ################################################################################################################################

    def test_the_connections_own_latency_is_in_seconds_and_takes_fractions(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Thirty completions of 1200 ms each - under the rule's ten seconds ..
        _seed_completions(audit_log, engine, now, 30)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-latency-1', None)
        assert result.raised_count == 0

        # .. over a connection's own warning of one second and under its error of one and a half ..
        object_settings = _new_object_settings(warning_latency=1, error_latency=1.5)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-llm-latency-2', object_settings)

        assert _rule_names(result) == ['Slow_Completions']

        _, _, body = recorder.emails[0]
        assert 'average duration 1200ms' in body

        # .. and over its error once that is 1.1 seconds.
        object_settings = _new_object_settings(warning_latency=0.5, error_latency=1.1)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-latency-3', object_settings)

        assert _rule_names(result) == ['Slow_Completions_Error']

# ################################################################################################################################

    def test_three_failures_in_a_row_mean_the_connection_is_down(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_completions(audit_log, engine, now, 30)
        _seed_failure(audit_log, engine, now, _status_rate_limited)
        _seed_failure(audit_log, engine, now, _status_rate_limited)
        _seed_failure(audit_log, engine, now, _status_rate_limited)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-llm-down', None)

        assert 'Connection_Down' in _rule_names(result)
        assert 'Status_Codes' in _rule_names(result)

# ################################################################################################################################
# ################################################################################################################################
