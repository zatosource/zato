# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The outgoing connection producer - the responses an outgoing REST or SOAP connection received within the window,
# counted by their status code, and the calls that failed before any response arrived. A response carries
# its HTTP status line, `503 Service Unavailable`, and a failed call one of the transport statuses,
# `timeout` or `connection-error`, so one query over the connection's response events sorts both out.
# Which codes a connection alerts on is not known here - the sweep matches the per-code counts against
# the codes in force for each connection right before the rule reads them.

from __future__ import annotations

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import new_fact, outgoing_sources, response_event_type_by_source
from zato.common.audit_log.api import event_table
from zato.common.audit_log.common import transport_statuses

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist, strintdict
    datetime = datetime
    dictlist = dictlist
    Engine = Engine
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

# A status line opens with its three-digit code - `401 Unauthorized` - and the code is what is counted on.
Status_Code_Length = 3

# ################################################################################################################################
# ################################################################################################################################

def _add_count(counts_by_object:'dict[str, strintdict]', object_name:'str', key:'str', count:'int') -> 'None':
    """ Adds one row's count to an object's counts under its key - a code or a fault code.
    """
    if object_name not in counts_by_object:
        counts_by_object[object_name] = {}

    counts = counts_by_object[object_name]
    counts[key] = counts.get(key, 0) + count

# ################################################################################################################################

def collect_outgoing_status_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the responses of every outgoing connection within the window - how many arrived with each
    status code, into `status_counts` by code, how many arrived as a SOAP fault of each fault code, into
    `fault_counts` by code, and how many calls failed before any response arrived, into `connection_failure_count`,
    one fact per connection that has any of the three. A failed call's status is a transport status rather than
    a code, so it never lands among the codes, and a fault is a fault and never a status code either, so three
    faults raise SOAP_Faults once rather than SOAP_Faults and Status_Codes together.
    """

    # Our response to produce
    out:'dictlist' = []

    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    # Every outgoing source counted by status, or the one asked about
    if source:
        if source not in outgoing_sources:
            return out
        sources = [source]
    else:
        sources = list(outgoing_sources)

    status_code = func.substr(event_table.c.status, 1, Status_Code_Length)

    for row_source in sources:

        conditions = [
            event_table.c.event_time_iso >= window_start_iso,
            event_table.c.source == row_source,
            event_table.c.event_type == response_event_type_by_source[row_source],
        ]

        # The optional criterion narrows the measures only when set
        if object_name:
            conditions.append(event_table.c.object_name == object_name)

        statement = select(
            event_table.c.object_name,
            event_table.c.status,
            status_code,
            event_table.c.application_outcome,
            func.count(),
        ).where(and_(*conditions)).group_by(
            event_table.c.object_name, event_table.c.status, event_table.c.application_outcome)

        with engine.connect() as connection:
            rows = connection.execute(statement).fetchall()

        # The counts of one connection - its responses by code, its faults by fault code and its calls that never got one
        status_counts_by_object:'dict[str, strintdict]' = {}
        fault_counts_by_object:'dict[str, strintdict]' = {}
        failures_by_object:'strintdict' = {}

        for row_object_name, status, code, application_outcome, count in rows:

            if status in transport_statuses:
                failures_by_object[row_object_name] = failures_by_object.get(row_object_name, 0) + count
                continue

            # A response with an application outcome is a SOAP fault of that code and nothing else
            if application_outcome:
                _add_count(fault_counts_by_object, row_object_name, application_outcome, count)
                continue

            # A response without a status code says nothing about what it was
            if not code:
                continue

            if not code.isdigit():
                continue

            _add_count(status_counts_by_object, row_object_name, code, count)

        # A connection with counts of any kind gets a fact carrying all of them
        object_names = set(status_counts_by_object) | set(fault_counts_by_object) | set(failures_by_object)

        for row_object_name in sorted(object_names):

            fact = new_fact(row_source, row_object_name)

            if row_object_name in status_counts_by_object:
                fact['status_counts'] = status_counts_by_object[row_object_name]

            if row_object_name in fault_counts_by_object:
                fact['fault_counts'] = fault_counts_by_object[row_object_name]

            if row_object_name in failures_by_object:
                fact['connection_failure_count'] = failures_by_object[row_object_name]

            fact['window_seconds'] = window_seconds

            out.append(fact)

    return out

# ################################################################################################################################
# ################################################################################################################################
