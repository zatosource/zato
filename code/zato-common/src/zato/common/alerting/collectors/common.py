# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The measurement defaults every fact producer shares, the resting fact each one
# starts from and the newest-failing-event reads the rate producers attach to
# their facts. The thresholds live in the alert rules - the rule engine decides
# what the measures mean, the collectors only report them.

from __future__ import annotations

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.audit_log.api import event_table, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.resubmit import is_event_type_resubmittable

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import stranydict
    Engine = Engine
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The window the error-rate measures cover.
Default_Window_Seconds = 300

# Sources measured over a window of their own - file transfer moves fewer, larger
# messages, so five minutes would rarely hold enough traffic to mean anything, and a
# health check runs on an interval a person chose, which reaches into the hours.
Default_Window_Seconds_By_Source = {
    AuditSource.File_Outgoing: 600,
    AuditSource.REST_Outgoing_Health: 3600,
    AuditSource.SOAP_Outgoing_Health: 3600,
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

        # The id of the object's newest failing event and whether that event's type
        # can be resubmitted per its source's declaration - what lets an alert
        # deep-link straight at the message that failed.
        'last_error_event_id': 0,
        'is_resubmittable': 0,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_newest_error_events(
    engine:'Engine',
    *,
    window_start_iso:'str' = '',
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dict':
    """ The newest failing event of each (source, object) pair - its id and event type,
    keyed by the pair. The type is what says whether that failure can be resubmitted
    from the audit log page.
    """

    # Our response to produce
    out:'dict' = {}

    conditions = [
        event_table.c.outcome == AuditOutcome.Error,
    ]

    # The optional criteria narrow the measures only when set
    if window_start_iso:
        conditions.append(event_table.c.event_time_iso >= window_start_iso)

    if source:
        conditions.append(event_table.c.source == source)

    if object_name:
        conditions.append(event_table.c.object_name == object_name)

    # The newest failing event of each pair is the one with the highest id
    latest_ids = select(func.max(event_table.c.id)).where(and_(*conditions)).group_by(
        event_table.c.source, event_table.c.object_name)

    statement = select(
        event_table.c.id,
        event_table.c.source,
        event_table.c.object_name,
        event_table.c.event_type,
    ).where(event_table.c.id.in_(latest_ids))

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for event_id, row_source, row_object_name, event_type in rows:
        out[(row_source, row_object_name)] = (event_id, event_type)

    return out

# ################################################################################################################################

def apply_newest_error(fact:'stranydict', newest_errors:'dict') -> 'None':
    """ Puts the fact's newest failing event on it - its id, and whether its type
    is resubmittable per the source's own declaration.
    """
    key = (fact['source'], fact['object_name'])

    # An object whose window holds no failing event has nothing to point at
    if key not in newest_errors:
        return

    event_id, event_type = newest_errors[key]

    fact['last_error_event_id'] = event_id

    if is_event_type_resubmittable(fact['source'], event_type):
        fact['is_resubmittable'] = 1

# ################################################################################################################################
# ################################################################################################################################
