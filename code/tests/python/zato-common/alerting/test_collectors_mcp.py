# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The MCP gateway collectors over rows inserted the way the gateway writes them, with the attributes next to each
# row - the invalid calls read the error code, the rejections the reject kind, the truncations the was_truncated flag,
# the throttled ones their own event type, the volume adds up the size column, the repeat calls pick the one session
# and tool with the most calls and never add two sessions together, and the tool count comes off the gateway itself,
# so a gateway with no rows at all is measured too. The shared rate collectors read a gateway's tool calls alone.

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.collectors import collect_auth_failure_facts, collect_consecutive_failure_facts, \
    collect_error_rate_facts, collect_facts, collect_latency_facts, Measure_Invalid_Calls, Measure_Repeat_Calls, \
    Measure_Volume, Window_Seconds_By_Measure_Key
from zato.common.alerting.collectors.mcp import collect_invalid_call_facts, collect_mcp_truncation_facts, \
    collect_rejection_facts, collect_repeat_call_facts, collect_throttled_facts, collect_tool_count_facts, \
    collect_volume_facts, Error_Code_Invalid_Params, Error_Code_Method_Not_Found
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import MCPAttr
from zato.common.json_internal import dumps
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

# The gateways the tests seed calls for
_gateway_name = 'orders.gateway'
_other_gateway_name = 'billing.gateway'

# The tools the agents call and the sessions they call them from
_tool_name = 'orders.get'
_other_tool_name = 'orders.list'
_session_id = 'session-1'
_other_session_id = 'session-2'

# The security definition the callers authenticate with
_sec_def_name = 'orders.agent'

# The window the measures cover in these tests, in seconds
_window_seconds = 3600

# The method attribute every row carries
_method_tools_call = 'tools/call'

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

def _newest_event_id() -> 'int':
    """ The id of the newest row stored.
    """
    engine = get_audit_engine()

    with engine.connect() as connection:
        out = connection.execute(event_table.select().order_by(event_table.c.id.desc()).limit(1)).fetchone()[0]

    return out

# ################################################################################################################################

def _seed_tool_call(
    audit_log:'AuditLog',
    *,
    object_name:'str' = _gateway_name,
    tool_name:'str' = _tool_name,
    session_id:'str' = _session_id,
    size:'int' = 1000,
    duration_ms:'int' = 100,
    is_ok:'bool' = True,
    attrs:'stranydict | None' = None,
    ) -> 'int':
    """ Stores the one row a tool call leaves behind, with the method and the request's bytes as its attributes
    the way the gateway writes them and whatever else the test adds. Returns the row's id.
    """
    row_attrs:'stranydict' = {MCPAttr.Method: _method_tools_call, MCPAttr.Request_Size: 200}

    if attrs:
        row_attrs.update(attrs)

    if is_ok:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    _ = audit_log.insert(AuditSource.MCP, AuditEvent.MCP_Tools_Call, object_name, ext_client_id=_sec_def_name,
        endpoint=tool_name, sub_key=session_id, size=size, outcome=outcome, duration_ms=duration_ms,
        data=dumps({'method': _method_tools_call}), attrs=row_attrs)

    out = _newest_event_id()
    return out

# ################################################################################################################################

def _seed_invalid_call(audit_log:'AuditLog', error_code:'int', *, object_name:'str'=_gateway_name) -> 'int':
    """ Stores a tool call the gateway answered with a JSON-RPC error - the error code rides as an attribute.
    """
    out = _seed_tool_call(audit_log, object_name=object_name, is_ok=False, size=0,
        attrs={MCPAttr.Error_Code: error_code})
    return out

# ################################################################################################################################

def _seed_other_event(audit_log:'AuditLog', event_type:'str', *, is_ok:'bool'=True, duration_ms:'int'=5000) -> 'None':
    """ Stores a row that is not a tool call - an initialize or a tools/list - with a duration of its own.
    """
    if is_ok:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    _ = audit_log.insert(AuditSource.MCP, event_type, _gateway_name, ext_client_id=_sec_def_name,
        outcome=outcome, duration_ms=duration_ms, attrs={MCPAttr.Method: event_type, MCPAttr.Request_Size: 100})

# ################################################################################################################################

def _seed_auth_failure(audit_log:'AuditLog') -> 'None':
    """ Stores the row of a request whose credentials matched none of the gateway's definitions.
    """
    _ = audit_log.insert(AuditSource.MCP, AuditEvent.Auth_Failed, _gateway_name, outcome=AuditOutcome.Error)

# ################################################################################################################################

def _seed_rate_limited(audit_log:'AuditLog', *, object_name:'str'=_gateway_name) -> 'None':
    """ Stores the row of a request a caller's own rate limit answered 429.
    """
    _ = audit_log.insert(AuditSource.MCP, AuditEvent.Rate_Limited, object_name, ext_client_id=_sec_def_name,
        outcome=AuditOutcome.Error, attrs={MCPAttr.Method: 'rate-limited', MCPAttr.Request_Size: 100})

# ################################################################################################################################

def _fact_of(facts:'list', object_name:'str') -> 'stranydict':
    """ The one fact of a gateway among the facts collected.
    """
    for fact in facts:
        if fact['source'] == AuditSource.MCP:
            if fact['object_name'] == object_name:
                return fact

    raise AssertionError(f'No fact for {object_name} in {facts}')

# ################################################################################################################################
# ################################################################################################################################

class TestInvalidCalls:

    def test_both_error_codes_count_and_a_backend_error_does_not(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_invalid_call(audit_log, Error_Code_Method_Not_Found)
        _ = _seed_invalid_call(audit_log, Error_Code_Method_Not_Found)
        _ = _seed_invalid_call(audit_log, Error_Code_Invalid_Params)

        # An internal error is the backend's and a call that went well is nobody's mistake
        _ = _seed_tool_call(audit_log, is_ok=False, attrs={MCPAttr.Error_Code: -32603})
        _ = _seed_tool_call(audit_log)

        fact = _fact_of(collect_invalid_call_facts(engine, _window_seconds, now), _gateway_name)

        assert fact['invalid_call_count'] == 3
        assert fact['window_seconds'] == _window_seconds

    def test_a_call_outside_the_window_adds_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_invalid_call(audit_log, Error_Code_Method_Not_Found)
        old_id = _seed_invalid_call(audit_log, Error_Code_Method_Not_Found)
        _backdate(old_id, now - timedelta(seconds=_window_seconds + 60))

        fact = _fact_of(collect_invalid_call_facts(engine, _window_seconds, now), _gateway_name)

        assert fact['invalid_call_count'] == 1

    def test_a_gateway_with_no_invalid_calls_emits_no_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_tool_call(audit_log)
        _ = _seed_tool_call(audit_log)

        assert collect_invalid_call_facts(engine, _window_seconds, now) == []

    def test_each_gateway_gets_its_own_fact_and_another_source_is_not_measured(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_invalid_call(audit_log, Error_Code_Method_Not_Found)
        _ = _seed_invalid_call(audit_log, Error_Code_Invalid_Params, object_name=_other_gateway_name)
        _ = _seed_invalid_call(audit_log, Error_Code_Invalid_Params, object_name=_other_gateway_name)

        facts = collect_invalid_call_facts(engine, _window_seconds, now)

        assert _fact_of(facts, _gateway_name)['invalid_call_count'] == 1
        assert _fact_of(facts, _other_gateway_name)['invalid_call_count'] == 2

        assert collect_invalid_call_facts(engine, _window_seconds, now, source=AuditSource.LLM) == []

        facts = collect_invalid_call_facts(engine, _window_seconds, now, source=AuditSource.MCP, object_name=_gateway_name)
        assert len(facts) == 1
        assert facts[0]['object_name'] == _gateway_name

# ################################################################################################################################
# ################################################################################################################################

class TestRejectionsAndTruncations:

    def test_a_rejected_response_counts_by_its_reject_kind(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_tool_call(audit_log, is_ok=False, attrs={MCPAttr.Reject_Kind: 'size'})
        _ = _seed_tool_call(audit_log, is_ok=False, attrs={MCPAttr.Reject_Kind: 'markup'})
        _ = _seed_tool_call(audit_log)

        fact = _fact_of(collect_rejection_facts(engine, _window_seconds, now), _gateway_name)

        assert fact['rejection_count'] == 2
        assert collect_mcp_truncation_facts(engine, _window_seconds, now) == []

    def test_a_truncated_response_counts_by_its_flag(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        attrs = {MCPAttr.Was_Truncated: True, MCPAttr.Tokens_Before: 9000, MCPAttr.Tokens_After: 2000}

        _ = _seed_tool_call(audit_log, attrs=attrs)
        _ = _seed_tool_call(audit_log, attrs=attrs)
        _ = _seed_tool_call(audit_log, attrs=attrs)
        _ = _seed_tool_call(audit_log)

        fact = _fact_of(collect_mcp_truncation_facts(engine, _window_seconds, now), _gateway_name)

        assert fact['truncation_count'] == 3
        assert collect_rejection_facts(engine, _window_seconds, now) == []

# ################################################################################################################################
# ################################################################################################################################

class TestThrottledCallers:

    def test_rate_limited_rows_count_and_tool_calls_do_not(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_rate_limited(audit_log)
        _seed_rate_limited(audit_log)
        _seed_rate_limited(audit_log, object_name=_other_gateway_name)
        _ = _seed_tool_call(audit_log)

        facts = collect_throttled_facts(engine, _window_seconds, now)

        assert _fact_of(facts, _gateway_name)['throttled_count'] == 2
        assert _fact_of(facts, _other_gateway_name)['throttled_count'] == 1

    def test_a_gateway_that_throttled_nobody_emits_no_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_tool_call(audit_log)
        _seed_auth_failure(audit_log)

        assert collect_throttled_facts(engine, _window_seconds, now) == []

# ################################################################################################################################
# ################################################################################################################################

class TestVolume:

    def test_the_sizes_of_every_tool_call_add_up(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_tool_call(audit_log, size=1000)
        _ = _seed_tool_call(audit_log, size=2500)
        _ = _seed_tool_call(audit_log, size=500, is_ok=False)

        # A tools/list has a size too and is not a tool call
        _seed_other_event(audit_log, AuditEvent.MCP_Tools_List)

        fact = _fact_of(collect_volume_facts(engine, _window_seconds, now), _gateway_name)

        assert fact['volume_bytes'] == 4000
        assert fact['window_seconds'] == _window_seconds

    def test_a_call_outside_the_window_adds_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_tool_call(audit_log, size=1000)
        old_id = _seed_tool_call(audit_log, size=90000)
        _backdate(old_id, now - timedelta(seconds=_window_seconds + 60))

        fact = _fact_of(collect_volume_facts(engine, _window_seconds, now), _gateway_name)

        assert fact['volume_bytes'] == 1000

    def test_a_gateway_whose_responses_were_all_empty_emits_no_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_tool_call(audit_log, size=0)

        assert collect_volume_facts(engine, _window_seconds, now) == []

# ################################################################################################################################
# ################################################################################################################################

class TestRepeatCalls:

    def test_the_worst_session_and_tool_are_picked(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # One session calling one tool four times, the same session calling another tool twice
        for _ in range(4):
            _ = _seed_tool_call(audit_log, tool_name=_tool_name, session_id=_session_id)

        for _ in range(2):
            _ = _seed_tool_call(audit_log, tool_name=_other_tool_name, session_id=_session_id)

        fact = _fact_of(collect_repeat_call_facts(engine, _window_seconds, now), _gateway_name)

        assert fact['repeat_call_count'] == 4
        assert fact['repeat_call_tool'] == _tool_name
        assert fact['repeat_call_session'] == _session_id
        assert fact['window_seconds'] == _window_seconds

    def test_two_sessions_calling_the_same_tool_never_add_up(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        for _ in range(3):
            _ = _seed_tool_call(audit_log, session_id=_session_id)

        for _ in range(3):
            _ = _seed_tool_call(audit_log, session_id=_other_session_id)

        fact = _fact_of(collect_repeat_call_facts(engine, _window_seconds, now), _gateway_name)

        assert fact['repeat_call_count'] == 3
        assert fact['repeat_call_tool'] == _tool_name

    def test_a_session_that_called_once_and_a_call_without_a_session_do_not_repeat(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_tool_call(audit_log, session_id=_session_id)
        _ = _seed_tool_call(audit_log, session_id=_other_session_id)
        _ = _seed_tool_call(audit_log, session_id='')
        _ = _seed_tool_call(audit_log, session_id='')

        assert collect_repeat_call_facts(engine, _window_seconds, now) == []

    def test_calls_outside_the_window_are_not_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_tool_call(audit_log)
        _ = _seed_tool_call(audit_log)
        old_id = _seed_tool_call(audit_log)
        _backdate(old_id, now - timedelta(seconds=_window_seconds + 60))

        fact = _fact_of(collect_repeat_call_facts(engine, _window_seconds, now), _gateway_name)

        assert fact['repeat_call_count'] == 2

# ################################################################################################################################
# ################################################################################################################################

class TestToolCount:

    def test_a_gateway_with_no_rows_is_measured_off_its_own_count(self) -> 'None':
        facts = collect_tool_count_facts({_gateway_name: 30, _other_gateway_name: 3})

        assert len(facts) == 2

        assert _fact_of(facts, _gateway_name)['tool_count'] == 30
        assert _fact_of(facts, _other_gateway_name)['tool_count'] == 3

        # A gateway nobody counted has no fact
        assert collect_tool_count_facts({}) == []

    def test_the_merged_facts_carry_the_tool_count_next_to_the_traffic(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_invalid_call(audit_log, Error_Code_Method_Not_Found)
        _ = _seed_tool_call(audit_log, size=3000)
        _ = _seed_tool_call(audit_log, size=3000)

        tool_counts = {_gateway_name: 30, _other_gateway_name: 3}
        facts = collect_facts(engine, {}, AuditSource.MCP, now, window_seconds=_window_seconds, tool_counts=tool_counts)

        fact = _fact_of(facts, _gateway_name)

        assert fact['tool_count'] == 30
        assert fact['invalid_call_count'] == 1
        assert fact['volume_bytes'] == 6000
        assert fact['repeat_call_count'] == 3
        assert fact['total_count'] == 3
        assert fact['error_count'] == 1

        windows = fact[Window_Seconds_By_Measure_Key]

        assert windows[Measure_Invalid_Calls] == _window_seconds
        assert windows[Measure_Volume] == _window_seconds
        assert windows[Measure_Repeat_Calls] == _window_seconds

        # The other gateway has no traffic and still its count
        other_fact = _fact_of(facts, _other_gateway_name)
        assert other_fact['tool_count'] == 3
        assert other_fact['total_count'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestSharedRatesOnAGateway:

    def test_the_error_rate_and_latency_read_tool_calls_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Four tool calls, one of them failed, each 100 ms ..
        _ = _seed_tool_call(audit_log)
        _ = _seed_tool_call(audit_log)
        _ = _seed_tool_call(audit_log)
        _ = _seed_tool_call(audit_log, is_ok=False)

        # .. next to a slow initialize, a failed tools/list and a rejected caller, none of which is a tool call.
        _seed_other_event(audit_log, AuditEvent.MCP_Initialize, duration_ms=5000)
        _seed_other_event(audit_log, AuditEvent.MCP_Tools_List, is_ok=False, duration_ms=5000)
        _seed_auth_failure(audit_log)

        rate_fact = _fact_of(collect_error_rate_facts(engine, _window_seconds, now, source=AuditSource.MCP), _gateway_name)

        assert rate_fact['total_count'] == 4
        assert rate_fact['error_count'] == 1
        assert rate_fact['error_rate'] == 0.25

        latency_fact = _fact_of(collect_latency_facts(engine, _window_seconds, now, source=AuditSource.MCP), _gateway_name)

        assert latency_fact['avg_duration_ms'] == 100

    def test_a_streak_is_counted_over_tool_calls_and_rejected_callers_are_their_own_measure(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_tool_call(audit_log)
        _ = _seed_tool_call(audit_log, is_ok=False)
        _ = _seed_tool_call(audit_log, is_ok=False)

        # Three rejected callers after the two failed calls - not a streak of five
        _seed_auth_failure(audit_log)
        _seed_auth_failure(audit_log)
        _seed_auth_failure(audit_log)

        streak_fact = _fact_of(collect_consecutive_failure_facts(engine, now, source=AuditSource.MCP), _gateway_name)
        assert streak_fact['consecutive_failures'] == 2

        auth_fact = _fact_of(collect_auth_failure_facts(engine, _window_seconds, now, source=AuditSource.MCP), _gateway_name)
        assert auth_fact['auth_failure_count'] == 3

# ################################################################################################################################
# ################################################################################################################################
