# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock

# Zato
from zato.cache import Cache as _CyCache
from zato.common import CACHE

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class Cache(object):
    """ The cache API through which services access the built-in self.cache objects.
    Attribute self.impl is the actual Cython-based cache implementation.
    """
    def __init__(self, config):
        self.config = config
        self.needs_sync = self.config.sync_method != CACHE.SYNC_METHOD.NO_SYNC.id
        self.impl = _CyCache(self.config.max_size, self.config.max_item_size, self.config.extend_expiry_on_get,
            self.config.extend_expiry_on_set)
        spawn(self._delete_expired)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        del self.impl[key]

    def __contains__(self, key):
        return key in self.impl

    def __len__(self):
        return len(self.impl)

    def set(self, key, value, expiry=0.0):
        """ Sets key to a given value. Key must be string/unicode. Value must be an integer or string/unicode.
        Expiry is in seconds (or a fraction of).
        """
        meta_ref = {} if self.needs_sync else None
        self.impl.set(key, value, expiry, meta_ref)

    def get(self, key, details=False):
        """ Returns a value stored under a given key. If details is True, return metadata about the key as well.
        """
        return self.impl.get(key, details)

    def delete(self, key):
        """ Deletes a cache entry by its key.
        """
        self.impl.delete(key)

    def expire(self, key, expiry=0.0):
        """ Sets expiry in seconds (or a fraction of) for a given key.
        """
        meta_ref = {} if self.needs_sync else None
        self.impl.expire(key, expiry, meta_ref)

    def keys(self):
        """ Returns all keys in the cache - like dict.keys().
        """
        return self.impl.keys()

    def values(self):
        """ Returns all values in the cache - like dict.values().
        """
        return self.impl.values()

    def items(self):
        """ Returns all items in the cache - like dict.items().
        """
        return self.impl.items()

    def clear(self):
        """ Clears the cache - removes all entries.
        """
        self.impl.clear()

    def _delete_expired(self, interval=5, _sleep=sleep):
        """ Invokes in its own greenlet in background to delete expired cache entries.
        """
        try:
            while True:
                try:
                    _sleep(interval)
                    deleted = self.impl.delete_expired()
                except Exception, e:
                    logger.warn('Exception while deleting expired keys %s', format_exc(e))
                    _sleep(2)
                else:
                    if deleted:
                        logger.info('Cache `%s` deleted keys expired in the last %ss - %s', self.config.name, interval, deleted)
        except Exception, e:
            logger.warn('Exception in _delete_expired loop %s', format_exc(e))

    def sync_entry(self, key, value, expiry):
        """ Invoked by other servers/processes to set this cache's key to value along with expiry,
        synchronizing this cache's entry with the one the calling cache has.
        """

# ################################################################################################################################

class _NotConfiguredAPI(object):
    def set(self, *args, **kwargs):
        raise Exception('Default cache is not configured')
    get = set

# ################################################################################################################################

class CacheAPI(object):
    """ Base class for all cache objects.
    """
    def __init__(self):
        self.lock = RLock()
        self.default = _NotConfiguredAPI()
        self.caches = {}

    def _maybe_set_default(self, config, cache):
        if config.is_default:
            self.default = cache

# ################################################################################################################################

    def _create_builtin(self, config):
        return Cache(config)

# ################################################################################################################################

    def _create(self, config):
        func = getattr(self, '_create_{}'.format(config.cache_type))
        cache = func(config)
        self.caches[config.name] = cache
        self._maybe_set_default(config, cache)

# ################################################################################################################################

    def create(self, config):
        with self.lock:
            self._create(config)

# ################################################################################################################################

    def _edit(self, config):
        self.caches[config.name].update_config(config)

# ################################################################################################################################

    def edit(self, config):
        with self.lock:
            self._edit(config)

# ################################################################################################################################

    def _delete(self, name):
        del self.caches[name]

# ################################################################################################################################

    def delete(self, config):
        with self.lock:
            self._delete(config.name)

# ################################################################################################################################

    def _clear(self, name):
        self.caches[name].clear()

# ################################################################################################################################

    def clear(self, name):
        with self.lock:
            self._clear(name)

# ################################################################################################################################

    def get_size(self, name):
        return len(self.caches[name])

# ################################################################################################################################
