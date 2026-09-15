# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The sweep over the MCP ruleset - a gateway's own invalid-call threshold fires where the default stays quiet, the two
# slow rules hand over at the error value with latencies typed in seconds, the tool count fires off the gateway's own
# number with no audit rows at all and stays quiet under the gateway's own maximum, a repeated call names the session
# and the tool, the volume reads as a size, and a gateway with alerts off is skipped while another still raises.

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.engine import AlertDefaults, AlertTransports
from zato.common.alerting.object_config import alert_type_mcp, get_defaults as get_object_defaults
from zato.common.alerting.seed.rules_mcp import mcp_rules
from zato.common.alerting.sweep import run_sweep
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import MCPAttr
from zato.common.json_internal import dumps
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.parser import parse_data_details
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.alerting.sweep import rule_engine_rule_list, SweepResult
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strintdict
    any_ = any_
    anydict = anydict
    anylist = anylist
    datetime = datetime
    Engine = Engine
    rule_engine_rule_list = rule_engine_rule_list
    stranydict = stranydict
    strintdict = strintdict
    SweepResult = SweepResult

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-sweep-mcp-server'

# The ruleset the gateways are judged by
_ruleset_name = 'alerts_mcp'

# The gateway with settings of its own and the one without any
_gateway_name = 'orders.gateway'
_other_gateway_name = 'billing.gateway'

# The tool the agents call, the session they call it from and the definition they authenticate with
_tool_name = 'orders.get'
_session_id = 'session-1'
_sec_def_name = 'orders.agent'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# The JSON-RPC error code of arguments the schema refused
_error_code_invalid_params = -32602

# ################################################################################################################################
# ################################################################################################################################

class _TransportRecorder:
    """ A stand-in for the real transports, remembering everything that went out.
    """
    def __init__(self) -> 'None':
        self.emails:'anylist' = []
        self.invocations:'anylist' = []

    def make(self) -> 'AlertTransports':
        out = AlertTransports()

        def send_email(addresses:'anylist', subject:'str', body:'str', email_connection:'str'='') -> 'None':
            self.emails.append((addresses, subject, body))

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
    """ The seeded MCP rules as runtime rules, all of them active - the silence rule ships off through the seed table,
    which this loader does not read, so it is muted per gateway by the traffic_expected switch instead.
    """
    documents, errors = parse_data_details(mcp_rules, _ruleset_name)
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

def _seed_tool_call(audit_log:'AuditLog', engine:'Engine', now:'datetime', *, object_name:'str'=_gateway_name,
    is_ok:'bool'=True, size:'int'=1000, duration_ms:'int'=100, error_code:'int | None'=None, seconds_back:'int'=0,
    session_id:'str'=_session_id) -> 'None':
    """ Stores the one row a tool call leaves behind, with the attributes the gateway writes, moved back in time if asked to.
    """
    attrs:'stranydict' = {MCPAttr.Method: 'tools/call', MCPAttr.Request_Size: 200}
    data:'stranydict' = {'method': 'tools/call'}

    if error_code is not None:
        attrs[MCPAttr.Error_Code] = error_code
        data['error_code'] = error_code
        data['error_message'] = 'Invalid params'

    if is_ok:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    _ = audit_log.insert(AuditSource.MCP, AuditEvent.MCP_Tools_Call, object_name, ext_client_id=_sec_def_name,
        endpoint=_tool_name, sub_key=session_id, size=size, outcome=outcome, duration_ms=duration_ms,
        data=dumps(data), attrs=attrs)

    if seconds_back:
        _backdate(engine, now, seconds_back)

# ################################################################################################################################

def _seed_tool_calls(audit_log:'AuditLog', engine:'Engine', now:'datetime', count:'int', **kwargs:'any_') -> 'None':
    """ Stores the given number of tool calls of one shape, each from a session of its own unless the caller names one,
    so that a crowd of calls never reads as one agent repeating itself.
    """
    for index in range(count):
        if 'session_id' in kwargs:
            _seed_tool_call(audit_log, engine, now, **kwargs)
        else:
            _seed_tool_call(audit_log, engine, now, session_id=f'session-{index}', **kwargs)

# ################################################################################################################################

def _seed_invalid_calls(audit_log:'AuditLog', engine:'Engine', now:'datetime', count:'int', *,
    object_name:'str'=_gateway_name) -> 'None':
    """ Stores the given number of calls whose arguments the schema refused, each followed by eleven that went well,
    so the failures never form a streak, stay under the error rate's tenth and only the invalid-call rule sees them.
    """
    for index in range(count):
        _seed_tool_call(audit_log, engine, now, object_name=object_name, is_ok=False, size=0,
            error_code=_error_code_invalid_params, session_id=f'invalid-{index}')

        for ok_index in range(11):
            _seed_tool_call(audit_log, engine, now, object_name=object_name, session_id=f'ok-{index}-{ok_index}')

# ################################################################################################################################

def _new_object_settings(**values:'any_') -> 'anydict':
    """ The object settings of one gateway at the defaults, with the given values on top.
    The explaining LLM stays out of it, so the actions run directly and can be observed.
    """
    settings = get_object_defaults(alert_type_mcp)
    settings['use_llm'] = False
    settings.update(values)

    out = {alert_type_mcp: {_gateway_name: settings}}
    return out

# ################################################################################################################################

def _run_sweep(engine:'Engine', audit_log:'AuditLog', now:'datetime', cid:'str', object_settings:'anydict | None',
    *, tool_counts:'strintdict | None'=None) -> 'tuple[SweepResult, _TransportRecorder]':
    """ Runs one sweep of the seeded ruleset with the given object settings and tool counts.
    """
    defaults = AlertDefaults()
    defaults.email_to = _addresses

    recorder = _TransportRecorder()
    rules = _load_rules()

    # A gateway with no settings of its own and no traffic_expected has its silence rule muted by its defaults,
    # so every sweep runs with settings for the gateway under test unless a test hands in its own
    if object_settings is None:
        object_settings = _new_object_settings()

    result = run_sweep(engine, rules, {}, AuditSource.MCP, recorder.make(), audit_log, cid, now,
        defaults=defaults, object_settings=object_settings, tool_counts=tool_counts)

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

class TestInvalidCalls:

    def test_two_invalid_calls_are_quiet_by_default_and_fire_on_the_gateways_own_two(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Two invalid calls among twenty-four - under the error rate's tenth and under the default five
        _seed_invalid_calls(audit_log, engine, now, 2)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-invalid-default', None)
        assert result.raised_count == 0

        object_settings = _new_object_settings(invalid_calls=2)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mcp-invalid-own', object_settings)

        assert _rule_names(result) == ['Invalid_Tool_Calls']
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _gateway_name in body
        assert '2 invalid tool calls' in body

# ################################################################################################################################

    def test_the_invalid_calls_window_of_the_gateway_applies_to_the_invalid_calls_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Five invalid calls half an hour back - outside the rule's five minutes, inside the gateway's own hour
        for index in range(5):
            _seed_tool_call(audit_log, engine, now, is_ok=False, size=0, error_code=_error_code_invalid_params,
                seconds_back=1800, session_id=f'invalid-{index}')
            for ok_index in range(11):
                _seed_tool_call(audit_log, engine, now, seconds_back=1800, session_id=f'ok-{index}-{ok_index}')

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-invalid-window-1', None)
        assert result.raised_count == 0

        object_settings = _new_object_settings(invalid_calls_window=3600)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mcp-invalid-window-2', object_settings)

        assert _rule_names(result) == ['Invalid_Tool_Calls']

        _, _, body = recorder.emails[0]
        assert '5 invalid tool calls over 3600s' in body

# ################################################################################################################################
# ################################################################################################################################

class TestSlowToolCalls:

    def test_the_warning_yields_to_the_error_above_the_error_value(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Thirty calls of 1200 ms each - under the rule's five seconds ..
        _seed_tool_calls(audit_log, engine, now, 30, duration_ms=1200)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-latency-1', None)
        assert result.raised_count == 0

        # .. over a gateway's own warning of one second and under its error of one and a half ..
        object_settings = _new_object_settings(warning_latency=1, error_latency=1.5)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mcp-latency-2', object_settings)

        assert _rule_names(result) == ['Slow_Tool_Calls']

        _, _, body = recorder.emails[0]
        assert 'average duration 1200ms' in body

        # .. and over its error once that is 1.1 seconds, the warning yielding.
        object_settings = _new_object_settings(warning_latency=0.5, error_latency=1.1)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-latency-3', object_settings)

        assert _rule_names(result) == ['Slow_Tool_Calls_Error']

# ################################################################################################################################
# ################################################################################################################################

class TestTooManyTools:

    def test_thirty_tools_fire_with_no_audit_rows_at_all(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mcp-tools-1', None, tool_counts={_gateway_name: 30})

        assert _rule_names(result) == ['Too_Many_Tools']
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _gateway_name in body
        assert '30 tools exposed' in body

# ################################################################################################################################

    def test_twenty_five_tools_stay_quiet_under_the_gateways_own_thirty(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # At the default of twenty-five the count has reached the number ..
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-tools-2', None, tool_counts={_gateway_name: 25})
        assert _rule_names(result) == ['Too_Many_Tools']

        # .. and under the gateway's own thirty it has not.
        object_settings = _new_object_settings(max_tools=30)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-tools-3', object_settings, tool_counts={_gateway_name: 25})
        assert result.raised_count == 0

# ################################################################################################################################
# ################################################################################################################################

class TestRepeatedCallsAndVolume:

    def test_a_repeated_call_names_the_session_and_the_tool(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Six calls of one tool from one session - under the default twenty, over a gateway's own five
        _seed_tool_calls(audit_log, engine, now, 6, session_id=_session_id)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-repeat-1', None)
        assert result.raised_count == 0

        object_settings = _new_object_settings(repeat_calls=5)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mcp-repeat-2', object_settings)

        assert _rule_names(result) == ['Repeated_Calls']

        _, _, body = recorder.emails[0]
        assert f'session {_session_id} called {_tool_name} 6 times' in body

# ################################################################################################################################

    def test_the_volume_over_the_budget_fires_and_reads_as_a_size(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Four responses of half a megabyte each - two megabytes, far under the default hundred
        _seed_tool_calls(audit_log, engine, now, 4, size=500000)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-volume-1', None)
        assert result.raised_count == 0

        # A gateway allowing a megabyte a day is over its budget
        object_settings = _new_object_settings(volume_budget=1000000)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mcp-volume-2', object_settings)

        assert _rule_names(result) == ['Response_Volume']

        _, _, body = recorder.emails[0]
        assert '2 megabytes of responses' in body

# ################################################################################################################################
# ################################################################################################################################

class TestTheOtherRules:

    def test_a_gateway_with_alerts_off_is_skipped_while_another_still_raises(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_invalid_calls(audit_log, engine, now, 5)
        _seed_invalid_calls(audit_log, engine, now, 5, object_name=_other_gateway_name)

        object_settings = _new_object_settings(is_active=False)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mcp-off', object_settings)

        assert _rule_names(result) == ['Invalid_Tool_Calls']
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _other_gateway_name in body
        assert _gateway_name not in body

# ################################################################################################################################

    def test_three_failed_tool_calls_in_a_row_mean_the_gateway_is_failing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_tool_calls(audit_log, engine, now, 30)
        _seed_tool_calls(audit_log, engine, now, 3, is_ok=False)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-failing', None)

        assert 'Gateway_Failing' in _rule_names(result)

# ################################################################################################################################

    def test_a_silent_gateway_fires_only_once_it_expects_traffic(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # One call two hours back and nothing since
        _seed_tool_call(audit_log, engine, now, seconds_back=7200)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-silent-1', None)
        assert result.raised_count == 0

        object_settings = _new_object_settings(traffic_expected=True)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mcp-silent-2', object_settings)

        assert 'Gateway_Silent' in _rule_names(result)

# ################################################################################################################################
# ################################################################################################################################
