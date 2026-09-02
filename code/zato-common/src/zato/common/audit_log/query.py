# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Shared audit log queries - the conditions the Dashboard filters build on.
# The outstanding filter pairs the event that opens an exchange with the acknowledgment
# that closes it, so one query lists everything still waiting for its receipt -
# an AS2 message without its MDN or an X12 interchange without its 997/999.

# stdlib
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import and_, exists, select

# Zato
from zato.common.api import SCHEDULER
from zato.common.audit_log.api import event_table, AuditEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutstandingFilter:
    """ The outstanding filter of one source - the event that opens an exchange, the acknowledgment
    that closes it, and whether the close matches on the partner pair too. AS2 MDNs answer
    the Message-ID alone while X12 acknowledgments echo both the pair and the control number.
    A source whose events are single rows updated in place has no exchange to pair - what is
    open there is an event still carrying its in-progress outcome, which open_outcome names.
    """
    open_event: str = ''
    close_event: str = ''
    needs_object_name_match: bool = False
    open_outcome: str = ''

# ################################################################################################################################

def _new_outstanding_filter(open_event:'str', close_event:'str', needs_object_name_match:'bool') -> 'OutstandingFilter':
    out = OutstandingFilter()
    out.open_event = open_event
    out.close_event = close_event
    out.needs_object_name_match = needs_object_name_match

    return out

# ################################################################################################################################

def _new_outcome_filter(open_outcome:'str') -> 'OutstandingFilter':
    out = OutstandingFilter()
    out.open_outcome = open_outcome

    return out

# ################################################################################################################################

# The sources whose events can be outstanding at all - what opens and what closes
# each one's exchanges.
source_outstanding = {
    'as2': _new_outstanding_filter(AuditEvent.Message_Sent, AuditEvent.MDN_Received, False),
    'as4': _new_outstanding_filter(AuditEvent.Message_Sent, AuditEvent.Receipt_Received, True),
    'x12': _new_outstanding_filter(AuditEvent.Interchange_Sent, AuditEvent.Ack_Received, True),
    'mllp-outgoing': _new_outstanding_filter(AuditEvent.Message_Sent, AuditEvent.Ack_Received, True),

    # A scheduler run is one row updated in place - outstanding means it is still running
    'scheduler': _new_outcome_filter(SCHEDULER.OUTCOME.RUNNING),
}

# ################################################################################################################################
# ################################################################################################################################

def outstanding_conditions(
    source:'str',
    open_event:'str',
    close_event:'str',
    needs_object_name_match:'bool',
    ) -> 'anylist':
    """ Builds the WHERE conditions selecting the open events of one source whose closing event
    has not arrived. AS2 MDNs answer the Message-ID alone while X12 acknowledgments echo
    both the partner pair and the control number, which is what the object name match toggles.
    """

    # A closing event matches on the same source and message id ..
    closing = event_table.alias('closing')

    match_conditions = [
        closing.c.source == source,
        closing.c.event_type == close_event,
        closing.c.msg_id == event_table.c.msg_id,
    ]

    # .. and, for sources whose acknowledgments echo the partner pair, on the pair too.
    if needs_object_name_match:
        object_name_matches = closing.c.object_name == event_table.c.object_name
        match_conditions.append(object_name_matches)

    close_conditions = and_(*match_conditions)
    close_select = select(closing.c.id)
    close_select = close_select.where(close_conditions)
    close_exists = exists(close_select)

    out:'anylist' = [
        event_table.c.event_type == open_event,
        ~close_exists,
    ]

    return out

# ################################################################################################################################
# ################################################################################################################################
