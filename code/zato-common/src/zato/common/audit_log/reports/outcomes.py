# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Delivered vs failed per partner and document type, with the failures broken down
# by their disposition modifier so the number is actionable.

from __future__ import annotations

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.audit_log.reports.common import _audit_log_link, _get_document_type, _load_events, _modifier_key, \
    _modifier_unspecified, _outcome_event_types, _OutcomeState, Default_Range, get_range_cutoff, OutcomeRow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.audit_log.reports.common import outcome_row_list, outcome_state_dict
    from zato.common.typing_ import anydict, strlist
    anydict = anydict
    datetime = datetime
    outcome_row_list = outcome_row_list
    outcome_state_dict = outcome_state_dict
    strlist = strlist

# ################################################################################################################################
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

def get_outcomes(now:'datetime', time_range:'str' = Default_Range, partner:'str' = '') -> 'outcome_row_list':
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
# ################################################################################################################################
