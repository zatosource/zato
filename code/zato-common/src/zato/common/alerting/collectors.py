# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The fact producers - pure functions over the audit database and live channel metrics.
# Each one measures without judging: error rates with their windows and counts, outstanding
# backlogs with the age of the oldest waiting item, feed silence. The thresholds that used
# to live here are in the alert rules now - the rule engine decides what the measures mean,
# the collectors only report them. One fact per (source, object) pair carries every measure,
# with zero as the resting value, so a rule can reference any measure without erroring out.

from __future__ import annotations

# stdlib
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import and_, case, func, select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.scheduler import Attr_Delay_Ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anylist, dictlist, stranydict, strintdict
    anylist = anylist
    Engine = Engine
    dictlist = dictlist
    stranydict = stranydict
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

# The window the error-rate measures cover.
Default_Window_Seconds = 300

# Sources measured over a window of their own - file transfer moves fewer, larger
# messages, so five minutes would rarely hold enough traffic to mean anything.
Default_Window_Seconds_By_Source = {
    AuditSource.File_Outgoing: 600,
}

# The event types the outstanding measures pair up - sent-not-acked is the canonical absence check.
Default_Begin_Event_Type = AuditEvent.Message_Sent
Default_End_Event_Type   = AuditEvent.Ack_Received

# How many newest outcomes of one object the consecutive-failure measure looks at.
Default_Consecutive_Depth = 3

# The probe sources - each probe collector reads the events one probe job writes.
Probe_Source_Certificate      = AuditSource.Certificate
Probe_Source_Microsoft_Health = AuditSource.Microsoft_Health
Probe_Source_Canary           = AuditSource.Canary

# The attr the certificate probe writes its days-left measure under.
Attr_Days_Left = 'days_left'

# ################################################################################################################################
# ################################################################################################################################

def new_fact(source:'str', object_name:'str') -> 'stranydict':
    """ One per-object fact in its resting state - every measure present, every measure zero,
    so a rule referencing any of them always finds a value.
    """
    out = {
        'source': source,
        'object_name': object_name,
        'error_rate': 0.0,
        'error_count': 0,
        'total_count': 0,
        'window_seconds': 0,
        'outstanding': 0,
        'oldest_waiting_seconds': 0,
        'silent_seconds': 0,

        # How many of the object's newest outcomes are errors, without a break -
        # the measure behind every connection-down rule.
        'consecutive_failures': 0,

        # The average duration of the object's completed calls within the window.
        'avg_duration_ms': 0,

        # How many authentication failures the window holds.
        'auth_failure_count': 0,

        # How many days the object's TLS certificate has left. Zero means unmeasured,
        # which is why the certificate rules also require a value of at least one.
        'cert_days_left': 0,

        # The health state the remote service reports about itself - empty means unmeasured.
        'health_state': '',

        # Whether the object's newest canary check failed.
        'canary_failed': 0,

        # The scheduler measures - how late the job's runs start and how far past
        # its own interval the newest run is. A ratio of 2.0 means twice the interval
        # has passed with no run.
        'start_delay_ms': 0,
        'overdue_ratio': 0.0,
    }

    return out

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
    per (source, object) pair that had any traffic at all.
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

    for row_source, row_object_name, total, errors in rows:

        # Each backend returns its own numeric type for a sum, hence the conversion
        error_count = int(errors)

        fact = new_fact(row_source, row_object_name)
        fact['error_rate'] = error_count / total
        fact['error_count'] = error_count
        fact['total_count'] = total
        fact['window_seconds'] = window_seconds

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

    for (row_source, row_object_name), streak in streaks.items():

        fact = new_fact(row_source, row_object_name)
        fact['consecutive_failures'] = streak

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

def _collect_latest_events(engine:'Engine', source:'str') -> 'anylist':
    """ Returns the newest event of each object of one source - the reading pattern
    every probe collector shares, because a probe's newest event is its current truth.
    """
    latest_ids = select(func.max(event_table.c.id)).where(
        event_table.c.source == source).group_by(event_table.c.object_name)

    statement = select(
        event_table.c.id,
        event_table.c.object_name,
        event_table.c.outcome,
        event_table.c.status,
    ).where(event_table.c.id.in_(latest_ids))

    with engine.connect() as connection:
        out = connection.execute(statement).fetchall()

    return out

# ################################################################################################################################

def collect_certificate_facts(engine:'Engine', now:'datetime') -> 'dictlist':
    """ Surfaces the newest days-left measure the certificate probe wrote about each
    object it checked. The days ride in the probe event's own attr.
    """

    # Our response to produce
    out:'dictlist' = []

    rows = _collect_latest_events(engine, Probe_Source_Certificate)

    if not rows:
        return out

    # The days-left attr of each newest probe event
    event_ids = [row[0] for row in rows]

    attr_query = select(event_attr_table.c.event_id, event_attr_table.c.value_number).where(
        event_attr_table.c.event_id.in_(event_ids)).where(
        event_attr_table.c.name == Attr_Days_Left)

    with engine.connect() as connection:
        attr_rows = connection.execute(attr_query).fetchall()

    days_by_event = {}

    for event_id, days_left in attr_rows:
        days_by_event[event_id] = days_left

    for event_id, object_name, _, _ in rows:

        # A probe that failed to measure wrote no attr - there is nothing to report
        if event_id not in days_by_event:
            continue

        fact = new_fact(Probe_Source_Certificate, object_name)
        fact['cert_days_left'] = round(days_by_event[event_id])

        out.append(fact)

    return out

# ################################################################################################################################

def collect_health_facts(engine:'Engine', now:'datetime') -> 'dictlist':
    """ Surfaces the newest health state the remote-service health probe recorded
    about each service - the state itself travels in the probe event's status column.
    """

    # Our response to produce
    out:'dictlist' = []

    rows = _collect_latest_events(engine, Probe_Source_Microsoft_Health)

    for _, object_name, _, status in rows:

        # A probe that could not reach the health endpoint recorded no state
        if not status:
            continue

        fact = new_fact(Probe_Source_Microsoft_Health, object_name)
        fact['health_state'] = status

        out.append(fact)

    return out

# ################################################################################################################################

def collect_canary_facts(engine:'Engine', now:'datetime') -> 'dictlist':
    """ Surfaces whether each object's newest canary check failed - the canary uploads,
    downloads and removes a test file, so its newest outcome is the current truth
    about the whole transfer path.
    """

    # Our response to produce
    out:'dictlist' = []

    rows = _collect_latest_events(engine, Probe_Source_Canary)

    for _, object_name, outcome, _ in rows:

        fact = new_fact(Probe_Source_Canary, object_name)

        if outcome == AuditOutcome.Error:
            fact['canary_failed'] = 1

        out.append(fact)

    return out

# ################################################################################################################################

def collect_scheduler_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    job_intervals:'strintdict',
    ) -> 'dictlist':
    """ Measures the scheduler's jobs - how late their runs start within the window,
    and how far past its own interval each job's newest run is. The intervals arrive
    from the caller because they live in the job definitions, not in the audit database.
    """

    # Our response to produce
    out:'dictlist' = []

    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    # The worst start delay of each job within the window - the delay rides
    # in every run event's own attr.
    delay_query = select(
        event_table.c.object_name,
        func.max(event_attr_table.c.value_number),
    ).select_from(
        event_table.join(event_attr_table, event_table.c.id == event_attr_table.c.event_id),
    ).where(and_(
        event_table.c.source == AuditSource.Scheduler,
        event_table.c.event_time_iso >= window_start_iso,
        event_attr_table.c.name == Attr_Delay_Ms,
    )).group_by(event_table.c.object_name)

    # When each job ran last, regardless of the window - overdue is about absence
    last_run_query = select(
        event_table.c.object_name,
        func.max(event_table.c.event_time_iso),
    ).where(and_(
        event_table.c.source == AuditSource.Scheduler,
        event_table.c.event_type == AuditEvent.Job_Executed,
    )).group_by(event_table.c.object_name)

    with engine.connect() as connection:
        delay_rows = connection.execute(delay_query).fetchall()
        last_run_rows = connection.execute(last_run_query).fetchall()

    facts_by_name:'dict[str, stranydict]' = {}

    def get_fact(job_name:'str') -> 'stranydict':
        if job_name not in facts_by_name:
            facts_by_name[job_name] = new_fact(AuditSource.Scheduler, job_name)
        return facts_by_name[job_name]

    for job_name, max_delay in delay_rows:
        fact = get_fact(job_name)
        fact['start_delay_ms'] = round(max_delay)
        fact['window_seconds'] = window_seconds

    for job_name, last_run_iso in last_run_rows:

        # A job with no interval on record - a one-time job or one this sweep
        # was not told about - has no notion of being overdue.
        interval = job_intervals.get(job_name)

        if not interval:
            continue

        last_run_time = datetime.fromisoformat(last_run_iso)
        since_last_run = (now - last_run_time).total_seconds()

        fact = get_fact(job_name)
        fact['overdue_ratio'] = round(since_last_run / interval, 2)

    out = list(facts_by_name.values())
    return out

# ################################################################################################################################

def collect_outstanding_facts(
    engine:'Engine',
    begin_event_type:'str',
    end_event_type:'str',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the backlog of begin events without the expected follow-up, one row
    of measures per (source, object) pair - the count of waiting items and the age
    of the oldest one, so rules can watch both a growing backlog and a stalled item.
    """

    # Our response to produce
    out:'dictlist' = []

    # The cids the expected follow-up did arrive on
    followed_up = select(event_table.c.cid).where(
        event_table.c.event_type == end_event_type,
    )

    conditions = [
        event_table.c.event_type == begin_event_type,
        event_table.c.cid.not_in(followed_up),
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
        func.min(event_table.c.event_time_iso),
    ).where(and_(*conditions)).group_by(event_table.c.source, event_table.c.object_name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for row_source, row_object_name, outstanding_count, oldest_iso in rows:

        # How long the oldest waiting item has been waiting
        oldest_time = datetime.fromisoformat(oldest_iso)
        waiting = now - oldest_time
        waiting_seconds = round(waiting.total_seconds())

        fact = new_fact(row_source, row_object_name)
        fact['outstanding'] = outstanding_count
        fact['oldest_waiting_seconds'] = waiting_seconds

        out.append(fact)

    return out

# ################################################################################################################################

def collect_feed_silent_facts(
    metrics_by_name:'stranydict',
    source:'str',
    ) -> 'dictlist':
    """ Measures how long each channel's feed has been silent - runs over the live
    endpoint metrics the channel state produces, not over the audit database,
    because silence leaves no rows to query.
    """

    # Our response to produce
    out:'dictlist' = []

    for name, metrics in metrics_by_name.items():

        # A channel that never received anything is a configuration matter, not a dead feed
        if not metrics.silence_seconds:
            continue

        fact = new_fact(source, name)
        fact['silent_seconds'] = round(metrics.silence_seconds)

        out.append(fact)

    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_facts(
    engine:'Engine',
    metrics_by_name:'stranydict',
    source:'str',
    now:'datetime',
    *,
    window_seconds:'int' = Default_Window_Seconds,
    window_seconds_by_source:'strintdict | None' = None,
    begin_event_type:'str' = Default_Begin_Event_Type,
    end_event_type:'str' = Default_End_Event_Type,
    job_intervals:'strintdict | None' = None,
    ) -> 'dictlist':
    """ Runs every fact producer and merges their measures into one fact
    per (source, object) pair - the input the alert rules match over.
    """
    if window_seconds_by_source is None:
        window_seconds_by_source = Default_Window_Seconds_By_Source

    if job_intervals is None:
        job_intervals = {}

    error_rate_facts = collect_error_rate_facts(engine, window_seconds, now)
    latency_facts = collect_latency_facts(engine, window_seconds, now)
    consecutive_facts = collect_consecutive_failure_facts(engine, now)
    auth_failure_facts = collect_auth_failure_facts(engine, window_seconds, now)
    outstanding_facts = collect_outstanding_facts(engine, begin_event_type, end_event_type, now)
    silent_facts = collect_feed_silent_facts(metrics_by_name, source)
    certificate_facts = collect_certificate_facts(engine, now)
    health_facts = collect_health_facts(engine, now)
    canary_facts = collect_canary_facts(engine, now)
    scheduler_facts = collect_scheduler_facts(engine, window_seconds, now, job_intervals)

    # A source with a window of its own is measured again over that window,
    # and its own measures replace the default-window ones below.
    override_error_rate_facts:'dictlist' = []
    override_latency_facts:'dictlist' = []

    for override_source, override_window in window_seconds_by_source.items():
        override_error_rate_facts.extend(collect_error_rate_facts(engine, override_window, now, source=override_source))
        override_latency_facts.extend(collect_latency_facts(engine, override_window, now, source=override_source))

    # The default-window measures of an overridden source step aside
    overridden_sources = set(window_seconds_by_source)

    error_rate_facts = [fact for fact in error_rate_facts if fact['source'] not in overridden_sources]
    latency_facts = [fact for fact in latency_facts if fact['source'] not in overridden_sources]

    error_rate_facts.extend(override_error_rate_facts)
    latency_facts.extend(override_latency_facts)

    # One merged fact per (source, object) pair - later measures land in the same fact
    by_object:'dict[tuple[str, str], stranydict]' = {}

    fact_lists = (
        error_rate_facts,
        latency_facts,
        consecutive_facts,
        auth_failure_facts,
        outstanding_facts,
        silent_facts,
        certificate_facts,
        health_facts,
        canary_facts,
        scheduler_facts,
    )

    for fact_list in fact_lists:
        for fact in fact_list:

            key = (fact['source'], fact['object_name'])

            if key in by_object:
                merged = by_object[key]

                # Only the measures this producer actually took overwrite the resting zeroes
                for name, value in fact.items():
                    if value:
                        merged[name] = value
            else:
                by_object[key] = fact

    out = list(by_object.values())
    return out

# ################################################################################################################################
# ################################################################################################################################
