# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.sql.admin import SQLAdminAPI
from zato.common.pubsub.sql.config import get_pull_lease_seconds
from zato.common.pubsub.sql.fast_path import State_Delivered
from zato.common.pubsub.sql.pending import new_pending_lease
from zato.common.pubsub.sql.pull import has_lease_candidates

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

_default_max_messages = PubSub.Message.Default_Max_Messages
_default_max_len      = PubSub.Message.Default_Max_Len

# One second expressed in milliseconds.
_milliseconds_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

class SQLPullAPI(SQLAdminAPI):
    """ The pulls of the SQL pub/sub backend, each of which leases the messages it hands out to its client
    or is handed them by a publication while it waits.
    """

    def pull_messages(
        self,
        sub_key:'str',
        max_messages:'int'=_default_max_messages,
        max_len:'int'=_default_max_len,
        wait_ms:'int'=0,
    ) -> 'anylist':
        """ Hands a subscriber's deliverable messages over to one pulling client, leasing them in the same transaction,
        so that concurrent pulls never receive the same message. The messages stay in the queue until the subscriber
        acknowledges them, and a pull after their lease runs out hands them out again. A pull that finds nothing
        waits for up to wait_ms milliseconds for a publication, which hands its messages over to the pull directly.
        """
        fast_path = self.fast_path
        deadline = monotonic() + wait_ms / _milliseconds_per_second

        while True:

            # A publication that commits from this point on is noticed by the version of the subscriber ..
            version = fast_path.get_version(sub_key)

            # .. the queue is read and leased as it stands ..
            out = self._lease_now(sub_key, max_messages, max_len)

            if out:
                return out

            # .. a pull that does not wait, or whose wait is over, returns what it found ..
            remaining = deadline - monotonic()

            if remaining <= 0:
                return out

            # .. one that a publication was announced to after its read reads the queue again ..
            if fast_path.get_version(sub_key) != version:
                continue

            # .. and any other one waits, either to be handed the messages of a publication or to be woken up
            # .. by one that it reads the queue again for.
            waiter = fast_path.add_pull_waiter(sub_key, max_messages, max_len)

            try:
                fast_path.wait_pull(waiter, remaining)
            finally:
                fast_path.remove_pull_waiter(waiter)

            if waiter.state == State_Delivered:
                out = waiter.messages
                return out

            if not waiter.is_notified:
                return out

# ################################################################################################################################

    def _lease_now(self, sub_key:'str', max_messages:'int', max_len:'int') -> 'anylist':
        """ Leases the deliverable messages of a subscriber as the queue stands now, returning no messages
        without a commit if there are none.
        """
        now_ms = self._database_now_ms()
        out:'anylist' = []

        # A pull that would hand out nothing does not wait for a commit ..
        if not has_lease_candidates(self.engine, self.subscription_list, sub_key, now_ms):
            return out

        # .. while any other one leases its messages in a commit that it may share with other writes.
        leased_until_ms = now_ms + get_pull_lease_seconds() * _milliseconds_per_second

        lease = new_pending_lease(sub_key, max_messages, max_len, now_ms, leased_until_ms, self._on_leased)
        self._writer.lease(lease)

        out = lease.messages
        return out

# ################################################################################################################################
# ################################################################################################################################
