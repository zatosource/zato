# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import Lock
from time import monotonic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strfloatdict

# ################################################################################################################################
# ################################################################################################################################

_MSH10_Index = 9

# How many control ids one cache holds before the oldest are dropped to make room. A sender that
# never repeats a control id would otherwise grow the cache for as long as the TTL window lasts.
Default_Max_Entries = 100_000

# ################################################################################################################################
# ################################################################################################################################

def extract_control_id(msh_line:'str') -> 'str':
    """ Extracts the message control ID (MSH-10) from a pipe-delimited MSH line.
    Returns an empty string if the MSH line does not have enough fields.
    """

    fields = msh_line.split('|')

    if len(fields) > _MSH10_Index:
        out = fields[_MSH10_Index]
    else:
        out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################

class MessageDeduplicator:
    """ Thread-safe in-memory cache that tracks recently seen HL7 message control IDs
    (MSH-10) and suppresses duplicates within a configurable time window.
    """

    def __init__(self, ttl_seconds:'float', max_entries:'int'=Default_Max_Entries) -> 'None':
        """ Creates a dedup cache that remembers up to `max_entries` control IDs for `ttl_seconds`.
        """
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries

        # A dict preserves insertion order, and an entry's timestamp is only ever set when it is
        # first inserted, so the cache is ordered oldest first and eviction can stop at the first
        # entry still inside the window rather than walking everything received so far.
        self._seen:'strfloatdict' = {}
        self._lock = Lock()

    def is_duplicate(self, control_id:'str') -> 'bool':
        """ Returns True if `control_id` was already seen within the TTL window.
        If not seen, records it and returns False.
        """
        now = monotonic()

        with self._lock:

            # .. an entry past the window is one this message may reuse the id of ..
            self._evict_expired(now)

            if control_id in self._seen:
                return True

            # .. and a cache at its cap makes room by dropping what it has held longest ..
            self._evict_overflow()

            self._seen[control_id] = now
            return False

    def _evict_expired(self, now:'float') -> 'None':
        """ Removes the entries at the front of the cache that are older than the TTL window.
        Called under lock by `is_duplicate`.
        """
        cutoff = now - self.ttl_seconds

        # The cost is the number of entries actually dropped rather than the number held
        while self._seen:

            oldest_key = next(iter(self._seen))

            # The front entry being inside the window means every entry behind it is too
            if self._seen[oldest_key] >= cutoff:
                break

            del self._seen[oldest_key]

    def _evict_overflow(self) -> 'None':
        """ Drops the oldest entries until the cache has room for one more.
        Called under lock by `is_duplicate`.
        """
        while len(self._seen) >= self.max_entries:
            oldest_key = next(iter(self._seen))
            del self._seen[oldest_key]

    def clear(self) -> 'None':
        """ Removes all entries from the cache.
        """
        with self._lock:
            self._seen.clear()

# ################################################################################################################################
# ################################################################################################################################
