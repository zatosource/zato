# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What every B2B report is built out of - the ranges they run over, the rows they return,
# the aggregation state they accumulate into and the reading of the events they aggregate.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import quote

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table, get_audit_engine, \
    Retention_Days
from zato.common.defaults import default_cluster_id
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, anytuple, dictlist, strlist, strtuple
    anydict = anydict
    anylist = anylist
    anytuple = anytuple
    dictlist = dictlist
    strlist = strlist
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
float_list       = list[float]
volume_row_list  = list['VolumeRow']
outcome_row_list = list['OutcomeRow']
ack_row_list     = list['AckDisciplineRow']

volume_state_dict  = dict['anytuple', '_VolumeState']
outcome_state_dict = dict['anytuple', '_OutcomeState']
ack_state_dict     = dict[str, '_AckState']

# ################################################################################################################################
# ################################################################################################################################

# The selectable report ranges
Range_Day   = 'day'
Range_Week  = 'week'
Range_Month = 'month'

# How far back each range reaches - the widest one is the audit log's own retention window,
# so the report never claims to cover more than the log actually holds.
Range_Hours = {
    Range_Day:   24,
    Range_Week:  7 * 24,
    Range_Month: Retention_Days * 24,
}

# The range a page opens with when none was chosen
Default_Range = Range_Week

# ################################################################################################################################

# The event time is an ISO timestamp, so a string prefix is a period bucket -
# 13 characters give one bucket per hour and 10 give one per day.
_bucket_len_hour = 13
_bucket_len_day  = 10

# ################################################################################################################################

# Which volume column each traffic event lands in
_direction_sent     = 'sent'
_direction_received = 'received'

_volume_direction = {
    AuditEvent.Message_Sent:         _direction_sent,
    AuditEvent.Message_Received:     _direction_received,
    AuditEvent.Interchange_Sent:     _direction_sent,
    AuditEvent.Interchange_Received: _direction_received,
}

_volume_event_types = tuple(_volume_direction)

# ################################################################################################################################

# Which JSON key carries the failure modifier of each outcome-bearing event - the MDNs
# of outbound AS2 exchanges report a disposition modifier, an inbound message that
# could not be processed reports its error, and an X12 acknowledgment that rejected
# what it answered may name its modifier too.
_modifier_key = {
    AuditEvent.MDN_Received:     'modifier',
    AuditEvent.Message_Received: 'error',
    AuditEvent.Ack_Received:     'modifier',
}

_outcome_event_types = tuple(_modifier_key)

# What a failure without a disposition modifier is reported as
_modifier_unspecified = 'unspecified'

# ################################################################################################################################

# The CSV headers of each table, matching the columns the page renders
Volume_Headers  = ('period', 'source', 'partner', 'document_type', 'sent', 'received')
Outcome_Headers = ('source', 'partner', 'document_type', 'delivered', 'failed', 'failure_breakdown')
Ack_Headers     = ('partner', 'acknowledged', 'average_seconds', 'max_seconds', 'outstanding', 'rejected')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class VolumeRow:
    """ Traffic of one period, source, partner and document type.
    """
    period:        str = ''
    source:        str = ''
    partner:       str = ''
    document_type: str = ''
    sent:          int = 0
    received:      int = 0

    # The filtered audit log page behind this row
    link: str = ''

# ################################################################################################################################

@dataclass(init=False)
class OutcomeRow:
    """ Delivered vs failed of one source, partner and document type, with the failures
    broken down by their disposition modifier so the number is actionable.
    """
    source:        str = ''
    partner:       str = ''
    document_type: str = ''
    delivered:     int = 0
    failed:        int = 0

    # The per-modifier failure counts, e.g. 'decryption-failed: 2, integrity-check-failed: 1'
    failure_breakdown: str = ''

    # The filtered audit log page behind this row
    link: str = ''

# ################################################################################################################################

@dataclass(init=False)
class AckDisciplineRow:
    """ Acknowledgment discipline of one partner - how fast its 997/999 answers arrive,
    how many are still outstanding and how many rejected what they answered.
    """
    partner:         str   = ''
    acknowledged:    int   = 0
    average_seconds: float = 0.0
    max_seconds:     float = 0.0
    outstanding:     int   = 0
    rejected:        int   = 0

    # The filtered audit log page behind this row, plus its outstanding-only view
    link:             str = ''
    outstanding_link: str = ''

# ################################################################################################################################
# ################################################################################################################################

class _VolumeState:
    """ The aggregation state of one volume row in the making.
    """

    def __init__(self) -> 'None':
        self.sent:'int' = 0
        self.received:'int' = 0

# ################################################################################################################################

class _OutcomeState:
    """ The aggregation state of one outcomes row in the making.
    """

    def __init__(self) -> 'None':
        self.delivered:'int' = 0
        self.failed:'int' = 0

        # How many times each failure modifier occurred
        self.modifiers:'anydict' = {}

# ################################################################################################################################

class _AckState:
    """ The aggregation state of one acknowledgment discipline row in the making.
    """

    def __init__(self) -> 'None':

        # The turnaround of each acknowledged interchange, in seconds
        self.deltas:'float_list' = []

        self.outstanding:'int' = 0
        self.rejected:'int' = 0

# ################################################################################################################################
# ################################################################################################################################

def _audit_log_link(source:'str', partner:'str', status:'str' = '') -> 'str':
    """ Builds the drill-down path from one aggregate row to the filtered audit log page.
    """
    # The pair is built out of partner-defined identifiers that can hold characters
    # that would split the query string
    partner = quote(partner)

    out = f'/zato/audit-log/?source={source}&object_name={partner}&cluster={default_cluster_id}'

    if status:
        out = f'{out}&status={status}'

    return out

# ################################################################################################################################

def _parse_details(data:'str') -> 'anydict':
    """ Parses the JSON data of one event - events recorded without data
    have no details to speak of.
    """
    if not data:
        return {}

    # A payload that is not JSON, e.g. a raw MIME body, has nothing to extract.
    try:
        out = loads(data)
    except ValueError:
        return {}

    return out

# ################################################################################################################################

def _get_document_type(details:'anydict') -> 'str':
    """ Returns the document type an event carries - only X12 interchange events have one.
    """
    if document_type := details.get('document_type'):
        out = document_type
    else:
        out = ''

    return out

# ################################################################################################################################

def get_range_cutoff(now:'datetime', time_range:'str') -> 'str':
    """ Returns the ISO timestamp the given range reaches back to.
    """
    range_hours = Range_Hours[time_range]
    cutoff = now - timedelta(hours=range_hours)

    out = cutoff.isoformat()
    return out

# ################################################################################################################################

def _load_events(event_types:'strtuple', cutoff_iso:'str', partner:'str') -> 'dictlist':
    """ Reads all the B2B events of the given types recorded after the cutoff, oldest first,
    with their JSON data parsed - what the aggregates below run on.
    """
    source_matches = event_table.c.source.in_((AuditSource.AS2, AuditSource.X12))
    event_type_matches = event_table.c.event_type.in_(event_types)

    conditions = and_(
        source_matches,
        event_type_matches,
        event_table.c.event_time_iso >= cutoff_iso,
    )

    statement = select(
        event_table.c.source,
        event_table.c.event_type,
        event_table.c.object_name,
        event_table.c.msg_id,
        event_table.c.event_time_iso,
        event_table.c.outcome,
        event_table.c.data,
    )
    statement = statement.where(conditions)
    statement = statement.order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        db_rows = result.fetchall()

    # Our response to produce
    out:'dictlist' = []

    for source, event_type, object_name, msg_id, event_time_iso, outcome, data in db_rows:

        # The partner filter matches anywhere inside the identity pair,
        # so either side of an exchange finds it.
        if partner:
            if partner not in object_name:
                continue

        details = _parse_details(data)

        item = {
            'source': source,
            'event_type': event_type,
            'partner': object_name,
            'msg_id': msg_id,
            'event_time_iso': event_time_iso,
            'outcome': outcome,
            'details': details,
        }

        out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################
