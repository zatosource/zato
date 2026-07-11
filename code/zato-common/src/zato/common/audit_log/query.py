# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Shared audit log queries - the conditions the Dashboard filters build on.
# The outstanding filter pairs the event that opens an exchange with the acknowledgment
# that closes it, so one query lists everything still waiting for its receipt -
# an AS2 message without its MDN or an X12 interchange without its 997/999.

# SQLAlchemy
from sqlalchemy import and_, exists, select

# Zato
from zato.common.audit_log.api import event_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist
    anylist = anylist

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
