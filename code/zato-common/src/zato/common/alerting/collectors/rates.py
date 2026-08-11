# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The rate producers - error rates with their windows and counts, unbroken failure
# streaks, average call durations and authentication failures, each one a pure
# function over the audit database.

from __future__ import annotations

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import and_, case, func, select

# Zato
from zato.common.alerting.collectors.common import apply_newest_error, collect_newest_error_events, new_fact, \
    Default_Consecutive_Depth
from zato.common.audit_log.api import event_table, AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist
    datetime = datetime
    dictlist = dictlist
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

def collect_error_rate_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the share of error outcomes within the window, one row of measures
    per (source, object) pair that had any traffic at all. A pair whose window holds
    failures also reports its newest failing event, so an alert about the failures
    can point straight at the message that failed.
    """

    # Our response to produce
    out:'dictlist' = []

    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    conditions = [
        event_table.c.event_time_iso >= window_start_iso,
    ]

    # The optional criteria narrow the measures only when set
    if source:
        conditions.append(event_table.c.source == source)

    if object_name:
        conditions.append(event_table.c.object_name == object_name)

    # Errors and totals per source and object, in one pass
    error_case = case((event_table.c.outcome == AuditOutcome.Error, 1), else_=0)

    statement = select(
        event_table.c.source,
        event_table.c.object_name,
        func.count(),
        func.sum(error_case),
    ).where(and_(*conditions)).group_by(event_table.c.source, event_table.c.object_name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    # The newest failing event of each pair within the same window, read once
    # for every pair rather than once per fact
    newest_errors = collect_newest_error_events(
        engine, window_start_iso=window_start_iso, source=source, object_name=object_name)

    for row_source, row_object_name, total, errors in rows:

        # Each backend returns its own numeric type for a sum, hence the conversion
        error_count = int(errors)

        fact = new_fact(row_source, row_object_name)
        fact['error_rate'] = error_count / total
        fact['error_count'] = error_count
        fact['total_count'] = total
        fact['window_seconds'] = window_seconds

        # Only a pair with failures has a failing event to point at
        if error_count:
            apply_newest_error(fact, newest_errors)

        out.append(fact)

    return out

# ################################################################################################################################

def collect_consecutive_failure_facts(
    engine:'Engine',
    now:'datetime',
    *,
    depth:'int' = Default_Consecutive_Depth,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures how many of each object's newest outcomes are errors, without a break.
    An object mid-streak also reports its newest failing event, so an alert about
    the streak can point straight at the message that failed.

    The count runs per event type and the object reports the highest one, because sources
    write paired events - a request that always leaves with an OK outcome and a response
    that carries the real one - and counting across types would let the OK halves of failed
    calls hide an unbroken run of failures.
    """

    # Our response to produce
    out:'dictlist' = []

    conditions = [
        event_table.c.outcome != '',
    ]

    # The optional criteria narrow the measures only when set
    if source:
        conditions.append(event_table.c.source == source)

    if object_name:
        conditions.append(event_table.c.object_name == object_name)

    # The newest outcomes of each (source, object, event type) stream, newest first
    row_number = func.row_number().over(
        partition_by=[event_table.c.source, event_table.c.object_name, event_table.c.event_type],
        order_by=event_table.c.id.desc(),
    ).label('row_number')

    ranked = select(
        event_table.c.source,
        event_table.c.object_name,
        event_table.c.event_type,
        event_table.c.outcome,
        row_number,
    ).where(and_(*conditions)).subquery()

    statement = select(
        ranked.c.source,
        ranked.c.object_name,
        ranked.c.event_type,
        ranked.c.outcome,
        ranked.c.row_number,
    ).where(ranked.c.row_number <= depth).order_by(
        ranked.c.source, ranked.c.object_name, ranked.c.event_type, ranked.c.row_number)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    # The newest outcomes of each stream, in newest-first order - the query ordered them
    per_stream:'dict[tuple[str, str, str], list[str]]' = {}

    for row_source, row_object_name, event_type, outcome, _ in rows:
        key = (row_source, row_object_name, event_type)
        per_stream.setdefault(key, []).append(outcome)

    # Each stream's streak is how many errors lead it - the first non-error ends the count.
    # The object reports its highest stream, and an object whose every stream is clean
    # still reports a zero, so a recovered connection resets the measure visibly.
    streaks:'dict[tuple[str, str], int]' = {}

    for (row_source, row_object_name, event_type), outcomes in per_stream.items():

        streak = 0

        for outcome in outcomes:
            if outcome == AuditOutcome.Error:
                streak += 1
            else:
                break

        object_key = (row_source, row_object_name)

        if streak > streaks.get(object_key, 0):
            streaks[object_key] = streak
        else:
            _ = streaks.setdefault(object_key, 0)

    # The newest failing event of each pair, all-time - a streak is about the newest
    # outcomes whenever they happened, so no window narrows this read either
    newest_errors = collect_newest_error_events(engine, source=source, object_name=object_name)

    for (row_source, row_object_name), streak in streaks.items():

        fact = new_fact(row_source, row_object_name)
        fact['consecutive_failures'] = streak

        # Only an object mid-streak has a failing event to point at
        if streak:
            apply_newest_error(fact, newest_errors)

        out.append(fact)

    return out

# ################################################################################################################################

def collect_latency_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the average duration of completed calls within the window, one row
    of measures per (source, object) pair. Only events that carry a duration count -
    a request-sent event has none and would drag the average down to nothing.
    """

    # Our response to produce
    out:'dictlist' = []

    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    conditions = [
        event_table.c.event_time_iso >= window_start_iso,
        event_table.c.duration_ms > 0,
    ]

    # The optional criteria narrow the measures only when set
    if source:
        conditions.append(event_table.c.source == source)

    if object_name:
        conditions.append(event_table.c.object_name == object_name)

    statement = select(
        event_table.c.source,
        event_table.c.object_name,
        func.avg(event_table.c.duration_ms),
    ).where(and_(*conditions)).group_by(event_table.c.source, event_table.c.object_name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for row_source, row_object_name, avg_duration in rows:

        fact = new_fact(row_source, row_object_name)
        fact['avg_duration_ms'] = round(avg_duration)
        fact['window_seconds'] = window_seconds

        out.append(fact)

    return out

# ################################################################################################################################

def collect_auth_failure_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures how many authentication failures the window holds, one row of measures
    per (source, object) pair. Authentication failing is its own event type because
    its remedy is credentials, not networking, so it gets its own measure too.
    """

    # Our response to produce
    out:'dictlist' = []

    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    conditions = [
        event_table.c.event_time_iso >= window_start_iso,
        event_table.c.event_type == AuditEvent.Auth_Failed,
    ]

    # The optional criteria narrow the measures only when set
    if source:
        conditions.append(event_table.c.source == source)

    if object_name:
        conditions.append(event_table.c.object_name == object_name)

    statement = select(
        event_table.c.source,
        event_table.c.object_name,
        func.count(),
    ).where(and_(*conditions)).group_by(event_table.c.source, event_table.c.object_name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for row_source, row_object_name, failure_count in rows:

        fact = new_fact(row_source, row_object_name)
        fact['auth_failure_count'] = failure_count
        fact['window_seconds'] = window_seconds

        out.append(fact)

    return out

# ################################################################################################################################
# ################################################################################################################################
