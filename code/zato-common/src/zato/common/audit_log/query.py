# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Shared audit log queries - the conditions the Dashboard filters build on.
# The outstanding filter pairs the event that opens an exchange with the acknowledgment
# that closes it, so one query lists everything still waiting for its receipt -
# an HL7 message without its ACK.

# stdlib
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import SCHEDULER
from zato.common.audit_log.common import event_open_table, event_table, exchange_pairs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutstandingFilter:
    """ The outstanding filter of one source - the event that opens an exchange, the acknowledgment
    that closes it, and whether the close matches on the object name too, not only on the message id.
    A source whose events are single rows updated
    in place has no exchange to pair - what is open there is an event still carrying its
    in-progress outcome, which open_outcome names.
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
# each one's exchanges ..
source_outstanding:'anydict' = {}

for _pair in exchange_pairs:
    source_outstanding[_pair.source] = _new_outstanding_filter(_pair.open_event, _pair.close_event, _pair.needs_object_name_match)

# .. and a scheduler run, which is one row updated in place - outstanding means it is still running.
source_outstanding['scheduler'] = _new_outcome_filter(SCHEDULER.OUTCOME.RUNNING)

# ################################################################################################################################
# ################################################################################################################################

def outstanding_conditions(source:'str') -> 'anylist':
    """ Builds the WHERE conditions selecting the open events of one source whose closing event
    has not arrived, which the table of open exchanges holds.
    """
    open_event_ids = select(event_open_table.c.event_id)
    open_event_ids = open_event_ids.where(event_open_table.c.source == source)

    is_open = event_table.c.id.in_(open_event_ids)

    out:'anylist' = [is_open]

    return out

# ################################################################################################################################
# ################################################################################################################################
