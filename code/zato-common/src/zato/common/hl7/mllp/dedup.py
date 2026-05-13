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

    def __init__(self, ttl_seconds:'float') -> 'None':
        """ Creates a dedup cache that remembers control IDs for `ttl_seconds`.
        """
        self.ttl_seconds = ttl_seconds
        self._seen:'strfloatdict' = {}
        self._lock = Lock()

    def is_duplicate(self, control_id:'str') -> 'bool':
        """ Returns True if `control_id` was already seen within the TTL window.
        If not seen, records it and returns False.
        """
        now = monotonic()

        with self._lock:

            # .. remove expired entries before the lookup ..
            self._evict_expired(now)

            if control_id in self._seen:
                return True

            self._seen[control_id] = now
            return False

    def _evict_expired(self, now:'float') -> 'None':
        """ Removes all entries from the cache whose timestamp is older than the TTL window.
        Called under lock by `is_duplicate`.
        """
        cutoff = now - self.ttl_seconds
        expired_keys = [key for key, timestamp in self._seen.items() if timestamp < cutoff]

        for key in expired_keys:
            del self._seen[key]

    def clear(self) -> 'None':
        """ Removes all entries from the cache.
        """
        with self._lock:
            self._seen.clear()

# ################################################################################################################################
# ################################################################################################################################
