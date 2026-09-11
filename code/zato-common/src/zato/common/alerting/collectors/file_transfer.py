# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The file transfer facts - arrival, daily expectations, run outcomes, quarantines and failed verifications.

from __future__ import annotations

# stdlib
from datetime import datetime, time as datetime_time, timedelta, timezone
from json import loads

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import new_fact, Default_Window_Seconds
from zato.common.audit_log.api import event_attr_table, event_table, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.file_transfer_run import Run_Status_Interrupted, Run_Status_List_Failed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anydict, dictlist, stranydict, strintdict, strlist, strstrdict
    anydict = anydict
    dictlist = dictlist
    Engine = Engine
    stranydict = stranydict
    strintdict = strintdict
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The attr each schedule-level event carries its schedule's name under.
Attr_Schedule = 'schedule'

# How far back a connection's quarantines and failed verifications are counted.
Quarantine_Window_Seconds = 86400

# How many of a schedule's newest runs the list-failed streak is counted over.
Run_Streak_Depth = 20

# How far back run rows are read - at least this far, and as far as the run window when that is longer.
Run_Facts_Window_Seconds = 3600

# The format of a schedule's expected-by time, e.g. 08:00.
_expected_by_format = '%H:%M'

# ################################################################################################################################
# ################################################################################################################################

def collect_file_transfer_facts(
    engine:'Engine',
    now:'datetime',
    arrival_windows:'strintdict',
    schedule_expectations:'anydict | None' = None,
    run_window_seconds:'int' = Default_Window_Seconds,
    ) -> 'dictlist':
    """ The arrival, expectation and run facts of each schedule and the quarantine and verification facts
    of each connection. The in-window run counts cover run_window_seconds, the window the type's failure rules carry.
    """

    # Our response to produce
    out:'dictlist' = []

    if schedule_expectations is None:
        schedule_expectations = {}

    arrival_facts = _collect_arrival_facts(engine, now, arrival_windows)
    expectation_facts = _collect_expectation_facts(engine, now, schedule_expectations)
    run_facts = _collect_run_facts(engine, now, run_window_seconds)
    connection_facts = _collect_connection_facts(engine, now)

    out.extend(arrival_facts)
    out.extend(expectation_facts)
    out.extend(run_facts)
    out.extend(connection_facts)

    return out

# ################################################################################################################################

def _collect_arrival_facts(engine:'Engine', now:'datetime', arrival_windows:'strintdict') -> 'dictlist':
    """ How far past its arrival window each schedule with a window is.
    """

    # Our response to produce
    out:'dictlist' = []

    # Nothing declares an arrival expectation, so there is nothing to measure
    if not arrival_windows:
        return out

    # When each schedule last handed a file to its service - every delivered event
    # carries its schedule's name as a searchable attr.
    query = select(
        event_attr_table.c.value,
        func.max(event_table.c.event_time_iso),
    ).select_from(
        event_table.join(event_attr_table, event_table.c.id == event_attr_table.c.event_id),
    ).where(and_(
        event_table.c.source == AuditSource.File_Outgoing,
        event_table.c.event_type == AuditEvent.Delivered,
        event_attr_table.c.name == Attr_Schedule,
    )).group_by(event_attr_table.c.value)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    for schedule_name, last_arrival_iso in rows:

        # A schedule with no window on record declares no expectation and is skipped
        if window := arrival_windows.get(schedule_name):

            last_arrival_time = datetime.fromisoformat(last_arrival_iso)
            since_last_arrival = (now - last_arrival_time).total_seconds()

            fact = new_fact(AuditSource.File_Outgoing, schedule_name)
            fact['seconds_since_last_arrival'] = round(since_last_arrival)
            fact['arrival_overdue_ratio'] = round(since_last_arrival / window, 2)

            out.append(fact)

    return out

# ################################################################################################################################

def _is_past_expected_by(now_local:'datetime', expectation:'stranydict') -> 'bool':
    """ Whether today is one of the schedule's expected days and its expected-by time has passed.
    """
    expected_days = expectation['expected_days']
    weekday_number = now_local.isoweekday()
    weekday = str(weekday_number)

    days:'strlist' = []

    for day in expected_days.split(','):
        days.append(day.strip())

    if weekday not in days:
        return False

    expected_by = datetime.strptime(expectation['expected_by'], _expected_by_format)
    today = now_local.date()
    deadline_time = datetime_time(expected_by.hour, expected_by.minute)
    deadline = datetime.combine(today, deadline_time, tzinfo=now_local.tzinfo)

    out = now_local >= deadline
    return out

# ################################################################################################################################

def _collect_expectation_facts(engine:'Engine', now:'datetime', schedule_expectations:'anydict') -> 'dictlist':
    """ How many expected files each schedule is still missing today, past its expected-by time.
    """

    # Our response to produce
    out:'dictlist' = []

    if not schedule_expectations:
        return out

    now_local = now.astimezone()
    today = now_local.date()
    day_start_local = datetime.combine(today, datetime_time.min, tzinfo=now_local.tzinfo)
    day_start_utc = day_start_local.astimezone(timezone.utc)
    day_start_iso = day_start_utc.isoformat()

    # How many files each schedule delivered today.
    attr_join = event_table.join(event_attr_table, event_table.c.id == event_attr_table.c.event_id)
    delivered_count = func.count(event_table.c.id)

    is_source = event_table.c.source == AuditSource.File_Outgoing
    is_delivered = event_table.c.event_type == AuditEvent.Delivered
    is_today = event_table.c.event_time_iso >= day_start_iso
    is_schedule_attr = event_attr_table.c.name == Attr_Schedule

    query = select(event_attr_table.c.value, delivered_count)
    query = query.select_from(attr_join)
    query = query.where(and_(is_source, is_delivered, is_today, is_schedule_attr))
    query = query.group_by(event_attr_table.c.value)

    with engine.connect() as connection:
        result = connection.execute(query)
        rows = result.fetchall()

    delivered_today:'strintdict' = {}

    for schedule_name, count in rows:
        delivered_today[schedule_name] = count

    for schedule_name, expectation in schedule_expectations.items():

        # Today is not an expected day or the deadline has not come yet.
        if not _is_past_expected_by(now_local, expectation):
            continue

        expected = expectation['expected_files']

        if not (delivered := delivered_today.get(schedule_name)):
            delivered = 0

        missing = expected - delivered

        if missing <= 0:
            continue

        fact = new_fact(AuditSource.File_Outgoing, schedule_name)
        fact['expected_files_missing'] = missing
        fact['delivered_today'] = delivered

        out.append(fact)

    return out

# ################################################################################################################################

def _collect_run_facts(engine:'Engine', now:'datetime', run_window_seconds:'int') -> 'dictlist':
    """ The newest run's status, the list-failed streak and the in-window counts of failed runs, failed files
    and interrupted runs, per schedule.
    """

    # Our response to produce
    out:'dictlist' = []

    # The rows read must reach back as far as the counted window does
    read_window_seconds = max(Run_Facts_Window_Seconds, run_window_seconds)

    since = now - timedelta(seconds=read_window_seconds)
    since_iso = since.isoformat()

    window_start = now - timedelta(seconds=run_window_seconds)
    window_start_iso = window_start.isoformat()

    # The run rows of every schedule, newest first.
    is_source = event_table.c.source == AuditSource.File_Outgoing
    is_run = event_table.c.event_type == AuditEvent.Run_Completed
    is_recent = event_table.c.event_time_iso >= since_iso
    newest_first = event_table.c.id.desc()

    query = select(event_table.c.status, event_table.c.outcome, event_table.c.event_time_iso, event_table.c.data)
    query = query.where(and_(is_source, is_run, is_recent))
    query = query.order_by(newest_first)

    with engine.connect() as connection:
        result = connection.execute(query)
        rows = result.fetchall()

    # The newest run's status and the list-failed streak, per schedule ..
    newest_status:'strstrdict' = {}
    streak:'strintdict' = {}
    seen:'strintdict' = {}

    # .. and the in-window counts, per schedule.
    runs_failed:'strintdict' = {}
    files_failed:'strintdict' = {}
    runs_interrupted:'strintdict' = {}

    for status, outcome, event_time_iso, data in rows:

        details = loads(data)
        schedule_name = details['schedule']

        if schedule_name not in seen:
            seen[schedule_name] = 0
            streak[schedule_name] = 0
            newest_status[schedule_name] = status
            runs_failed[schedule_name] = 0
            files_failed[schedule_name] = 0
            runs_interrupted[schedule_name] = 0

        # The in-window counts.
        if event_time_iso >= window_start_iso:

            if outcome == AuditOutcome.Error:
                runs_failed[schedule_name] += 1

            if status == Run_Status_Interrupted:
                runs_interrupted[schedule_name] += 1

            # A run that failed before listing its directory has no file counts.
            if failed := details.get('failed'):
                files_failed[schedule_name] += failed

        # The streak is counted over the newest Run_Streak_Depth runs ..
        if seen[schedule_name] >= Run_Streak_Depth:
            continue

        seen[schedule_name] += 1

        # .. from the newest run to the first one that listed its directory.
        if status == Run_Status_List_Failed:
            if streak[schedule_name] == seen[schedule_name] - 1:
                streak[schedule_name] += 1

    for schedule_name, status in newest_status.items():

        fact = new_fact(AuditSource.File_Outgoing, schedule_name)
        fact['last_run_status'] = status
        fact['list_failed_streak'] = streak[schedule_name]
        fact['runs_failed_in_window'] = runs_failed[schedule_name]
        fact['failed_files_in_window'] = files_failed[schedule_name]
        fact['runs_interrupted_in_window'] = runs_interrupted[schedule_name]

        out.append(fact)

    return out

# ################################################################################################################################

def _collect_connection_facts(engine:'Engine', now:'datetime') -> 'dictlist':
    """ How many files each connection quarantined and how many stores failed verification within the window.
    """

    # Our response to produce
    out:'dictlist' = []

    since = now - timedelta(seconds=Quarantine_Window_Seconds)
    since_iso = since.isoformat()

    counted_types = [AuditEvent.File_Quarantined, AuditEvent.Verify_Failed]
    event_count = func.count(event_table.c.id)

    is_source = event_table.c.source == AuditSource.File_Outgoing
    is_counted = event_table.c.event_type.in_(counted_types)
    is_recent = event_table.c.event_time_iso >= since_iso

    query = select(event_table.c.object_name, event_table.c.event_type, event_count)
    query = query.where(and_(is_source, is_counted, is_recent))
    query = query.group_by(event_table.c.object_name, event_table.c.event_type)

    with engine.connect() as connection:
        result = connection.execute(query)
        rows = result.fetchall()

    facts_by_name:'anydict' = {}

    for conn_name, event_type, count in rows:

        if not (fact := facts_by_name.get(conn_name)):
            fact = new_fact(AuditSource.File_Outgoing, conn_name)
            facts_by_name[conn_name] = fact

        if event_type == AuditEvent.File_Quarantined:
            fact['quarantined_count'] = count
        else:
            fact['verify_failed_count'] = count

    facts = facts_by_name.values()
    out.extend(facts)

    return out

# ################################################################################################################################
# ################################################################################################################################
