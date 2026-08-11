# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The absence producers - outstanding backlogs with the age of the oldest waiting
# item, read from the audit database, and feed silence, read from the live channel
# metrics because silence leaves no rows to query.

from __future__ import annotations

# stdlib
from datetime import datetime

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import new_fact
from zato.common.audit_log.api import event_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist, stranydict
    dictlist = dictlist
    Engine = Engine
    stranydict = stranydict

# ################################################################################################################################
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
