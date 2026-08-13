# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The file transfer arrival producer - measures how long each schedule has gone
# without a file arriving, against the arrival window the schedule declares.

from __future__ import annotations

# stdlib
from datetime import datetime

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import new_fact
from zato.common.audit_log.api import event_attr_table, event_table, AuditEvent, AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist, strintdict
    dictlist = dictlist
    Engine = Engine
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

# The attr each schedule-level event carries its schedule's name under.
Attr_Schedule = 'schedule'

# ################################################################################################################################
# ################################################################################################################################

def collect_file_transfer_facts(
    engine:'Engine',
    now:'datetime',
    arrival_windows:'strintdict',
    ) -> 'dictlist':
    """ Measures each file transfer schedule's arrivals - how long ago its newest file
    was handed to the target service and how far past the schedule's own arrival window
    that moment is. The windows arrive from the caller because they live in the schedule
    definitions, not in the audit database. A schedule with no window declares
    no expectation and is not measured, and one that never delivered anything
    has no baseline to be overdue against.
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
# ################################################################################################################################
