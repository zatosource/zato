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

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import is_failed, is_object, is_recent, is_source, response_event_type_by_source, \
    Default_Window_Seconds, Probe_Source_Test_Transfer
from zato.common.alerting.collectors.file_transfer import Attr_Schedule
from zato.common.audit_log.api import event_attr_table, event_table, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.file_transfer_run import Run_Status_Failed, Run_Status_Interrupted, Run_Status_List_Failed, \
    Run_Status_No_Directory, Run_Status_Partial
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

# How many rows one measure contributes at most - the budget the document is fitted to
# trims further, this only keeps a very busy connection from being read in full.
Max_Rows_Per_Measure = 200

# The run statuses that say a run did not go as it should have.
_troubled_run_statuses = (
    Run_Status_Failed,
    Run_Status_Partial,
    Run_Status_No_Directory,
    Run_Status_List_Failed,
    Run_Status_Interrupted,
)

# The columns every evidence row carries.
_row_columns = (
    event_table.c.id,
    event_table.c.event_time_iso,
    event_table.c.event_type,
    event_table.c.endpoint,
    event_table.c.outcome,
    event_table.c.status,
    event_table.c.duration_ms,
    event_table.c.data,
    event_table.c.ext_client_id,
)

# ################################################################################################################################
# ################################################################################################################################

def _window_start_iso(fact:'stranydict', now:'datetime') -> 'str':
    """ Where the fact's window starts - a fact measured without a window, e.g. a probe's
    point-in-time reading, is read over the default window instead.
    """
    window_seconds = fact['window_seconds']

    if not window_seconds:
        window_seconds = Default_Window_Seconds

    start = now - timedelta(seconds=window_seconds)
    out = start.isoformat()

    return out

# ################################################################################################################################

def _rows_from(result:'anylist') -> 'dictlist':
    """ The rows of a query as evidence rows.
    """

    # Our response to produce
    out:'dictlist' = []

    for event_id, event_time_iso, event_type, endpoint, outcome, status, duration_ms, data, ext_client_id in result:

        row:'stranydict' = {
            'id': event_id,
            'event_time_iso': event_time_iso,
            'event_type': event_type,
            'endpoint': endpoint,
            'outcome': outcome,
            'status': status,
            'duration_ms': duration_ms,
            'data': data,
            'ext_client_id': ext_client_id,
        }

        out.append(row)

    return out

# ################################################################################################################################

def _select_rows(engine:'Engine', conditions:'anylist') -> 'dictlist':
    """ The newest rows meeting the conditions, newest first, capped per measure.
    """
    statement = select(*_row_columns).where(and_(*conditions)).order_by(event_table.c.id.desc()).limit(Max_Rows_Per_Measure)

    with engine.connect() as connection:
        result = connection.execute(statement).fetchall()

    out = _rows_from(result)
    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_failed_events(engine:'Engine', fact:'stranydict', now:'datetime') -> 'dictlist':
    """ The failed events of the fact's object within its window - what the error counts,
    the error rate and the consecutive failures were counted from.
    """
    conditions = [
        is_source(fact['source']),
        is_object(fact['object_name']),
        is_failed(),
        is_recent(_window_start_iso(fact, now)),
    ]

    out = _select_rows(engine, conditions)
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
