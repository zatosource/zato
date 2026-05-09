
# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redis import Redis
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Key_Prefix = 'zato:cache:'

# ################################################################################################################################
# ################################################################################################################################

class CacheAPI:
    """ Redis-backed cache with get, set, delete, and exists operations.
    """
    def __init__(self, redis_client:'Redis') -> 'None':
        self.redis = redis_client

# ################################################################################################################################

    def _make_key(self, key:'str') -> 'str':
        out = _Key_Prefix + key
        return out

# ################################################################################################################################

    def get(self, key:'str') -> 'any_':
        """ Returns the value stored under the key, or None if the key does not exist or has expired.
        """
        redis_key = self._make_key(key)
        raw = self.redis.get(redis_key)

        if raw is None:
            return None

        out = loads(raw)
        return out

# ################################################################################################################################

    def exists(self, key:'str') -> 'bool':
        """ Returns True if the key exists and has not expired, False otherwise.
        """
        redis_key = self._make_key(key)
        count = self.redis.exists(redis_key)
        out = bool(count)
        return out

# ################################################################################################################################

    def set(self, key:'str', value:'any_', expiry:'int'=0) -> 'None':
        """ Stores a value under the given key. Expiry is in seconds, 0 means no expiry.
        """
        redis_key = self._make_key(key)
        serialized = dumps(value)

        if expiry:
            expiry_int = int(expiry)
            self.redis.set(redis_key, serialized, ex=expiry_int)

        else:
            self.redis.set(redis_key, serialized)

# ################################################################################################################################

    def delete(self, key:'str') -> 'None':
        """ Deletes a key from the cache. No-op if the key does not exist.
        """
        redis_key = self._make_key(key)
        self.redis.delete(redis_key)

# ################################################################################################################################
# ################################################################################################################################
