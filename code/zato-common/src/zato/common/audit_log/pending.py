# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
pending_event_list = list['PendingEvent']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingEvent:
    """ One audit event that is not written yet, with everything that is written alongside it.
    """

    # The values of the event row itself
    values: 'stranydict'

    # Searchable attributes, name to value
    attrs: 'stranydict'

    # Message bodies, kind to content
    bodies: 'stranydict'

    # Attachment envelopes, one body row each
    attachments: 'anylist'

    # Lineage - the ids of parent events and how this event relates to them
    parents: 'anylist'
    parent_link_type: 'str' = ''

    # Whether the event's payload leaves the process with the export
    is_export_payload_active: 'bool' = False

    # The id the database gave the event once it was written
    event_id: 'int' = 0

# ################################################################################################################################
# ################################################################################################################################
