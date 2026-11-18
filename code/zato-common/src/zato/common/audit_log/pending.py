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
    from zato.common.typing_ import anylist, stranydict, strnone

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    stranydict = stranydict
    strnone = strnone

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

    # The values of the event row itself, with its payload under data, which is stored in the payload table
    # under the digest the event row references
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

    # Whether the digest and the search text of the payload were computed before the write
    is_payload_prepared: 'bool' = False

    # The digest the payload is stored under, None for an empty payload
    payload_digest: 'strnone' = None

    # The words of the payload that the search index holds
    search_text: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################
