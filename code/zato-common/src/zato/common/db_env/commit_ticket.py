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
    from zato.common.typing_ import any_

    # Dummy assignments to satisfy type checkers
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
commit_ticket_list = list['CommitTicket']

# ################################################################################################################################
# ################################################################################################################################

class CommitTicket:
    """ One item waiting for a group commit, with the exception of the commit it was part of, if the commit failed.
    """

    def __init__(self, item:'any_', weight:'int', is_urgent:'bool') -> 'None':

        # The item to write
        self.item = item

        # How much of a commit's capacity the item takes
        self.weight = weight

        # Whether the item goes into the next commit ahead of the items that are not urgent
        self.is_urgent = is_urgent

        # The exception of the commit the item was part of
        self.exception:'BaseException | None' = None

        # The tickets this one commits, set when its caller becomes the one that runs a commit
        self.batch:'commit_ticket_list | None' = None

        # Whether the caller has begun the commit of its batch
        self.has_started = False

        # Whether the batch of the ticket is committed in the lane reserved for urgent items
        self.is_urgent_lane = False

        # Set when the commit of the ticket completes or when its caller is to run the next commit
        self.ready = Event()

# ################################################################################################################################
# ################################################################################################################################
