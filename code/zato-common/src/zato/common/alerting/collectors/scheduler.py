# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The scheduler producer - measures how the scheduler's jobs run against
# their own definitions.

from __future__ import annotations

# stdlib
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import new_fact
from zato.common.audit_log.api import event_attr_table, event_table, AuditEvent, AuditSource
from zato.common.audit_log.scheduler import Attr_Delay_Ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist, stranydict, strintdict
    dictlist = dictlist
    Engine = Engine
    stranydict = stranydict
    strintdict = strintdict

# ################################################################################################################################
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
# ################################################################################################################################
