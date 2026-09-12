# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The channel producers - the failed responses of a channel sorted by what their HTTP status
# says about who is at fault, and how long a channel that expects traffic has gone without a request.
# A channel has no authentication event of its own - a rejected caller is a response with a 401
# or a 403 - so the status classes are what tell a caller's problem from the service's.

from __future__ import annotations

# stdlib
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.alerting.collectors.common import new_fact, response_event_type_by_source
from zato.common.audit_log.api import event_table, AuditEvent, AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist, strset
    dictlist = dictlist
    Engine = Engine
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

# A status line opens with its three-digit code - `401 Unauthorized` - and the code is what is sorted on.
Status_Code_Length = 3

# The codes that say the caller's credentials were rejected.
auth_failure_codes = ('401', '403')

# The first digit of the codes that say the caller sent what the channel does not accept ..
Client_Error_Class = '4'

# .. and of the codes that say the service behind the channel failed.
Server_Error_Class = '5'

# The event a channel writes the moment a request arrives - its newest one says when the channel last heard from anyone.
Request_Event_Type = AuditEvent.Request_Received

# The one channel kind whose settings can say traffic is expected
Silence_Source = AuditSource.REST_Channel

# ################################################################################################################################
# ################################################################################################################################

def collect_channel_status_facts(
    engine:'Engine',
    window_seconds:'int',
    now:'datetime',
    *,
    source:'str' = '',
    object_name:'str' = '',
    ) -> 'dictlist':
    """ Measures the responses of every channel within the window by their status class, one row
    of measures per channel that answered anything - the 401 and 403 responses as authentication failures,
    every other 4xx as a client error and the 5xx responses as server errors, with the share of 5xx
    among all the channel's responses next to the count. The responses of a channel are read once,
    grouped by their status code, and the groups are sorted into the three measures here.
    """

    # Our response to produce
    out:'dictlist' = []

    window_start = now - timedelta(seconds=window_seconds)
    window_start_iso = window_start.isoformat()

    # Every channel kind with a response event of its own, or the one asked about
    if source:
        if source not in response_event_type_by_source:
            return out
        sources = [source]
    else:
        sources = list(response_event_type_by_source)

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
            status_code,
            func.count(),
        ).where(and_(*conditions)).group_by(event_table.c.object_name, status_code)

        with engine.connect() as connection:
            rows = connection.execute(statement).fetchall()

        # The counts of one channel, by what its status codes say
        totals:'dict[str, int]' = {}
        auth_failures:'dict[str, int]' = {}
        client_errors:'dict[str, int]' = {}
        server_errors:'dict[str, int]' = {}

        for row_object_name, code, count in rows:

            totals[row_object_name] = totals.get(row_object_name, 0) + count

            # A response without a status code says nothing about who is at fault
            if not code:
                continue

            if code in auth_failure_codes:
                auth_failures[row_object_name] = auth_failures.get(row_object_name, 0) + count
            elif code.startswith(Client_Error_Class):
                client_errors[row_object_name] = client_errors.get(row_object_name, 0) + count
            elif code.startswith(Server_Error_Class):
                server_errors[row_object_name] = server_errors.get(row_object_name, 0) + count

        for row_object_name, total in totals.items():

            fact = new_fact(row_source, row_object_name)
            fact['auth_failure_count'] = auth_failures.get(row_object_name, 0)
            fact['client_error_count'] = client_errors.get(row_object_name, 0)
            fact['server_error_count'] = server_errors.get(row_object_name, 0)
            fact['server_error_rate'] = fact['server_error_count'] / total
            fact['window_seconds'] = window_seconds

            out.append(fact)

    return out

# ################################################################################################################################

def collect_channel_silence_facts(engine:'Engine', now:'datetime', expected_names:'strset') -> 'dictlist':
    """ Measures how long each of the given REST channels has gone without a request - the time since
    its newest request event. Only the channels whose settings say traffic is expected are measured,
    so a channel nobody calls raises nothing unless a person asked for it, and one of them that
    never received a request at all has nothing to measure from.
    """

    # Our response to produce
    out:'dictlist' = []

    if not expected_names:
        return out

    conditions = [
        event_table.c.source == Silence_Source,
        event_table.c.event_type == Request_Event_Type,
        event_table.c.object_name.in_(list(expected_names)),
    ]

    statement = select(
        event_table.c.object_name,
        func.max(event_table.c.event_time_iso),
    ).where(and_(*conditions)).group_by(event_table.c.object_name)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for row_object_name, newest_iso in rows:

        newest = datetime.fromisoformat(newest_iso)
        silent = now - newest

        fact = new_fact(Silence_Source, row_object_name)
        fact['silent_seconds'] = int(silent.total_seconds())

        out.append(fact)

    return out

# ################################################################################################################################
# ################################################################################################################################
