# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import OrderedDict
from logging import getLogger
from time import time

# Zato
from zato.common.soap.common import SOAPSecurityException

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# How long a value is remembered. A replay is only worth rejecting for as long as the message
# carrying it would still be accepted on its own merits, so this matches the timestamp and
# assertion time-to-live - remembering for longer would grow the cache without buying anything.
Default_TTL_Seconds = 300

# The most values remembered at once. An unauthenticated caller decides how many values arrive,
# so the cache has to have a ceiling or it becomes a way to exhaust the worker's memory. At this
# size the cache holds several minutes of traffic at a high request rate, and the effect of the
# ceiling being reached is that the oldest value is forgotten, which is the same outcome as its
# time-to-live expiring a moment later.
Default_Max_Size = 100_000

# ################################################################################################################################
# ################################################################################################################################

class ReplayCache:
    """ Remembers the one-shot values of messages already accepted - the wsse:Nonce of a
    UsernameToken and the ID of a SAML assertion - so a captured message cannot be replayed.

    The cache is per worker process, and deliberately so: a shared cache would mean a round trip
    to Redis on the authentication path of every signed message, and a lock to make the check and
    the insert atomic. The cost of that is paid on every request, while the benefit only applies
    to an attacker who replays into a different worker from the one that saw the original. With
    several workers behind the load balancer, a per-worker cache narrows the replay window from
    unlimited to one accepted replay per worker rather than closing it outright. The timestamp
    and expiry checks are what bound the window in absolute time - this cache is what stops the
    same message being accepted repeatedly inside that window.
    """

    def __init__(self, ttl_seconds:'int'=Default_TTL_Seconds, max_size:'int'=Default_Max_Size) -> 'None':
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size

        # Insertion-ordered, so eviction is a matter of dropping from the front - the oldest
        # entry is always the first one, which makes both forms of eviction O(1) per entry.
        self._seen:'OrderedDict[str, float]' = OrderedDict()

# ################################################################################################################################

    def _evict_expired(self, now:'float') -> 'None':
        """ Drops every entry whose time-to-live has passed.
        """
        while self._seen:

            # Reading the front key is O(1) and the entries are in insertion order, so the first
            # one still within its time-to-live means every entry behind it is too and the walk
            # can stop. This is what keeps the common case - nothing to evict - free.
            key = next(iter(self._seen))

            if now - self._seen[key] < self.ttl_seconds:
                break

            del self._seen[key]

# ################################################################################################################################

    def check_and_add(self, key:'str', what:'str') -> 'None':
        """ Records a value, raising when it has been seen before - the check and the insert
        are one operation so there is no window between them for a concurrent replay.
        """
        now = time()

        # Expired entries go first, otherwise a value whose time-to-live has passed would still
        # be reported as a replay and the size ceiling would be reached sooner than it should.
        self._evict_expired(now)

        if key in self._seen:
            raise SOAPSecurityException(f'{what} has already been used')

        self._seen[key] = now

        # Over the ceiling, the oldest entries go, which is the same thing their time-to-live
        # would have done shortly afterwards. Reaching the ceiling means traffic is arriving faster
        # than the time-to-live retires it, so it is worth saying once per batch of evictions.
        if len(self._seen) > self.max_size:
            logger.info('Replay cache is at its ceiling of %s entries, forgetting the oldest ones', self.max_size)

            while len(self._seen) > self.max_size:
                _ = self._seen.popitem(last=False)

# ################################################################################################################################

    def __len__(self) -> 'int':
        out = len(self._seen)
        return out

# ################################################################################################################################
# ################################################################################################################################

# The one cache the WS-Security enforcement path uses. It is a module-level instance because the
# values it remembers have to outlive any one request and any one security definition - the same
# nonce replayed against a different definition is still a replay.
replay_cache = ReplayCache()

# ################################################################################################################################
# ################################################################################################################################
