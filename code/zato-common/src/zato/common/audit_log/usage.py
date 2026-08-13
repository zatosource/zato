# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Usage reporting - a per-object aggregate built over the audit events channels and
# outgoing connections already record. Each row counts the completed exchanges of one
# caller with one object over the range, where the caller is the security definition
# that authenticated the requests, when there was one. The table answers "who still
# calls this channel" and "how much does this connection run", which is what retiring
# a deprecated API needs, and it renders as CSV too.

from __future__ import annotations

# stdlib
import csv
from dataclasses import dataclass
from io import StringIO
from urllib.parse import quote

# SQLAlchemy
from sqlalchemy import and_, or_, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table, get_audit_engine
from zato.common.audit_log.reports import get_range_cutoff
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import any_, anylist, anytuple, strlist

    # Dummy assignments to satisfy type checkers
    datetime = datetime
    any_ = any_
    anylist = anylist
    anytuple = anytuple
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
usage_row_list      = list['UsageRow']
usage_state_dict    = dict['anytuple', '_UsageState']
object_options_dict = dict[str, list[str]]

# ################################################################################################################################
# ################################################################################################################################

# What a caller that authenticated with no security definition is reported as
Caller_Anonymous = 'Anonymous'

# What an outgoing connection's row shows in the caller column - nobody calls out to us
# through one, so there is no caller to name
Caller_Outgoing = '-'

# The sources the usage page covers and, per source, the event marking one completed
# exchange - the completing event rather than request-sent, so a destination delivery,
# whose hop recorder writes an extra request-sent row, is never counted twice.
# The order is the display order of the page's type filter - each protocol's
# channels and outgoing connections stand together.
_usage_event_by_source = {
    AuditSource.REST_Channel:  AuditEvent.Response_Sent,
    AuditSource.REST_Outgoing: AuditEvent.Response_Received,
    AuditSource.SOAP_Channel:  AuditEvent.Response_Sent,
    AuditSource.MLLP_Channel:  AuditEvent.Ack_Sent,
    AuditSource.MLLP_Outgoing: AuditEvent.Ack_Received,
    AuditSource.FHIR:          AuditEvent.Response_Received,
}

# The covered sources in their display order - what the page's source filter offers
Usage_Sources = tuple(_usage_event_by_source)

# The report's outgoing sources, whose rows carry no caller of their own
_outgoing_sources = {AuditSource.REST_Outgoing, AuditSource.MLLP_Outgoing, AuditSource.FHIR}

# The CSV headers of the usage table, matching the columns the page renders
Usage_Headers = ('channel', 'type', 'caller', 'calls', 'first_call', 'last_call')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class UsageRow:
    """ The calls one caller exchanged with one object over the range.
    """
    channel:    str = ''
    source:     str = ''
    caller:     str = ''
    calls:      int = 0
    first_call: str = ''
    last_call:  str = ''

    # What the object's source is called on the page - the view fills it in
    type_label: str = ''

    # The filtered audit log page behind this row
    link: str = ''

# ################################################################################################################################
# ################################################################################################################################

class _UsageState:
    """ The aggregation state of one usage row in the making.
    """

    def __init__(self) -> 'None':
        self.calls:'int' = 0
        self.first_call:'str' = ''
        self.last_call:'str' = ''

# ################################################################################################################################
# ################################################################################################################################

def _audit_log_link(source:'str', channel:'str') -> 'str':
    """ Builds the drill-down path from one usage row to the filtered audit log page.
    """
    # The name is user-defined and can hold characters that would split the query string
    channel = quote(channel)

    out = f'/zato/audit-log/?source={source}&object_name={channel}&cluster={default_cluster_id}'
    return out

# ################################################################################################################################

def normalize_sources(sources:'strlist') -> 'strlist':
    """ Keeps only the sources the usage page covers - anything else came from
    the address bar and never reaches a query. An empty list stays empty,
    which downstream means all the covered sources.
    """
    out = [item for item in sources if item in _usage_event_by_source]
    return out

# ################################################################################################################################

def _completed_exchange_matches(sources:'strlist') -> 'any_':
    """ The condition matching one completed exchange of any of the given sources -
    each source pairs with its own completing event type.
    """
    # An empty filter means every covered source is reported on
    if not sources:
        sources = list(_usage_event_by_source)

    per_source = []

    for source in sources:
        event_type = _usage_event_by_source[source]
        matches = and_(
            event_table.c.source == source,
            event_table.c.event_type == event_type,
        )
        per_source.append(matches)

    out = or_(*per_source)
    return out

# ################################################################################################################################

def _load_usage_events(cutoff_iso:'str', sources:'strlist', objects:'strlist') -> 'anylist':
    """ Reads all the completed exchanges recorded after the cutoff, oldest first -
    channel responses are audited after authentication, so each one knows its caller.
    """
    exchange_matches = _completed_exchange_matches(sources)
    cutoff_matches = event_table.c.event_time_iso >= cutoff_iso

    conditions = and_(
        exchange_matches,
        cutoff_matches,
    )

    # An empty object filter means all the objects are reported on
    if objects:
        object_matches = event_table.c.object_name.in_(objects)
        conditions = and_(conditions, object_matches)

    statement = select(
        event_table.c.source,
        event_table.c.object_name,
        event_table.c.ext_client_id,
        event_table.c.event_time_iso,
    )
    statement = statement.where(conditions)

    # Ordered by the moment rather than by the id - a resubmit is recorded after the traffic
    # it reprocesses, so its id is higher while its exchange is older, and the first and last
    # call of a row are read off this order
    statement = statement.order_by(event_table.c.event_time_iso, event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        out = result.fetchall()

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_usage(
    now,        # type: datetime
    time_range, # type: str
    sources,    # type: strlist
    objects,    # type: strlist
) -> 'usage_row_list':
    """ Call counts per object and caller over the range - one row per object
    and security definition, with the first and last call times of each pair.
    """
    cutoff_iso = get_range_cutoff(now, time_range)

    sources = normalize_sources(sources)
    events = _load_usage_events(cutoff_iso, sources, objects)

    # Call counts and call times per object and caller - the source is part of
    # the key because one name can exist both as a channel and as a connection
    groups:'usage_state_dict' = {}

    for source, object_name, ext_client_id, event_time_iso in events:

        # An exchange with no identity on it is an outgoing connection's own call, which has
        # no caller at all, or a channel response that authenticated with no security definition
        if not ext_client_id:
            if source in _outgoing_sources:
                ext_client_id = Caller_Outgoing
            else:
                ext_client_id = Caller_Anonymous

        key = (object_name, source, ext_client_id)

        if group := groups.get(key):
            pass
        else:
            group = _UsageState()
            groups[key] = group

        # Events arrive oldest first, so the first one seen is the first call ..
        if not group.first_call:
            group.first_call = event_time_iso

        # .. and every later one moves the last call forward.
        group.calls += 1
        group.last_call = event_time_iso

    # Our response to produce
    out:'usage_row_list' = []

    for key in sorted(groups):

        object_name, source, caller = key
        group = groups[key]

        row = UsageRow()
        row.channel = object_name
        row.source = source
        row.caller = caller
        row.calls = group.calls
        row.first_call = group.first_call
        row.last_call = group.last_call
        row.link = _audit_log_link(source, object_name)

        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_object_options() -> 'object_options_dict':
    """ All the object names the audit log has completed exchanges for, grouped
    by source and sorted by name - this is what the filters on the usage page list.
    """
    conditions = _completed_exchange_matches([])

    statement = select(event_table.c.source, event_table.c.object_name).distinct()
    statement = statement.where(conditions)
    statement = statement.order_by(event_table.c.source, event_table.c.object_name)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    # Our response to produce
    out:'object_options_dict' = {}

    for row in rows:
        names = out.setdefault(row.source, [])
        names.append(row.object_name)

    return out

# ################################################################################################################################
# ################################################################################################################################

def usage_csv(rows:'usage_row_list') -> 'str':
    """ The usage table as CSV - the same rows the page renders.
    """
    buffer = StringIO()
    writer = csv.writer(buffer)

    _ = writer.writerow(Usage_Headers)

    for row in rows:
        row_values = [row.channel, row.source, row.caller, row.calls, row.first_call, row.last_call]
        _ = writer.writerow(row_values)

    out = buffer.getvalue()
    return out

# ################################################################################################################################
# ################################################################################################################################
