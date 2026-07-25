# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Traffic counts per period, partner and document type - the messages of AS2
# and the interchanges of X12, sent and received.

from __future__ import annotations

# Zato
from zato.common.audit_log.reports.common import _audit_log_link, _bucket_len_day, _bucket_len_hour, _direction_sent, \
    _get_document_type, _load_events, _volume_direction, _volume_event_types, _VolumeState, Default_Range, \
    get_range_cutoff, Range_Day, VolumeRow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.audit_log.reports.common import volume_row_list, volume_state_dict
    datetime = datetime
    volume_row_list = volume_row_list
    volume_state_dict = volume_state_dict

# ################################################################################################################################
# ################################################################################################################################

def get_volume(now:'datetime', time_range:'str' = Default_Range, partner:'str' = '') -> 'volume_row_list':
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
# ################################################################################################################################
