
# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from fnmatch import fnmatch
from json import dumps, loads
from logging import getLogger

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redis import Redis
    from zato.common.typing_ import any_
    from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Key_Prefix = 'zato:cache:'
_response_cache = HTTP_SOAP.ResponseCache

# ################################################################################################################################
# ################################################################################################################################

class CacheAPI:
    """ Redis-backed cache with get, set, delete, and exists operations.
    """
    def __init__(self, redis_client:'Redis', config_manager:'ConfigManager | None'=None) -> 'None':
        self.redis = redis_client

        # Used to resolve channel names to their IDs when responses are invalidated by name
        self.config_manager = config_manager

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

    def delete_by_prefix(self, prefix:'str') -> 'None':
        """ Deletes all the keys that start with the given prefix. No-op if none match.
        """
        match = self._make_key(prefix) + '*'

        for redis_key in self.redis.scan_iter(match=match):
            _ = self.redis.delete(redis_key)

# ################################################################################################################################

    def invalidate_response(self, channel_name:'str', pattern:'str'='') -> 'None':
        """ Invalidates cached responses of a REST or SOAP channel. Without a pattern, the channel's whole
        key space is purged. With a pattern, only the entries whose path and query match it are deleted,
        e.g. '/api/customers*' - admission markers are left alone because they carry no path to match.
        """

        # Resolve the channel's name to its ID through the in-memory config store ..
        config_manager = cast_('ConfigManager', self.config_manager)
        channel = config_manager.get_channel_rest(channel_name)

        if not channel:
            raise Exception(f'Channel not found: `{channel_name}` (invalidate-response)')

        channel_id = channel['id']
        prefix = _response_cache.Key_Prefix.format(channel_id)

        # .. without a pattern, the whole prefix goes away ..
        if not pattern:
            self.delete_by_prefix(prefix)
            return

        # .. with a pattern, each entry's stored path and query decides its fate.
        match = self._make_key(prefix) + '*'

        for redis_key in self.redis.scan_iter(match=match):
            raw = self.redis.get(redis_key)

            if raw is None:
                continue

            value = loads(cast_('str', raw))

            # Only full entries carry a path - markers are one-byte strings
            if isinstance(value, dict):
                if fnmatch(value['path'], pattern):
                    _ = self.redis.delete(redis_key)

# ################################################################################################################################
# ################################################################################################################################
