# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Channel usage reporting - a per-channel aggregate built over the audit events REST
# and SOAP channels already record. Each row counts the responses one caller received
# from one channel over the range, where the caller is the security definition that
# authenticated the requests. The table answers "who still calls this channel",
# which is what retiring a deprecated API needs, and it renders as CSV too.

from __future__ import annotations

# stdlib
import csv
from dataclasses import dataclass
from io import StringIO

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table, get_audit_engine
from zato.common.audit_log.reports import get_range_cutoff, Default_Range
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import anylist, anytuple, strlist, strstrdict

    # Dummy assignments to satisfy type checkers
    datetime = datetime
    anylist = anylist
    anytuple = anytuple
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
usage_row_list   = list['UsageRow']
usage_state_dict = dict['anytuple', '_UsageState']

# ################################################################################################################################
# ################################################################################################################################

# What a caller that authenticated with no security definition is reported as
Caller_Anonymous = 'Anonymous'

# The CSV headers of the usage table, matching the columns the page renders
Usage_Headers = ('channel', 'caller', 'calls', 'first_call', 'last_call')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class UsageRow:
    """ The calls one caller made to one channel over the range.
    """
    channel:    str = ''
    caller:     str = ''
    calls:      int = 0
    first_call: str = ''
    last_call:  str = ''

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
    out = f'/zato/audit-log/?source={source}&object_name={channel}&cluster={default_cluster_id}'
    return out

# ################################################################################################################################

def _load_usage_events(cutoff_iso:'str', channel:'str') -> 'anylist':
    """ Reads all the channel responses recorded after the cutoff, oldest first -
    responses are audited after authentication, so each one knows its caller.
    """
    source_matches = event_table.c.source.in_((AuditSource.REST_Channel, AuditSource.SOAP_Channel))
    event_type_matches = event_table.c.event_type == AuditEvent.Response_Sent
    cutoff_matches = event_table.c.event_time_iso >= cutoff_iso

    conditions = and_(
        source_matches,
        event_type_matches,
        cutoff_matches,
    )

    # An empty channel filter means all the channels are reported on
    if channel:
        channel_matches = event_table.c.object_name == channel
        conditions = and_(conditions, channel_matches)

    statement = select(
        event_table.c.source,
        event_table.c.object_name,
        event_table.c.ext_client_id,
        event_table.c.event_time_iso,
    )
    statement = statement.where(conditions)
    statement = statement.order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        out = result.fetchall()

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_usage(now:'datetime', time_range:'str'=Default_Range, channel:'str'='') -> 'usage_row_list':
    """ Call counts per channel and caller over the range - one row per channel
    and security definition, with the first and last call times of each pair.
    """
    cutoff_iso = get_range_cutoff(now, time_range)

    events = _load_usage_events(cutoff_iso, channel)

    # Call counts and call times per channel and caller
    groups:'usage_state_dict' = {}

    # Each channel's audit source, so the drill-down link filters the audit log correctly
    channel_sources:'strstrdict' = {}

    for source, object_name, ext_client_id, event_time_iso in events:

        # A response recorded without a security definition came from an anonymous caller
        if not ext_client_id:
            ext_client_id = Caller_Anonymous

        channel_sources[object_name] = source

        key = (object_name, ext_client_id)

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

        channel_name, caller = key
        group = groups[key]
        source = channel_sources[channel_name]

        row = UsageRow()
        row.channel = channel_name
        row.caller = caller
        row.calls = group.calls
        row.first_call = group.first_call
        row.last_call = group.last_call
        row.link = _audit_log_link(source, channel_name)

        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_channel_list() -> 'strlist':
    """ All the channel names the audit log has responses for, sorted by name -
    this is what the channel filter on the usage page lists.
    """
    source_matches = event_table.c.source.in_((AuditSource.REST_Channel, AuditSource.SOAP_Channel))
    event_type_matches = event_table.c.event_type == AuditEvent.Response_Sent

    conditions = and_(
        source_matches,
        event_type_matches,
    )

    statement = select(event_table.c.object_name).distinct()
    statement = statement.where(conditions)
    statement = statement.order_by(event_table.c.object_name)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    # Our response to produce
    out:'strlist' = []

    for row in rows:
        out.append(row.object_name)

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
        row_values = [row.channel, row.caller, row.calls, row.first_call, row.last_call]
        _ = writer.writerow(row_values)

    out = buffer.getvalue()
    return out

# ################################################################################################################################
# ################################################################################################################################
