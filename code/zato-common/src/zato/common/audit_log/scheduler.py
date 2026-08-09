# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Where the scheduler's execution history lives - one audit event per job run, inserted with
# the running outcome the moment a server picks the fire message up, then updated in place
# when the run completes or times out. Log lines a service emits during the run are stored
# as event body rows so the run detail screen can tail them while the run is still going.

from __future__ import annotations

# stdlib
from json import dumps

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import SCHEDULER
from zato.common.audit_log.api import AuditEvent, AuditSource, get_audit_engine
from zato.common.audit_log.common import event_attr_table, event_body_table, event_table
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import intnone

    # Dummy assignments to satisfy type checkers
    AuditLog = AuditLog
    intnone = intnone

# ################################################################################################################################
# ################################################################################################################################

# The names under which a run's searchable attributes are stored
Attr_Job_ID      = 'job_id'
Attr_Current_Run = 'current_run'
Attr_Delay_Ms    = 'delay_ms'

# The event body kinds log lines are stored under - the kind carries the level bucket
# so per-level counts are one GROUP BY away, while the original level name stays in the body.
Log_Kind_System = 'scheduler-log-system'
Log_Kind_Info   = 'scheduler-log-info'
Log_Kind_Warn   = 'scheduler-log-warn'
Log_Kind_Error  = 'scheduler-log-error'

# All log body kinds, in the order the log summary reports them
Log_Kinds = (Log_Kind_System, Log_Kind_Info, Log_Kind_Warn, Log_Kind_Error)

# How a log record's level name selects the body kind - anything unlisted counts as info
_log_level_kind = {
    'SYSTEM':   Log_Kind_System,
    'WARNING':  Log_Kind_Warn,
    'WARN':     Log_Kind_Warn,
    'ERROR':    Log_Kind_Error,
    'CRITICAL': Log_Kind_Error,
}

# The level name of the entries the scheduler adds on its own
Log_Level_System = 'SYSTEM'

# ################################################################################################################################
# ################################################################################################################################

def format_duration_ms(duration_ms:'int') -> 'str':
    """ Renders a millisecond duration the way the run detail screen shows it.
    """
    if duration_ms == 0:
        out = '< 1ms'
    elif duration_ms < 1000:
        out = f'{duration_ms}ms'
    else:
        seconds = duration_ms / 1000
        out = f'{seconds:.1f}s'

    return out

# ################################################################################################################################

def _get_log_kind(level:'str') -> 'str':
    """ Maps a log record's level name to the event body kind its line is stored under.
    """
    if kind := _log_level_kind.get(level):
        out = kind
    else:
        out = Log_Kind_Info

    return out

# ################################################################################################################################
# ################################################################################################################################

def record_job_start(
    audit_log:'AuditLog',
    job_name:'str',
    *,
    cid:'str',
    job_id:'int',
    current_run:'int',
    planned_fire_time_iso:'str',
    delay_ms:'int',
    service:'str',
    ) -> 'intnone':
    """ Writes the running event for a job run the server is about to execute.
    Returns the event id the completion and log writes update, or None when the audit log
    is turned off, in which case those writes no-op like any other source's would.
    """

    # The searchable attributes every history query keys on
    attrs = {
        Attr_Job_ID: job_id,
        Attr_Current_Run: current_run,
        Attr_Delay_Ms: delay_ms,
    }

    # One event per run - the planned fire time rides in the publication time column
    # and the actual fire time is the event time the insert assigns.
    out = audit_log.insert(
        AuditSource.Scheduler,
        AuditEvent.Job_Executed,
        job_name,
        cid=cid,
        pub_time_iso=planned_fire_time_iso,
        endpoint=service,
        outcome=SCHEDULER.OUTCOME.RUNNING,
        attrs=attrs,
    )

    # The run opens with its own system entry, the same way the run detail screen expects it.
    if out:
        delay_human = format_duration_ms(delay_ms)
        now = utcnow()
        append_job_log_entry(out, now.isoformat(), Log_Level_System, f'Job started, delay: {delay_human}')

    return out

# ################################################################################################################################

def record_job_complete(event_id:'int', *, outcome:'str', duration_ms:'int', error:'str') -> 'None':
    """ Updates a run's event with its final outcome, duration and error, keeping one record
    per run from start to finish.
    """
    engine = get_audit_engine()

    update_statement = event_table.update()
    update_statement = update_statement.where(event_table.c.id == event_id)
    update_statement = update_statement.values(outcome=outcome, duration_ms=duration_ms, data=error)

    with engine.begin() as connection:
        _ = connection.execute(update_statement)

    # The run closes with its own system entry, mirroring the one it opened with.
    duration_human = format_duration_ms(duration_ms)
    now = utcnow()
    append_job_log_entry(event_id, now.isoformat(), Log_Level_System, f'Job completed, outcome: {outcome}, duration: {duration_human}')

# ################################################################################################################################

def record_job_timeout(job_id:'int', current_run:'int', *, elapsed_ms:'int', error:'str') -> 'None':
    """ Marks a run as timed out. The run is located through its job id and run number
    because the timeout arrives from the scheduler process, which never saw the event id.
    """
    engine = get_audit_engine()

    # Find the newest event of this very run ..
    job_id_match = select(event_attr_table.c.event_id).where(
        event_attr_table.c.name == Attr_Job_ID).where(
        event_attr_table.c.value_number == job_id)

    current_run_match = select(event_attr_table.c.event_id).where(
        event_attr_table.c.name == Attr_Current_Run).where(
        event_attr_table.c.value_number == current_run)

    event_query = select(event_table.c.id).where(
        event_table.c.source == AuditSource.Scheduler).where(
        event_table.c.id.in_(job_id_match)).where(
        event_table.c.id.in_(current_run_match)).order_by(
        event_table.c.id.desc()).limit(1)

    with engine.begin() as connection:
        event_id = connection.execute(event_query).scalar()

        # .. a run that was never recorded means the audit log was off when it started ..
        if event_id is None:
            return

        # .. and mark it as timed out in place.
        update_statement = event_table.update()
        update_statement = update_statement.where(event_table.c.id == event_id)
        update_statement = update_statement.values(
            outcome=SCHEDULER.OUTCOME.TIMEOUT, duration_ms=elapsed_ms, data=error)

        _ = connection.execute(update_statement)

    elapsed_human = format_duration_ms(elapsed_ms)
    now = utcnow()
    append_job_log_entry(event_id, now.isoformat(), Log_Level_System, f'Job timed out after {elapsed_human}')

# ################################################################################################################################

def append_job_log_entry(event_id:'int', timestamp_iso:'str', level:'str', message:'str') -> 'None':
    """ Stores one log line a service emitted during a run, as an event body row keyed
    by the run's event id.
    """
    engine = get_audit_engine()

    kind = _get_log_kind(level)

    body = {
        'timestamp_iso': timestamp_iso,
        'level': level,
        'message': message,
    }

    insert_statement = event_body_table.insert()
    insert_statement = insert_statement.values(
        event_id=event_id, kind=kind, event_time_iso=timestamp_iso, data=dumps(body))

    with engine.begin() as connection:
        _ = connection.execute(insert_statement)

# ################################################################################################################################
# ################################################################################################################################
