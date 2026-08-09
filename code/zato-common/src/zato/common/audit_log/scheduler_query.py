# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The read side of the scheduler's execution history - every function returns the very
# JSON shape the dashboard's scheduler screens consume, with one audit event standing
# for one job run and the log lines coming from the run's event body rows.

from __future__ import annotations

# stdlib
from datetime import datetime, timezone
from json import loads

# SQLAlchemy
from sqlalchemy import func, or_, select

# Zato
from zato.common.api import SCHEDULER
from zato.common.audit_log.api import AuditSource, get_audit_engine
from zato.common.audit_log.common import event_attr_table, event_body_table, event_table
from zato.common.audit_log.scheduler import Attr_Current_Run, Attr_Delay_Ms, Attr_Job_ID, Log_Kind_Error, Log_Kind_Info, \
    Log_Kind_System, Log_Kind_Warn, Log_Kinds

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, dictlist, intlistnone, intnone, strlist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict
    anylist = anylist
    dictlist = dictlist
    intlistnone = intlistnone
    intnone = intnone
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# How many time buckets the chart is aggregated into
Chart_Bucket_Count = 120

# Window the chart falls back to when every event carries the same timestamp,
# or when the caller asks for a range of zero length.
_default_chart_range_ms = 3_600_000

# How a log body kind maps to its bucket in a record's log summary
_log_kind_summary = {
    Log_Kind_System: 'system',
    Log_Kind_Info:   'info',
    Log_Kind_Warn:   'warn',
    Log_Kind_Error:  'error',
}

# The outcomes the chart counts, keyed exactly like its response buckets
_chart_outcomes = (
    SCHEDULER.OUTCOME.OK,
    SCHEDULER.OUTCOME.ERROR,
    SCHEDULER.OUTCOME.TIMEOUT,
    SCHEDULER.OUTCOME.SKIPPED_ALREADY_IN_FLIGHT,
)

# All the outcomes a per-job aggregate counts
_countable_outcomes = (
    SCHEDULER.OUTCOME.OK,
    SCHEDULER.OUTCOME.ERROR,
    SCHEDULER.OUTCOME.TIMEOUT,
    SCHEDULER.OUTCOME.RUNNING,
    SCHEDULER.OUTCOME.SKIPPED_ALREADY_IN_FLIGHT,
)

# How many of a job's newest outcomes its summary reports
_recent_outcome_count = 10

# ################################################################################################################################
# ################################################################################################################################

def _parse_outcome_filter(outcomes:'any_') -> 'strlist | None':
    """ Turns an outcome filter - a list of labels or a comma-separated string - into
    an allow-list, or None when everything is allowed. Running records are always allowed
    through so an in-progress run never disappears from a filtered view.
    """
    if not outcomes:
        return None

    if isinstance(outcomes, str):
        if outcomes == SCHEDULER.OUTCOME.All:
            return None
        items = outcomes.split(',')
    else:
        items = list(outcomes)

    out:'strlist' = []

    for item in items:
        item = item.strip()
        if item == SCHEDULER.OUTCOME.All:
            return None
        out.append(item)

    if SCHEDULER.OUTCOME.RUNNING not in out:
        out.append(SCHEDULER.OUTCOME.RUNNING)

    return out

# ################################################################################################################################

def _parse_iso_ms(value:'str') -> 'int':
    """ Parses an ISO timestamp into milliseconds since the epoch, 0 when it cannot be parsed.
    """
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return 0

    # A timestamp with no timezone is taken to be UTC
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    out = int(parsed.timestamp() * 1000)
    return out

# ################################################################################################################################

def _ms_to_iso(value_ms:'int') -> 'str':
    """ Renders milliseconds since the epoch as an ISO timestamp in UTC.
    """
    parsed = datetime.fromtimestamp(value_ms / 1000, timezone.utc)

    out = parsed.isoformat()
    return out

# ################################################################################################################################

def _attr_match(name:'str', value:'any_') -> 'any_':
    """ Builds a subquery of event ids whose given attribute equals the given number.
    """
    out = select(event_attr_table.c.event_id).where(
        event_attr_table.c.name == name).where(
        event_attr_table.c.value_number == value)

    return out

# ################################################################################################################################

def _job_events(job_name:'str') -> 'any_':
    """ Builds the base select of one job's run events, newest first.
    """
    out = select(event_table).where(
        event_table.c.source == AuditSource.Scheduler).where(
        event_table.c.object_name == job_name)

    return out

# ################################################################################################################################

def _rows_to_records(connection:'any_', rows:'anylist', job_id:'intnone'=None) -> 'dictlist':
    """ Turns event rows into the record dicts the history screens consume, joining in
    each run's attributes and per-level log line counts.
    """

    # Our response to produce
    out:'dictlist' = []

    event_ids:'anylist' = []
    for row in rows:
        event_ids.append(row.id)

    if not event_ids:
        return out

    # One query brings in every row's attributes ..
    attr_query = select(event_attr_table.c.event_id, event_attr_table.c.name, event_attr_table.c.value_number).where(
        event_attr_table.c.event_id.in_(event_ids))

    attrs_by_event:'anydict' = {}

    for attr_row in connection.execute(attr_query):
        event_attrs = attrs_by_event.setdefault(attr_row.event_id, {})
        event_attrs[attr_row.name] = attr_row.value_number

    # .. and one more counts every row's log lines per level bucket.
    log_query = select(event_body_table.c.event_id, event_body_table.c.kind, func.count().label('line_count')).where(
        event_body_table.c.event_id.in_(event_ids)).where(
        event_body_table.c.kind.in_(Log_Kinds)).group_by(
        event_body_table.c.event_id, event_body_table.c.kind)

    log_counts_by_event:'anydict' = {}

    for log_row in connection.execute(log_query):
        event_counts = log_counts_by_event.setdefault(log_row.event_id, {})
        bucket = _log_kind_summary[log_row.kind]
        event_counts[bucket] = log_row.line_count

    for row in rows:

        event_attrs = attrs_by_event.setdefault(row.id, {})
        event_counts = log_counts_by_event.setdefault(row.id, {})

        # History queries already know the job the records belong to,
        # cross-job queries read each record's own attribute instead.
        if job_id is None:
            record_job_id = int(event_attrs[Attr_Job_ID])
        else:
            record_job_id = job_id

        # A run that is still going has no duration, and only a failed one carries an error
        if row.outcome == SCHEDULER.OUTCOME.RUNNING:
            duration_ms = None
        else:
            duration_ms = row.duration_ms

        if row.data:
            error = row.data
        else:
            error = None

        out.append({
            'job_id': record_job_id,
            'job_name': row.object_name,
            'planned_fire_time_iso': row.pub_time_iso,
            'actual_fire_time_iso': row.event_time_iso,
            'delay_ms': int(event_attrs[Attr_Delay_Ms]),
            'outcome': row.outcome,
            'current_run': int(event_attrs[Attr_Current_Run]),
            'duration_ms': duration_ms,
            'error': error,
            'outcome_ctx': None,
            'log_summary': {
                'system': event_counts.setdefault('system', 0),
                'info': event_counts.setdefault('info', 0),
                'warn': event_counts.setdefault('warn', 0),
                'error': event_counts.setdefault('error', 0),
            },
        })

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_history_page(
    job_id:'int',
    job_name:'str',
    offset:'int',
    limit:'int',
    outcomes:'any_',
    since_iso:'str' = '',
    ) -> 'anydict':
    """ Returns one page of a job's execution records, newest first, along with the total
    count of completed records matching the filter.
    """
    engine = get_audit_engine()
    allowed = _parse_outcome_filter(outcomes)

    rows_query = _job_events(job_name)
    total_query = select(func.count()).where(
        event_table.c.source == AuditSource.Scheduler).where(
        event_table.c.object_name == job_name).where(
        event_table.c.outcome != SCHEDULER.OUTCOME.RUNNING)

    if since_iso:
        rows_query = rows_query.where(event_table.c.event_time_iso >= since_iso)
        total_query = total_query.where(event_table.c.event_time_iso >= since_iso)

    if allowed:
        rows_query = rows_query.where(event_table.c.outcome.in_(allowed))
        total_query = total_query.where(event_table.c.outcome.in_(allowed))

    rows_query = rows_query.order_by(
        event_table.c.event_time_iso.desc(), event_table.c.id.desc()).offset(offset).limit(limit)

    with engine.connect() as connection:
        rows = connection.execute(rows_query).fetchall()
        total = connection.execute(total_query).scalar()
        records = _rows_to_records(connection, rows, job_id)

    out = {'records': records, 'total': total}
    return out

# ################################################################################################################################

def get_history_since(
    job_id:'int',
    job_name:'str',
    since_iso:'str',
    outcomes:'any_',
    running_runs:'intlistnone' = None,
    range_since_iso:'str' = '',
    ) -> 'anydict':
    """ Returns a job's records added since the given timestamp, newest first. Runs named
    in running_runs are always included so a poll can watch them complete no matter the filter.
    """
    engine = get_audit_engine()
    allowed = _parse_outcome_filter(outcomes)

    # The rows a poll asks for - everything new enough and allowed through the filter ..
    new_enough = event_table.c.event_time_iso >= since_iso

    if allowed:
        matches_filter = new_enough & event_table.c.outcome.in_(allowed)
    else:
        matches_filter = new_enough

    # .. with the watched runs riding along regardless.
    if running_runs:
        run_match = select(event_attr_table.c.event_id).where(
            event_attr_table.c.name == Attr_Current_Run).where(
            event_attr_table.c.value_number.in_(running_runs))
        matches_filter = or_(matches_filter, event_table.c.id.in_(run_match))

    rows_query = _job_events(job_name).where(matches_filter).order_by(
        event_table.c.event_time_iso.desc(), event_table.c.id.desc())

    total_query = select(func.count()).where(
        event_table.c.source == AuditSource.Scheduler).where(
        event_table.c.object_name == job_name).where(
        event_table.c.outcome != SCHEDULER.OUTCOME.RUNNING)

    if allowed:
        total_query = total_query.where(event_table.c.outcome.in_(allowed))

    if range_since_iso:
        total_query = total_query.where(event_table.c.event_time_iso >= range_since_iso)

    with engine.connect() as connection:
        rows = connection.execute(rows_query).fetchall()
        total = connection.execute(total_query).scalar()
        records = _rows_to_records(connection, rows, job_id)

    out = {'rows': records, 'total': total}
    return out

# ################################################################################################################################

def get_run_detail(job_id:'int', job_name:'str', current_run:'int') -> 'anydict':
    """ Returns a single run's record along with the run numbers just before and after it,
    for the run detail screen's navigation.
    """
    engine = get_audit_engine()

    run_match = _attr_match(Attr_Current_Run, current_run)
    row_query = _job_events(job_name).where(event_table.c.id.in_(run_match)).order_by(
        event_table.c.id.desc()).limit(1)

    # Run numbers grow monotonically, so the neighbours are the nearest ones either side
    neighbour_base = select(event_attr_table.c.value_number).select_from(
        event_attr_table.join(event_table, event_table.c.id == event_attr_table.c.event_id)).where(
        event_table.c.source == AuditSource.Scheduler).where(
        event_table.c.object_name == job_name).where(
        event_attr_table.c.name == Attr_Current_Run)

    prev_query = neighbour_base.where(event_attr_table.c.value_number < current_run).order_by(
        event_attr_table.c.value_number.desc()).limit(1)

    next_query = neighbour_base.where(event_attr_table.c.value_number > current_run).order_by(
        event_attr_table.c.value_number.asc()).limit(1)

    with engine.connect() as connection:
        rows = connection.execute(row_query).fetchall()

        if not rows:
            out = {'record': None, 'prev_run': None, 'next_run': None}
            return out

        records = _rows_to_records(connection, rows, job_id)

        prev_run = connection.execute(prev_query).scalar()
        next_run = connection.execute(next_query).scalar()

    if prev_run is not None:
        prev_run = int(prev_run)

    if next_run is not None:
        next_run = int(next_run)

    out = {'record': records[0], 'prev_run': prev_run, 'next_run': next_run}
    return out

# ################################################################################################################################

def get_log_entries(job_name:'str', current_run:'int', since_idx:'int') -> 'dictlist':
    """ Returns a run's log lines in the order they were written, starting at the given
    index so a live tail only ever fetches what it has not seen yet.
    """
    engine = get_audit_engine()

    run_match = _attr_match(Attr_Current_Run, current_run)
    event_query = select(event_table.c.id).where(
        event_table.c.source == AuditSource.Scheduler).where(
        event_table.c.object_name == job_name).where(
        event_table.c.id.in_(run_match)).order_by(
        event_table.c.id.desc()).limit(1)

    # Our response to produce
    out:'dictlist' = []

    with engine.connect() as connection:
        event_id = connection.execute(event_query).scalar()

        if event_id is None:
            return out

        body_query = select(event_body_table.c.data).where(
            event_body_table.c.event_id == event_id).where(
            event_body_table.c.kind.in_(Log_Kinds)).order_by(
            event_body_table.c.id.asc()).offset(since_idx)

        for body_row in connection.execute(body_query):
            out.append(loads(body_row.data))

    return out

# ################################################################################################################################

def get_chart_data(since_iso:'str' = '', until_iso:'str' = '') -> 'anydict':
    """ Returns all jobs' executions pre-aggregated into fixed time buckets with per-outcome
    counts. With both boundaries given the bucket grid spans exactly that window, so the chart
    never shifts between polls - without them the grid spans the data itself.
    """
    engine = get_audit_engine()

    # A fixed window needs both boundaries, parseable and the right way around
    fixed_window = None

    if since_iso and until_iso:
        since_ms = _parse_iso_ms(since_iso)
        until_ms = _parse_iso_ms(until_iso)

        if since_ms > 0:
            if until_ms > since_ms:
                fixed_window = (since_ms, until_ms)

    events_query = select(event_table.c.event_time_iso, event_table.c.outcome).where(
        event_table.c.source == AuditSource.Scheduler).where(
        event_table.c.outcome.in_(_chart_outcomes))

    # Collect every countable execution as its epoch milliseconds and outcome ..
    collected:'anylist' = []

    with engine.connect() as connection:
        for event_row in connection.execute(events_query):
            event_ms = _parse_iso_ms(event_row.event_time_iso)

            if fixed_window:
                window_since, window_until = fixed_window
                if event_ms < window_since:
                    continue
                if event_ms >= window_until:
                    continue

            collected.append((event_ms, event_row.outcome))

    # .. work out the window the buckets span ..
    if fixed_window:
        window_min, window_max = fixed_window
    elif not collected:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        window_min, window_max = now_ms, now_ms
    else:
        window_min = collected[0][0]
        window_max = collected[0][0]

        for event_ms, _outcome in collected:
            if event_ms < window_min:
                window_min = event_ms
            if event_ms > window_max:
                window_max = event_ms

        # Every event at the same instant still needs a window with some width
        if window_max == window_min:
            window_min = window_max - _default_chart_range_ms

    time_range = window_max - window_min

    if time_range == 0:
        effective_range = _default_chart_range_ms
    else:
        effective_range = time_range

    # .. count each event into its bucket ..
    bucket_counts:'anylist' = []

    for _ in range(Chart_Bucket_Count):
        bucket_counts.append({
            SCHEDULER.OUTCOME.OK: 0,
            SCHEDULER.OUTCOME.ERROR: 0,
            SCHEDULER.OUTCOME.TIMEOUT: 0,
            SCHEDULER.OUTCOME.SKIPPED_ALREADY_IN_FLIGHT: 0,
        })

    for event_ms, outcome in collected:
        offset_ms = event_ms - window_min
        raw_index = offset_ms * Chart_Bucket_Count // effective_range
        bucket_index = min(max(raw_index, 0), Chart_Bucket_Count - 1)
        bucket_counts[bucket_index][outcome] += 1

    # .. and render the buckets with their exact boundaries.
    buckets:'dictlist' = []

    for bucket_index, counts in enumerate(bucket_counts):
        start_ms = window_min + bucket_index * effective_range // Chart_Bucket_Count
        end_ms = window_min + (bucket_index + 1) * effective_range // Chart_Bucket_Count

        buckets.append({
            'start_iso': _ms_to_iso(start_ms),
            'end_iso': _ms_to_iso(end_ms),
            'ok': counts[SCHEDULER.OUTCOME.OK],
            'error': counts[SCHEDULER.OUTCOME.ERROR],
            'timeout': counts[SCHEDULER.OUTCOME.TIMEOUT],
            'skipped_already_in_flight': counts[SCHEDULER.OUTCOME.SKIPPED_ALREADY_IN_FLIGHT],
        })

    out = {
        'buckets': buckets,
        'min_time_iso': _ms_to_iso(window_min),
        'max_time_iso': _ms_to_iso(window_max),
    }

    return out

# ################################################################################################################################

def get_timeline_events_since(since_iso:'str' = '', limit:'int' = 0) -> 'dictlist':
    """ Returns every job's executions strictly after the given timestamp, newest first,
    for the dashboard's recent activity table.
    """
    engine = get_audit_engine()

    events_query = select(event_table).where(event_table.c.source == AuditSource.Scheduler)

    if since_iso:
        events_query = events_query.where(event_table.c.event_time_iso > since_iso)

    events_query = events_query.order_by(event_table.c.event_time_iso.desc(), event_table.c.id.desc())

    if limit:
        events_query = events_query.limit(limit)

    with engine.connect() as connection:
        rows = connection.execute(events_query).fetchall()
        records = _rows_to_records(connection, rows)

    # Our response to produce
    out:'dictlist' = []

    for record in records:
        out.append({
            'outcome': record['outcome'],
            'actual_fire_time_iso': record['actual_fire_time_iso'],
            'job_id': record['job_id'],
            'job_name': record['job_name'],
            'duration_ms': record['duration_ms'],
            'error': record['error'],
            'outcome_ctx': record['outcome_ctx'],
            'current_run': record['current_run'],
            'planned_fire_time_iso': record['planned_fire_time_iso'],
        })

    return out

# ################################################################################################################################

def get_job_aggregates() -> 'anydict':
    """ Returns per-job history aggregates keyed by job name - outcome counts, the newest
    run's outcome, duration and time, and the last few outcomes for the activity strip.
    These are the fields the dashboard merges into the scheduler's runtime job summaries.
    """
    engine = get_audit_engine()

    counts_query = select(event_table.c.object_name, event_table.c.outcome, func.count().label('outcome_count')).where(
        event_table.c.source == AuditSource.Scheduler).group_by(
        event_table.c.object_name, event_table.c.outcome)

    # Our response to produce
    out:'anydict' = {}

    with engine.connect() as connection:

        # Every job that ever ran gets its outcome counts first ..
        for count_row in connection.execute(counts_query):

            if count_row.object_name not in out:

                zero_counts:'anydict' = {}
                for outcome in _countable_outcomes:
                    zero_counts[outcome] = 0

                out[count_row.object_name] = {
                    'outcome_counts': zero_counts,
                    'last_outcome': None,
                    'last_duration_ms': None,
                    'last_run_utc': None,
                    'recent_outcomes': [],
                }

            aggregate = out[count_row.object_name]

            if count_row.outcome in aggregate['outcome_counts']:
                aggregate['outcome_counts'][count_row.outcome] = count_row.outcome_count

        # .. and the newest few records fill in the rest, oldest of them first.
        for job_name, aggregate in out.items():

            recent_query = select(
                event_table.c.outcome, event_table.c.duration_ms, event_table.c.event_time_iso).where(
                event_table.c.source == AuditSource.Scheduler).where(
                event_table.c.object_name == job_name).order_by(
                event_table.c.event_time_iso.desc(), event_table.c.id.desc()).limit(_recent_outcome_count)

            recent_rows = connection.execute(recent_query).fetchall()

            if not recent_rows:
                continue

            newest = recent_rows[0]
            aggregate['last_outcome'] = newest.outcome
            aggregate['last_run_utc'] = newest.event_time_iso

            # The newest completed run is the one whose duration the dashboard shows
            for recent_row in recent_rows:
                if recent_row.outcome != SCHEDULER.OUTCOME.RUNNING:
                    aggregate['last_duration_ms'] = recent_row.duration_ms
                    break

            recent_outcomes:'anylist' = []
            for recent_row in reversed(recent_rows):
                recent_outcomes.append(recent_row.outcome)

            aggregate['recent_outcomes'] = recent_outcomes

    return out

# ################################################################################################################################
# ################################################################################################################################
