# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The MLLP producers - the negative acknowledgments counted by their code, the ones a channel sent back
# and the ones an outgoing connection was answered, and the messages an outgoing connection got no
# acknowledgment for at all.

from __future__ import annotations

# stdlib
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import ack_sources, new_fact, response_event_type_by_source
from zato.common.audit_log.api import event_table, AuditOutcome, AuditSource

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

# The one source whose messages may go unacknowledged - a channel always answers, a connection may not be answered
Connection_Failure_Source = AuditSource.MLLP_Outgoing

# ################################################################################################################################
# ################################################################################################################################

def collect_ack_code_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the negative acknowledgments of every MLLP channel and outgoing connection within the window -
    the ones a channel sent back and the ones a connection was answered - how many carried each code, into
    `fault_counts` by code, one fact per object that had any. An ack row carries its code as the application
    outcome only when the code is negative, so the positive acks group under an empty outcome and are left out.
    Which codes an object alerts on is not known here - the sweep matches the counts against the codes in force
    for each object right before the rule reads them.
    """

    # Our response to produce
    out:'dictlist' = []

    # Every source whose acks are counted, or the one asked about
    if source:
        if source not in ack_sources:
            return out
        sources = [source]
    else:
        sources = list(ack_sources)

    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    for row_source in sources:

        conditions = [
            event_table.c.event_time_iso >= window_start_iso,
            event_table.c.source == row_source,
            event_table.c.event_type == response_event_type_by_source[row_source],
            event_table.c.application_outcome != '',
        ]

        # The optional criterion narrows the measures only when set
        if object_name:
            conditions.append(event_table.c.object_name == object_name)

        statement = select(
            event_table.c.object_name,
            event_table.c.application_outcome,
            func.count(),
        ).where(and_(*conditions)).group_by(event_table.c.object_name, event_table.c.application_outcome)

        with engine.connect() as connection:
            rows = connection.execute(statement).fetchall()

        # The counts of one object, by the code of its acks
        counts_by_object:'dict[str, strintdict]' = {}

        for row_object_name, code, count in rows:

            if row_object_name not in counts_by_object:
                counts_by_object[row_object_name] = {}

            counts = counts_by_object[row_object_name]
            counts[code] = counts.get(code, 0) + count

        for row_object_name in sorted(counts_by_object):

            fact = new_fact(row_source, row_object_name)
            fact['fault_counts'] = counts_by_object[row_object_name]
            fact['window_seconds'] = window_seconds

            out.append(fact)

    return out

# ################################################################################################################################

def collect_mllp_connection_failure_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the messages every outgoing MLLP connection got no acknowledgment for within the window, into
    `connection_failure_count`, one fact per connection that had any. The wrapper writes an ack-received row
    for every exception on the wire - a timeout waiting for the ack, a refused or reset connection, a connection
    closed early, a TLS handshake that failed - with a failed outcome and no application outcome, and that empty
    outcome is what tells such a row from a negative acknowledgment, which carries its code there.
    """

    # Our response to produce
    out:'dictlist' = []

    # The failures of one source alone are counted here
    if source:
        if source != Connection_Failure_Source:
            return out

    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    conditions = [
        event_table.c.event_time_iso >= window_start_iso,
        event_table.c.source == Connection_Failure_Source,
        event_table.c.event_type == response_event_type_by_source[Connection_Failure_Source],
        event_table.c.outcome == AuditOutcome.Error,
        event_table.c.application_outcome == '',
    ]

    # The optional criterion narrows the measures only when set
    if object_name:
        conditions.append(event_table.c.object_name == object_name)

    statement = select(
        event_table.c.object_name,
        func.count(),
    ).where(and_(*conditions)).group_by(event_table.c.object_name).order_by(event_table.c.object_name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for row_object_name, count in rows:

        fact = new_fact(Connection_Failure_Source, row_object_name)
        fact['connection_failure_count'] = count
        fact['window_seconds'] = window_seconds

        out.append(fact)

    return out

# ################################################################################################################################
# ################################################################################################################################
