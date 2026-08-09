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
from zato.common.audit_log.api import event_table, AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist, stranydict
    Engine = Engine
    dictlist = dictlist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The window the error-rate measures cover.
Default_Window_Seconds = 300

# The event types the outstanding measures pair up - sent-not-acked is the canonical absence check.
Default_Begin_Event_Type = AuditEvent.Message_Sent
Default_End_Event_Type   = AuditEvent.Ack_Received

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
    begin_event_type:'str' = Default_Begin_Event_Type,
    end_event_type:'str' = Default_End_Event_Type,
    ) -> 'dictlist':
    """ Runs every fact producer and merges their measures into one fact
    per (source, object) pair - the input the alert rules match over.
    """
    error_rate_facts = collect_error_rate_facts(engine, window_seconds, now)
    outstanding_facts = collect_outstanding_facts(engine, begin_event_type, end_event_type, now)
    silent_facts = collect_feed_silent_facts(metrics_by_name, source)

    # One merged fact per (source, object) pair - later measures land in the same fact
    by_object:'dict[tuple[str, str], stranydict]' = {}

    for fact_list in (error_rate_facts, outstanding_facts, silent_facts):
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
