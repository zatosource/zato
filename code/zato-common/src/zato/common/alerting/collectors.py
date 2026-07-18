# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The generic collectors - pure functions over the audit database and live channel
# metrics, each returning findings for the engine to route through the rules.
# The absence collector is the general form of "something expected did not happen":
# an event of one type arrived and the expected following event on the same cid
# did not, within the deadline - sent-not-acked for HL7, started-not-terminated
# for a workflow run, always the same anti-join.

from __future__ import annotations

# stdlib
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import and_, case, func, select

# Zato
from zato.common.alerting.model import finding_list, new_finding, FindingKind
from zato.common.audit_log.api import event_table, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.monitoring.health import EndpointMetrics
    from zato.common.typing_ import stranydict
    EndpointMetrics = EndpointMetrics
    Engine = Engine
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

def collect_missing_followups(
    engine:'Engine',
    source:'str',
    begin_event_type:'str',
    end_event_type:'str',
    deadline_seconds:'int',
    now:'datetime',
    *,
    object_name:'str' = '',
    link:'str' = '',
    ) -> 'finding_list':
    """ The clock-driven absence collector - every event of the begin type older
    than the deadline whose cid received no event of the end type becomes a finding.
    Sent-not-acked is this collector parameterized with message-sent and ack-received.
    """

    # Our response to produce
    out:'finding_list' = []

    # Only events that had enough time to receive their follow-up count
    deadline_cutoff = now - timedelta(seconds=deadline_seconds)
    deadline_cutoff_iso = deadline_cutoff.isoformat()

    # The cids the expected follow-up did arrive on
    followed_up = select(event_table.c.cid).where(and_(
        event_table.c.source == source,
        event_table.c.event_type == end_event_type,
    ))

    conditions = [
        event_table.c.source == source,
        event_table.c.event_type == begin_event_type,
        event_table.c.event_time_iso <= deadline_cutoff_iso,
        event_table.c.cid.not_in(followed_up),
    ]

    # The optional criterion narrows the match only when set
    if object_name:
        conditions.append(event_table.c.object_name == object_name)

    statement = select(
        event_table.c.cid,
        event_table.c.object_name,
        event_table.c.msg_id,
        event_table.c.event_time_iso,
    ).where(and_(*conditions)).order_by(event_table.c.id)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for cid, row_object_name, msg_id, event_time_iso in rows:

        message = f'No `{end_event_type}` followed `{begin_event_type}` of `{msg_id or cid}`'
        message += f' on `{row_object_name}` within {deadline_seconds}s, recorded {event_time_iso}'

        finding = new_finding(FindingKind.Missing_Followup, source, row_object_name, message, link=link)
        out.append(finding)

    return out

# ################################################################################################################################

def collect_outstanding_threshold(
    engine:'Engine',
    source:'str',
    begin_event_type:'str',
    end_event_type:'str',
    threshold:'int',
    *,
    object_name:'str' = '',
    link:'str' = '',
    ) -> 'finding_list':
    """ Returns one finding per object whose count of begin events without
    the expected follow-up reached the threshold - detects a growing backlog
    regardless of how long each item has been waiting.
    """

    # Our response to produce
    out:'finding_list' = []

    # The cids the expected follow-up did arrive on
    followed_up = select(event_table.c.cid).where(and_(
        event_table.c.source == source,
        event_table.c.event_type == end_event_type,
    ))

    conditions = [
        event_table.c.source == source,
        event_table.c.event_type == begin_event_type,
        event_table.c.cid.not_in(followed_up),
    ]

    # The optional criterion narrows the match only when set
    if object_name:
        conditions.append(event_table.c.object_name == object_name)

    statement = select(
        event_table.c.object_name,
        func.count(),
    ).where(and_(*conditions)).group_by(event_table.c.object_name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for row_object_name, outstanding_count in rows:

        # Objects below the threshold raise nothing
        if outstanding_count < threshold:
            continue

        message = f'{outstanding_count} outstanding `{begin_event_type}` events on `{row_object_name}`'
        message += f' await `{end_event_type}` (threshold: {threshold})'

        finding = new_finding(FindingKind.Outstanding, source, row_object_name, message, link=link)
        out.append(finding)

    return out

# ################################################################################################################################

def collect_error_rate(
    engine:'Engine',
    source:'str',
    window_seconds:'int',
    threshold:'float',
    now:'datetime',
    *,
    object_name:'str' = '',
    link:'str' = '',
    ) -> 'finding_list':
    """ Returns one finding per object whose share of error outcomes within the window
    reached the threshold - detects degradation while the channel remains operational.
    """

    # Our response to produce
    out:'finding_list' = []

    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    conditions = [
        event_table.c.source == source,
        event_table.c.event_time_iso >= window_start_iso,
    ]

    # The optional criterion narrows the match only when set
    if object_name:
        conditions.append(event_table.c.object_name == object_name)

    # Errors and totals per object, in one pass
    error_case = case((event_table.c.outcome == AuditOutcome.Error, 1), else_=0)

    statement = select(
        event_table.c.object_name,
        func.count(),
        func.sum(error_case),
    ).where(and_(*conditions)).group_by(event_table.c.object_name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for row_object_name, total, errors in rows:

        # Each backend returns its own numeric type for a sum, hence the conversion
        error_rate = float(errors) / total

        # Objects below the threshold raise nothing
        if error_rate < threshold:
            continue

        percent = round(error_rate * 100)
        message = f'Error rate on `{row_object_name}` is {percent}% over the last {window_seconds}s'
        message += f' ({errors} of {total}, threshold: {round(threshold * 100)}%)'

        finding = new_finding(FindingKind.Error_Rate, source, row_object_name, message, link=link)
        out.append(finding)

    return out

# ################################################################################################################################

def collect_feed_silent(
    metrics_by_name:'stranydict',
    source:'str',
    silent_after_seconds:'float',
    *,
    link:'str' = '',
    ) -> 'finding_list':
    """ Returns one finding per channel whose feed has been silent past the threshold -
    runs over the live endpoint metrics the channel state produces, not over
    the audit database, because silence leaves no rows to query.
    """

    # Our response to produce
    out:'finding_list' = []

    for name, metrics in metrics_by_name.items():

        # A channel that never received anything is a configuration matter, not a dead feed
        if not metrics.silence_seconds:
            continue

        # Channels still inside the window raise nothing
        if metrics.silence_seconds < silent_after_seconds:
            continue

        silence = round(metrics.silence_seconds)
        message = f'Feed on `{name}` silent for {silence}s (threshold: {round(silent_after_seconds)}s)'

        finding = new_finding(FindingKind.Feed_Silent, source, name, message, link=link)
        out.append(finding)

    return out

# ################################################################################################################################
# ################################################################################################################################
