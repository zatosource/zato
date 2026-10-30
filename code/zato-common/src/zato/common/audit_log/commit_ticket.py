# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import Event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.buffer import PendingEvent
    from zato.common.typing_ import intnone

    # Dummy assignments to satisfy type checkers
    intnone = intnone
    PendingEvent = PendingEvent

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
commit_ticket_list = list['CommitTicket']

# ################################################################################################################################
# ################################################################################################################################

class CommitTicket:
    """ One event waiting for a group commit, with what its caller receives once the commit completes.
    """

    def __init__(self, pending:'PendingEvent') -> 'None':

        # The event to write
        self.pending = pending

        # The id the database gave the event, or the exception of the commit it was part of
        self.event_id:'intnone' = None
        self.exception:'BaseException | None' = None

        # The tickets this one commits, set when its caller becomes the one that runs a commit
        self.batch:'commit_ticket_list | None' = None

        # Whether the caller has begun the commit of its batch
        self.has_started = False

        # Set when the commit of the ticket completes or when its caller is to run the next commit
        self.ready = Event()

# ################################################################################################################################
# ################################################################################################################################
