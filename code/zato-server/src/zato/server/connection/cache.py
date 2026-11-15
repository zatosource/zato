
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
    from zato.common.typing_ import any_, anytuple
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

class ModuleCtx:

    # The generation counter of the cached responses of a channel, outside the key space that a purge deletes
    Response_Generation_Key = 'cache:generation:{}'

    # The prefix of the coalescing lock of a cached response, outside the key space that a purge deletes
    Response_Lock_Prefix = 'cache:lock:'

    # Stores a value only while a counter holds the value read earlier, an absent counter reading as 0,
    # with ARGV[3] as the expiry in seconds and 0 meaning no expiry.
    Set_If_Counter_Script = """
local current = redis.call('get', KEYS[2])
if current == false then
    current = '0'
end
if current ~= ARGV[1] then
    return 0
end
if ARGV[3] == '0' then
    redis.call('set', KEYS[1], ARGV[2])
else
    redis.call('set', KEYS[1], ARGV[2], 'EX', ARGV[3])
end
return 1
"""

    # Deletes a key only while it holds the value given, so a holder never deletes a key that expired
    # and was stored again by another holder.
    Delete_If_Value_Script = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
end
return 0
"""

# ################################################################################################################################
# ################################################################################################################################

class CacheAPI:
    """ Redis-backed cache with get, set, delete, and exists operations.
    """
    def __init__(self, redis_client:'Redis', config_manager:'ConfigManager | None'=None) -> 'None':
        self.redis = redis_client

        # Used to resolve channel names to their IDs when responses are invalidated by name
        self.config_manager = config_manager

        self._set_if_counter = self.redis.register_script(ModuleCtx.Set_If_Counter_Script)
        self._delete_if_value = self.redis.register_script(ModuleCtx.Delete_If_Value_Script)

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
            _ = self.redis.set(redis_key, serialized, ex=expiry_int)

        else:
            _ = self.redis.set(redis_key, serialized)

# ################################################################################################################################

    def set_if_absent(self, key:'str', value:'any_', expiry:'int'=0) -> 'bool':
        """ Stores a value only if the key is not there already. Returns True when this call is the
        one that stored it, which is what lets several processes claim the same key and have exactly
        one of them win. Expiry is in seconds, 0 means no expiry.
        """
        redis_key = self._make_key(key)
        serialized = dumps(value)

        if expiry:
            stored = self.redis.set(redis_key, serialized, ex=expiry, nx=True)
        else:
            stored = self.redis.set(redis_key, serialized, nx=True)

        out = bool(stored)
        return out

# ################################################################################################################################

    def get_with_counter(self, key:'str', counter_key:'str') -> 'anytuple':
        """ Returns the value stored under the key, or None, and the value of a counter, 0 when the counter
        does not exist, both read in one round trip.
        """
        redis_key = self._make_key(key)
        redis_counter_key = self._make_key(counter_key)

        raw, raw_counter = self.redis.mget([redis_key, redis_counter_key])

        if raw is None:
            value = None
        else:
            value = loads(raw)

        if raw_counter is None:
            counter = 0
        else:
            counter = int(raw_counter)

        out = (value, counter)
        return out

# ################################################################################################################################

    def get_counter(self, counter_key:'str') -> 'int':
        """ Returns the value of a counter, 0 when the counter does not exist.
        """
        redis_counter_key = self._make_key(counter_key)
        raw_counter = self.redis.get(redis_counter_key)

        if raw_counter is None:
            return 0

        out = int(raw_counter)
        return out

# ################################################################################################################################

    def increment_counter(self, counter_key:'str') -> 'int':
        """ Increments a counter, which starts from 0, and returns its new value.
        """
        redis_counter_key = self._make_key(counter_key)

        out = self.redis.incr(redis_counter_key)
        return out

# ################################################################################################################################

    def set_if_counter(self, key:'str', value:'any_', expiry:'int', counter_key:'str', counter:'int') -> 'bool':
        """ Stores a value under the key only while the counter holds the value given, in one atomic step.
        Returns True when the value was stored. Expiry is in seconds, 0 means no expiry.
        """
        redis_key = self._make_key(key)
        redis_counter_key = self._make_key(counter_key)
        serialized = dumps(value)

        stored = self._set_if_counter(keys=[redis_key, redis_counter_key], args=[counter, serialized, expiry])

        out = bool(stored)
        return out

# ################################################################################################################################

    def delete_if_value(self, key:'str', value:'any_') -> 'bool':
        """ Deletes a key only while it holds the value given, in one atomic step. Returns True when the key was deleted.
        """
        redis_key = self._make_key(key)
        serialized = dumps(value)

        deleted = self._delete_if_value(keys=[redis_key], args=[serialized])

        out = bool(deleted)
        return out

# ################################################################################################################################

    def delete(self, key:'str') -> 'None':
        """ Deletes a key from the cache. No-op if the key does not exist.
        """
        redis_key = self._make_key(key)
        _ = self.redis.delete(redis_key)

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

        # .. a response whose service read the data before this point is no longer stored ..
        generation_key = ModuleCtx.Response_Generation_Key.format(channel_id)
        _ = self.increment_counter(generation_key)

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
