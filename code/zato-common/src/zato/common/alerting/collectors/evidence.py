# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The evidence behind one alert - the audit rows the measures a rule read were counted from,
# and the baseline that says how the object fared around them. A measure knows which rows
# it was taken over, so the rows read here are the same ones the collectors counted -
# the failed transfers of a connection, the runs of a schedule, the deliveries a schedule
# made, the probe results - newest first and within the window the fact was measured over.

from __future__ import annotations

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import is_failed, is_object, is_recent, is_source, response_event_type_by_source, \
    Probe_Source_Test_Transfer
from zato.common.alerting.collectors.evidence_mcp import attach_mcp_details, collect_invalid_calls, collect_mcp_truncations, \
    collect_rejections, collect_repeat_calls, collect_throttled
from zato.common.alerting.collectors.evidence_rows import row_columns as _row_columns, rows_from as _rows_from, \
    select_rows as _select_rows, window_start_iso as _window_start_iso, Max_Rows_Per_Measure
from zato.common.alerting.collectors.file_transfer import Attr_Schedule
from zato.common.audit_log.api import event_attr_table, event_body_table, event_table, AuditBody, AuditEvent, AuditOutcome, \
    AuditSource
from zato.common.audit_log.common import LLMAttr, LLMFinish
from zato.common.audit_log.file_transfer_run import Run_Status_Failed, Run_Status_Interrupted, Run_Status_List_Failed, \
    Run_Status_No_Directory, Run_Status_Partial
from zato.common.hl7.audit import Attr_Ack_Status
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anylist, callable_, dictlist, stranydict, strlist
    any_ = any_
    anylist = anylist
    callable_ = callable_
    datetime = datetime
    dictlist = dictlist
    Engine = Engine
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The cap on how many rows one measure contributes, re-exported for the readers of this module
Max_Rows_Per_Measure = Max_Rows_Per_Measure

# The run statuses that say a run did not go as it should have.
_troubled_run_statuses = (
    Run_Status_Failed,
    Run_Status_Partial,
    Run_Status_No_Directory,
    Run_Status_List_Failed,
    Run_Status_Interrupted,
)

# The sources whose failed rows say what went wrong in a body rather than in their data - an MLLP channel's
# failed ack is the ACK message itself, kept as the row's response body, so the evidence reads it from there.
_body_kind_by_source = {
    AuditSource.MLLP_Channel: AuditBody.Response,
}

# The sources whose failed rows may say nothing in their status and carry what happened in an attr instead -
# an outgoing MLLP connection's ack row has the ack's error text as its status, and a message no ack came back
# for has an empty one, its ack status attr reading `timeout`, so the evidence reads that onto the row.
_status_attr_by_source = {
    AuditSource.MLLP_Outgoing: Attr_Ack_Status,
}

# The attributes an LLM row shows in the evidence next to its status, in this order - the model asked, why the
# provider stopped and what the call cost, so a `200 OK` that was a truncation reads as one.
_llm_evidence_attrs = (LLMAttr.Model, LLMAttr.Finish_Reason, LLMAttr.Input_Tokens, LLMAttr.Output_Tokens)

# The finish reasons an LLM completion alert was counted from - a truncation and a refusal both arrive as an HTTP 200
_llm_counted_finish_reasons = (LLMFinish.Length, LLMFinish.Refusal)

# ################################################################################################################################
# ################################################################################################################################

def _attach_bodies(engine:'Engine', rows:'dictlist', kind:'str') -> 'None':
    """ Puts the body of the given kind on each row that has one, as its data - what the rows of a source
    that keeps its error text in a body say went wrong.
    """
    if not rows:
        return

    by_id = {row['id']: row for row in rows}

    statement = select(event_body_table.c.event_id, event_body_table.c.data).where(and_(
        event_body_table.c.event_id.in_(list(by_id)),
        event_body_table.c.kind == kind,
    ))

    with engine.connect() as connection:
        result = connection.execute(statement).fetchall()

    for event_id, data in result:
        by_id[event_id]['data'] = data

# ##############################################################################################################################

def _attach_status_attr(engine:'Engine', rows:'dictlist', attr_name:'str') -> 'None':
    """ Puts the value of the given attr on each row whose status is empty, as its data - what such a row
    has to say about what went wrong when its status says nothing.
    """
    by_id = {row['id']: row for row in rows if not row['status']}

    if not by_id:
        return

    statement = select(event_attr_table.c.event_id, event_attr_table.c.value).where(and_(
        event_attr_table.c.event_id.in_(list(by_id)),
        event_attr_table.c.name == attr_name,
    ))

    with engine.connect() as connection:
        result = connection.execute(statement).fetchall()

    for event_id, value in result:
        by_id[event_id]['data'] = value

# ##############################################################################################################################

def _attach_llm_attrs(engine:'Engine', rows:'dictlist') -> 'None':
    """ Puts what an LLM row's attributes say onto the row as its data - `model=gpt-4o, finish_reason=length,
    input_tokens=1200, output_tokens=300` - so the evidence tells a truncated `200 OK` from a plain one and
    names the model and the cost of every call it lists. A row with no attributes keeps whatever data it had.
    """
    if not rows:
        return

    by_id = {row['id']: row for row in rows}

    statement = select(event_attr_table.c.event_id, event_attr_table.c.name, event_attr_table.c.value).where(and_(
        event_attr_table.c.event_id.in_(list(by_id)),
        event_attr_table.c.name.in_(list(_llm_evidence_attrs)),
    ))

    with engine.connect() as connection:
        result = connection.execute(statement).fetchall()

    # The attributes of each row by name, so they can be written out in one order whatever order they were read in
    attrs_by_id:'dict[int, dict[str, str]]' = {}

    for event_id, name, value in result:
        attrs_by_id.setdefault(event_id, {})[name] = value

    for event_id, attrs in attrs_by_id.items():

        parts:'strlist' = []

        for name in _llm_evidence_attrs:
            if name in attrs:
                parts.append(f'{name}={attrs[name]}')

        by_id[event_id]['data'] = ', '.join(parts)

# ################################################################################################################################

def _attach_source_details(engine:'Engine', source:'str', rows:'dictlist') -> 'None':
    """ Reads onto the rows whatever their source keeps outside the event row itself - a body, a status attr
    or, for an LLM connection, the attributes of each call.
    """

    # A source whose rows say what went wrong in a body has it read onto them ..
    if source in _body_kind_by_source:
        _attach_bodies(engine, rows, _body_kind_by_source[source])

    # .. one whose rows may say it in an attr alone has that read onto the rows with nothing in their status ..
    if source in _status_attr_by_source:
        _attach_status_attr(engine, rows, _status_attr_by_source[source])

    # .. an LLM row shows its model, finish reason and token usage next to its status ..
    if source == AuditSource.LLM:
        _attach_llm_attrs(engine, rows)

    # .. and a gateway's row says what went wrong with the tool call in one line read off its data document.
    if source == AuditSource.MCP:
        attach_mcp_details(rows)

# ################################################################################################################################

def collect_failed_events(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The failed events of the fact's object within its window - what the error counts,
    the error rate, the consecutive failures and the negative acks were counted from.
    """
    source = fact['source']

    conditions = [
        is_source(source),
        is_object(fact['object_name']),
        is_failed(),
        is_recent(_window_start_iso(fact, now)),
    ]

    out = _select_rows(engine, conditions)
    _attach_source_details(engine, source, out)

    return out

# ################################################################################################################################

def collect_llm_completions(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The completions of the fact's LLM connection the provider cut short or declined within its window - the rows
    whose finish reason attr is `length` or `refusal`, whatever their outcome, because a truncation and a refusal are
    OK rows while a Gemini prompt block is an Error one with a refusal for its reason. What the truncation and the
    refusal counts were counted from.
    """
    conditions = [
        is_source(fact['source']),
        is_object(fact['object_name']),
        event_attr_table.c.name == LLMAttr.Finish_Reason,
        event_attr_table.c.value.in_(list(_llm_counted_finish_reasons)),
        is_recent(_window_start_iso(fact, now)),
    ]

    attr_join = event_table.join(event_attr_table, event_table.c.id == event_attr_table.c.event_id)

    statement = select(*_row_columns).select_from(attr_join).where(and_(*conditions))
    statement = statement.order_by(event_table.c.id.desc()).limit(Max_Rows_Per_Measure)

    with engine.connect() as connection:
        result = connection.execute(statement).fetchall()

    out = _rows_from(result)
    _attach_llm_attrs(engine, out)

    return out

# ################################################################################################################################

def collect_truncations(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The rows a truncation count was counted from - an LLM connection's completions the provider cut short,
    or an MCP gateway's tool responses its size cap cut, the one fact key standing for either.
    """
    if fact['source'] == AuditSource.MCP:
        out = collect_mcp_truncations(engine, fact, now)
    else:
        out = collect_llm_completions(engine, fact, now)

    return out

# ################################################################################################################################

def collect_no_rows(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ What a measure that is a sum or a reading rather than a count of failures has for rows - none. A token
    budget alert's evidence is the count and its split into input and output, both of which the fact carries
    already, and listing every call that added to the sum would say nothing the numbers do not - the same goes
    for a gateway's response volume and for its tool count, which is read off the gateway rather than the log.
    """
    out:'dictlist' = []
    return out

# ################################################################################################################################

def collect_events_of_type(engine:'Engine', fact:'stranydict', now:'datetime', event_type:'str') -> 'dictlist':
    """ The events of one type about the fact's object within its window, whatever their outcome.
    """
    conditions = [
        is_source(fact['source']),
        is_object(fact['object_name']),
        event_table.c.event_type == event_type,
        is_recent(_window_start_iso(fact, now)),
    ]

    out = _select_rows(engine, conditions)
    return out

# ################################################################################################################################

def collect_all_events(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ Every event about the fact's object within its window - what a probe's readings are.
    """
    conditions = [
        is_source(fact['source']),
        is_object(fact['object_name']),
        is_recent(_window_start_iso(fact, now)),
    ]

    out = _select_rows(engine, conditions)
    return out

# ################################################################################################################################

def collect_troubled_runs(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The runs of the fact's schedule that did not go as they should have, within its window.
    A run row is stored under its connection and names its schedule in its data, so the rows
    of the whole source are read and the schedule's own are picked out.
    """
    conditions = [
        is_source(AuditSource.File_Outgoing),
        event_table.c.event_type == AuditEvent.Run_Completed,
        is_recent(_window_start_iso(fact, now)),
    ]

    statement = select(*_row_columns).where(and_(*conditions)).order_by(event_table.c.id.desc())

    with engine.connect() as connection:
        result = connection.execute(statement).fetchall()

    # Our response to produce
    out:'dictlist' = []

    for row in _rows_from(result):

        details = loads(row['data'])

        if details['schedule'] != fact['object_name']:
            continue

        is_troubled = row['outcome'] == AuditOutcome.Error or row['status'] in _troubled_run_statuses

        if not is_troubled:
            continue

        out.append(row)

        if len(out) >= Max_Rows_Per_Measure:
            break

    return out

# ################################################################################################################################

def collect_deliveries(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The files the fact's schedule delivered within its window - a delivered event is stored
    under its connection and carries its schedule's name as an attr.
    """
    conditions = [
        is_source(AuditSource.File_Outgoing),
        event_table.c.event_type == AuditEvent.Delivered,
        event_attr_table.c.name == Attr_Schedule,
        event_attr_table.c.value == fact['object_name'],
        is_recent(_window_start_iso(fact, now)),
    ]

    attr_join = event_table.join(event_attr_table, event_table.c.id == event_attr_table.c.event_id)

    statement = select(*_row_columns).select_from(attr_join).where(and_(*conditions))
    statement = statement.order_by(event_table.c.id.desc()).limit(Max_Rows_Per_Measure)

    with engine.connect() as connection:
        result = connection.execute(statement).fetchall()

    out = _rows_from(result)
    return out

# ################################################################################################################################

def collect_test_transfers(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The test transfer results of the fact's connection within its window.
    """
    conditions = [
        is_source(Probe_Source_Test_Transfer),
        is_object(fact['object_name']),
        is_recent(_window_start_iso(fact, now)),
    ]

    out = _select_rows(engine, conditions)
    return out

# ################################################################################################################################

def collect_quarantined(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    out = collect_events_of_type(engine, fact, now, AuditEvent.File_Quarantined)
    return out

# ################################################################################################################################

def collect_verify_failed(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    out = collect_events_of_type(engine, fact, now, AuditEvent.Verify_Failed)
    return out

# ################################################################################################################################
# ################################################################################################################################

# Which rows each measure was counted from - a measure not listed here was counted from
# the object's failed events, the same as the error counts.
measure_to_evidence:'dict[str, callable_]' = {
    'error_count':                collect_failed_events,
    'error_rate':                 collect_failed_events,
    'consecutive_failures':       collect_failed_events,
    'auth_failure_count':         collect_failed_events,
    'runs_failed_in_window':      collect_troubled_runs,
    'failed_files_in_window':     collect_troubled_runs,
    'runs_interrupted_in_window': collect_troubled_runs,
    'list_failed_streak':         collect_troubled_runs,
    'last_run_status':            collect_troubled_runs,
    'seconds_since_last_arrival': collect_deliveries,
    'arrival_overdue_ratio':      collect_deliveries,
    'expected_files_missing':     collect_deliveries,
    'delivered_today':            collect_deliveries,
    'test_transfer_failed':       collect_test_transfers,
    'quarantined_count':          collect_quarantined,
    'verify_failed_count':        collect_verify_failed,
    'cert_days_left':             collect_all_events,
    'health_state':               collect_all_events,
    'truncation_count':           collect_truncations,
    'refusal_count':              collect_llm_completions,
    'token_count':                collect_no_rows,
    'input_token_count':          collect_no_rows,
    'output_token_count':         collect_no_rows,
    'invalid_call_count':         collect_invalid_calls,
    'rejection_count':            collect_rejections,
    'throttled_count':            collect_throttled,
    'repeat_call_count':          collect_repeat_calls,
    'repeat_call_tool':           collect_repeat_calls,
    'repeat_call_session':        collect_repeat_calls,
    'volume_bytes':               collect_no_rows,
    'tool_count':                 collect_no_rows,
}

# ################################################################################################################################

def collect_measure_rows(engine:'Engine', fact:'stranydict', measures:'strlist', now:'datetime') -> 'dictlist':
    """ The rows the given measures of a fact were counted from - each measure's own query,
    the rows of all of them together, each row once, newest first.
    """
    by_id:'dict[int, stranydict]' = {}

    for measure in measures:

        if measure in measure_to_evidence:
            collect = measure_to_evidence[measure]
        else:
            collect = collect_failed_events

        for row in collect(engine, fact, now):
            by_id[row['id']] = row

    # Our response to produce
    out = list(by_id.values())
    out.sort(key=_by_id_newest_first)

    return out

# ################################################################################################################################

def _by_id_newest_first(row:'stranydict') -> 'int':
    out = -row['id']
    return out

# ################################################################################################################################
# ################################################################################################################################

def _outcome_conditions(source:'str') -> 'anylist':
    """ What narrows the events whose outcomes a baseline reads - a channel logs each call twice, the request
    and the response, and the response alone says how the call went, so only responses count for a channel.
    """

    # Our response to produce
    out:'anylist' = []

    if source in response_event_type_by_source:
        out.append(event_table.c.event_type == response_event_type_by_source[source])

    return out

# ################################################################################################################################

def _newest_ok_before(engine:'Engine', source:'str', object_name:'str', before_id:'int') -> 'stranydict | None':
    """ The newest successful event of an object older than the given one, None when there is none.
    """
    conditions = [
        is_source(source),
        is_object(object_name),
        event_table.c.outcome == AuditOutcome.OK,
        event_table.c.id < before_id,
    ]
    conditions.extend(_outcome_conditions(source))

    statement = select(*_row_columns).where(and_(*conditions)).order_by(event_table.c.id.desc()).limit(1)

    with engine.connect() as connection:
        result = connection.execute(statement).fetchall()

    rows = _rows_from(result)

    if rows:
        out = rows[0]
    else:
        out = None

    return out

# ################################################################################################################################

def collect_baseline(
    engine:'Engine',
    fact:'stranydict',
    now:'datetime',
    *,
    baseline_object_name:'str' = '',
    test_transfers_on:'bool' = False,
    ) -> 'stranydict':
    """ How the object fared around its failures - how many events succeeded in the window and
    which was the newest, how long the current run of failures is and what the last success
    before it was, and the newest test transfer result when test transfers are on for the
    connection. A fact keyed by a schedule has its successes read under the owning connection,
    which is what the baseline object name is for.
    """
    if not baseline_object_name:
        baseline_object_name = fact['object_name']

    source = fact['source']
    window_start_iso = _window_start_iso(fact, now)
    outcome_conditions = _outcome_conditions(source)

    # How many events succeeded in the window ..
    ok_conditions = [
        is_source(source),
        is_object(baseline_object_name),
        event_table.c.outcome == AuditOutcome.OK,
        is_recent(window_start_iso),
    ]
    ok_conditions.extend(outcome_conditions)

    count_statement = select(func.count(event_table.c.id)).where(and_(*ok_conditions))

    with engine.connect() as connection:
        ok_count = connection.execute(count_statement).scalar()

    # .. and which was the newest of them.
    last_ok_statement = select(*_row_columns).where(and_(*ok_conditions)).order_by(event_table.c.id.desc()).limit(1)

    with engine.connect() as connection:
        last_ok_rows = _rows_from(connection.execute(last_ok_statement).fetchall())

    if last_ok_rows:
        last_ok = last_ok_rows[0]
    else:
        last_ok = None

    # The current run of failures - the newest events of the object, as long as they keep failing.
    newest_conditions = [
        is_source(source),
        is_object(baseline_object_name),
        event_table.c.outcome.in_([AuditOutcome.OK, AuditOutcome.Error]),
        is_recent(window_start_iso),
    ]
    newest_conditions.extend(outcome_conditions)

    newest_statement = select(*_row_columns).where(and_(*newest_conditions)).order_by(event_table.c.id.desc())
    newest_statement = newest_statement.limit(Max_Rows_Per_Measure)

    with engine.connect() as connection:
        newest_rows = _rows_from(connection.execute(newest_statement).fetchall())

    streak_count = 0
    streak_start_iso = ''
    last_ok_before_streak = None

    for row in newest_rows:

        if row['outcome'] != AuditOutcome.Error:
            break

        streak_count += 1
        streak_start_iso = row['event_time_iso']

    if streak_count:
        oldest_streak_row = newest_rows[streak_count - 1]
        last_ok_before_streak = _newest_ok_before(engine, source, baseline_object_name, oldest_streak_row['id'])

    # The newest test transfer result, when the connection takes part in them
    test_transfer = None

    if test_transfers_on:
        probe_conditions = [
            is_source(Probe_Source_Test_Transfer),
            is_object(baseline_object_name),
        ]

        probe_statement = select(*_row_columns).where(and_(*probe_conditions)).order_by(event_table.c.id.desc()).limit(1)

        with engine.connect() as connection:
            probe_rows = _rows_from(connection.execute(probe_statement).fetchall())

        if probe_rows:
            test_transfer = probe_rows[0]

    # Our response to produce
    out:'stranydict' = {
        'ok_count': ok_count,
        'last_ok': last_ok,
        'streak_count': streak_count,
        'streak_start_iso': streak_start_iso,
        'last_ok_before_streak': last_ok_before_streak,
        'test_transfers_on': test_transfers_on,
        'test_transfer': test_transfer,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
