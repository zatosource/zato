# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# B2B reporting - aggregate tables built over the audit events the AS2 and X12 exchanges
# already record. Volume counts traffic per period, partner and document type, outcomes
# split delivered from failed with failures broken down by disposition modifier, and
# acknowledgment discipline measures per-partner turnaround from interchange-sent
# to ack-received. Each aggregate row links back to the filtered audit log page
# and each table renders as CSV too.

from __future__ import annotations

# stdlib
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import StringIO

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource, event_table, get_audit_engine, Retention_Days
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

def _audit_log_link(source:'str', partner:'str', status:'str'='') -> 'str':
    """ Builds the drill-down path from one aggregate row to the filtered audit log page.
    """
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

def get_volume(now:'datetime', time_range:'str'=Default_Range, partner:'str'='') -> 'volume_row_list':
    """ Traffic counts per period, partner and document type over the range -
    the messages of AS2 and the interchanges of X12, sent and received.
    """
    cutoff_iso = get_range_cutoff(now, time_range)

    # The day range buckets by hour, the wider ones by day.
    if time_range == Range_Day:
        bucket_len = _bucket_len_hour
    else:
        bucket_len = _bucket_len_day

    events = _load_events(_volume_event_types, cutoff_iso, partner)

    # Sent and received counts per period, source, partner and document type
    counts:'volume_state_dict' = {}

    for event in events:

        event_time_iso = event['event_time_iso']
        period = event_time_iso[:bucket_len]

        details = event['details']
        document_type = _get_document_type(details)

        key = (period, event['source'], event['partner'], document_type)

        if group := counts.get(key):
            pass
        else:
            group = _VolumeState()
            counts[key] = group

        event_type = event['event_type']
        direction = _volume_direction[event_type]

        if direction == _direction_sent:
            group.sent += 1
        else:
            group.received += 1

    # Our response to produce
    out:'volume_row_list' = []

    for key in sorted(counts):

        period, source, pair, document_type = key
        group = counts[key]

        row = VolumeRow()
        row.period = period
        row.source = source
        row.partner = pair
        row.document_type = document_type
        row.sent = group.sent
        row.received = group.received
        row.link = _audit_log_link(source, pair)

        out.append(row)

    return out

# ################################################################################################################################

def _format_breakdown(modifiers:'anydict') -> 'str':
    """ Turns the per-modifier failure counts of one row into their display string.
    """
    parts:'strlist' = []

    for name in sorted(modifiers):
        count = modifiers[name]
        parts.append(f'{name}: {count}')

    out = ', '.join(parts)
    return out

# ################################################################################################################################

def get_outcomes(now:'datetime', time_range:'str'=Default_Range, partner:'str'='') -> 'outcome_row_list':
    """ Delivered vs failed per partner and document type over the range - the MDNs received
    for outbound AS2 exchanges, the messages that arrived from partners and the X12
    acknowledgments, with failures broken down by their disposition modifier.
    """
    cutoff_iso = get_range_cutoff(now, time_range)

    events = _load_events(_outcome_event_types, cutoff_iso, partner)

    # An X12 acknowledgment does not name the document type itself - the interchange
    # it answers does, so the sent interchanges provide the lookup.
    sent_types = (AuditEvent.Interchange_Sent,)
    sent_events = _load_events(sent_types, cutoff_iso, partner)

    document_types:'anydict' = {}

    for event in sent_events:
        lookup_key = (event['partner'], event['msg_id'])
        details = event['details']
        document_type = _get_document_type(details)
        document_types[lookup_key] = document_type

    # Delivered and failed counts per source, partner and document type,
    # with a per-modifier breakdown of the failures.
    groups:'outcome_state_dict' = {}

    for event in events:

        event_type = event['event_type']
        details = event['details']

        # An acknowledgment inherits the document type of the interchange it answers.
        if event_type == AuditEvent.Ack_Received:
            lookup_key = (event['partner'], event['msg_id'])

            if found := document_types.get(lookup_key):
                document_type = found
            else:
                document_type = ''
        else:
            document_type = _get_document_type(details)

        key = (event['source'], event['partner'], document_type)

        if group := groups.get(key):
            pass
        else:
            group = _OutcomeState()
            groups[key] = group

        # Anything that did not fail was delivered ..
        if event['outcome'] != AuditOutcome.Error:
            group.delivered += 1
            continue

        # .. and a failure additionally counts against its disposition modifier.
        group.failed += 1

        modifier_key = _modifier_key[event_type]

        if modifier := details.get(modifier_key):
            pass
        else:
            modifier = _modifier_unspecified

        if modifier in group.modifiers:
            group.modifiers[modifier] += 1
        else:
            group.modifiers[modifier] = 1

    # Our response to produce
    out:'outcome_row_list' = []

    for key in sorted(groups):

        source, pair, document_type = key
        group = groups[key]

        row = OutcomeRow()
        row.source = source
        row.partner = pair
        row.document_type = document_type
        row.delivered = group.delivered
        row.failed = group.failed
        row.failure_breakdown = _format_breakdown(group.modifiers)
        row.link = _audit_log_link(source, pair)

        out.append(row)

    return out

# ################################################################################################################################

def get_ack_discipline(now:'datetime', time_range:'str'=Default_Range, partner:'str'='') -> 'ack_row_list':
    """ Per-partner acknowledgment discipline over the range - the average and maximum time
    from interchange-sent to ack-received, the interchanges still waiting for their
    acknowledgment and the acknowledgments that rejected what they answered.
    """
    cutoff_iso = get_range_cutoff(now, time_range)

    sent_types = (AuditEvent.Interchange_Sent,)
    ack_types = (AuditEvent.Ack_Received,)

    sent_events = _load_events(sent_types, cutoff_iso, partner)
    ack_events = _load_events(ack_types, cutoff_iso, partner)

    # The first acknowledgment of each pair and control number is the one that counts.
    first_acks:'anydict' = {}

    for ack in ack_events:
        lookup_key = (ack['partner'], ack['msg_id'])

        if lookup_key not in first_acks:
            first_acks[lookup_key] = ack

    # Per-partner aggregation state
    groups:'ack_state_dict' = {}

    for event in sent_events:

        pair = event['partner']

        if group := groups.get(pair):
            pass
        else:
            group = _AckState()
            groups[pair] = group

        lookup_key = (pair, event['msg_id'])

        # An acknowledged interchange contributes its turnaround ..
        if ack := first_acks.get(lookup_key):
            sent_time_iso = event['event_time_iso']
            ack_time_iso = ack['event_time_iso']

            sent_time = datetime.fromisoformat(sent_time_iso)
            ack_time = datetime.fromisoformat(ack_time_iso)

            delta = ack_time - sent_time
            delta_seconds = delta.total_seconds()
            group.deltas.append(delta_seconds)

        # .. and one still waiting is an open item.
        else:
            group.outstanding += 1

    # Rejections count per partner on the acknowledgments themselves,
    # so a rejected 997 or 999 shows even if its interchange left before the range began.
    for ack in first_acks.values():

        if ack['outcome'] != AuditOutcome.Error:
            continue

        pair = ack['partner']

        if group := groups.get(pair):
            pass
        else:
            group = _AckState()
            groups[pair] = group

        group.rejected += 1

    # Our response to produce
    out:'ack_row_list' = []

    for pair in sorted(groups):

        group = groups[pair]
        deltas = group.deltas

        row = AckDisciplineRow()
        row.partner = pair
        row.acknowledged = len(deltas)

        if deltas:
            total = sum(deltas)
            count = len(deltas)
            average = total / count
            max_delta = max(deltas)
            row.average_seconds = round(average, 1)
            row.max_seconds = round(max_delta, 1)

        row.outstanding = group.outstanding
        row.rejected = group.rejected
        row.link = _audit_log_link(AuditSource.X12, pair)
        row.outstanding_link = _audit_log_link(AuditSource.X12, pair, status='outstanding')

        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _rows_to_csv(headers:'strtuple', values:'anylist') -> 'str':
    """ Renders one table as CSV, headers first.
    """
    buffer = StringIO()
    writer = csv.writer(buffer)

    _ = writer.writerow(headers)

    for row_values in values:
        _ = writer.writerow(row_values)

    out = buffer.getvalue()
    return out

# ################################################################################################################################

def volume_csv(rows:'volume_row_list') -> 'str':
    """ The volume table as CSV - the same rows the page renders.
    """
    values:'anylist' = []

    for row in rows:
        row_values = [row.period, row.source, row.partner, row.document_type, row.sent, row.received]
        values.append(row_values)

    out = _rows_to_csv(Volume_Headers, values)
    return out

# ################################################################################################################################

def outcomes_csv(rows:'outcome_row_list') -> 'str':
    """ The outcomes table as CSV - the same rows the page renders.
    """
    values:'anylist' = []

    for row in rows:
        row_values = [row.source, row.partner, row.document_type, row.delivered, row.failed, row.failure_breakdown]
        values.append(row_values)

    out = _rows_to_csv(Outcome_Headers, values)
    return out

# ################################################################################################################################

def ack_discipline_csv(rows:'ack_row_list') -> 'str':
    """ The acknowledgment discipline table as CSV - the same rows the page renders.
    """
    values:'anylist' = []

    for row in rows:
        row_values = [row.partner, row.acknowledged, row.average_seconds, row.max_seconds, row.outstanding, row.rejected]
        values.append(row_values)

    out = _rows_to_csv(Ack_Headers, values)
    return out

# ################################################################################################################################
# ################################################################################################################################
