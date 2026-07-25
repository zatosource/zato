# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Per-partner acknowledgment discipline - how fast the 997 and 999 answers arrive,
# how many interchanges are still waiting and how many answers rejected what they answered.

from __future__ import annotations

# stdlib
from datetime import datetime

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.reports.common import _AckState, _audit_log_link, _load_events, AckDisciplineRow, \
    Default_Range, get_range_cutoff

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.reports.common import ack_row_list, ack_state_dict
    from zato.common.typing_ import anydict
    ack_row_list = ack_row_list
    ack_state_dict = ack_state_dict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

def get_ack_discipline(now:'datetime', time_range:'str' = Default_Range, partner:'str' = '') -> 'ack_row_list':
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
