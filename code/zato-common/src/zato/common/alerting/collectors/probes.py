# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The probe readers - each one surfaces the newest event a probe job wrote,
# because a probe's newest event is its current truth about the object it checked.

from __future__ import annotations

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.alerting.collectors.common import new_fact, Attr_Days_Left, Probe_Source_Certificate, \
    Probe_Source_Microsoft_Health, Probe_Source_Test_Transfer
from zato.common.audit_log.api import event_attr_table, event_table, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anylist, dictlist
    anylist = anylist
    datetime = datetime
    dictlist = dictlist
    Engine = Engine

# ################################################################################################################################
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
    event_ids = []

    for row in rows:
        event_ids.append(row[0])

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

def collect_test_transfer_facts(engine:'Engine', now:'datetime') -> 'dictlist':
    """ Surfaces whether each object's newest test transfer check failed - the test
    transfer uploads, downloads and removes a test file, so its newest outcome is
    the current truth about the whole transfer path.
    """

    # Our response to produce
    out:'dictlist' = []

    rows = _collect_latest_events(engine, Probe_Source_Test_Transfer)

    for _, object_name, outcome, _ in rows:

        fact = new_fact(Probe_Source_Test_Transfer, object_name)

        if outcome == AuditOutcome.Error:
            fact['test_transfer_failed'] = 1

        out.append(fact)

    return out

# ################################################################################################################################
# ################################################################################################################################
