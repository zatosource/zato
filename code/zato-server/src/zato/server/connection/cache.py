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

# python-memcached
from memcache import Client as _MemcachedClient

# Paste
from paste.util.converters import asbool

# Zato
from zato.cache import Cache as _CyCache
from zato.common import CACHE
from zato.common.broker_message import CACHE as CACHE_BROKER_MSG
from zato.common.util import parse_extra_into_dict

builtin_op_to_broker_msg = {
    CACHE.STATE_CHANGED.GET: CACHE_BROKER_MSG.BUILTIN_STATE_CHANGED_GET.value,
    CACHE.STATE_CHANGED.SET: CACHE_BROKER_MSG.BUILTIN_STATE_CHANGED_SET.value,
    CACHE.STATE_CHANGED.DELETE: CACHE_BROKER_MSG.BUILTIN_STATE_CHANGED_DELETE.value,
    CACHE.STATE_CHANGED.EXPIRE: CACHE_BROKER_MSG.BUILTIN_STATE_CHANGED_EXPIRE.value,
}

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class Cache(object):
    """ The cache API through which services access the built-in self.cache objects.
    Attribute self.impl is the actual Cython-based cache implementation.
    """
    def __init__(self, config):
        self.config = config
        self.after_state_changed_callback = self.config.after_state_changed_callback
        self.needs_sync = self.config.sync_method != CACHE.SYNC_METHOD.NO_SYNC.id
        self.impl = _CyCache(self.config.max_size, self.config.max_item_size, self.config.extend_expiry_on_get,
            self.config.extend_expiry_on_set)
        spawn(self._delete_expired)

# ################################################################################################################################

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.impl.get_slice(key.start, key.stop, key.step)
        else:
            return self.get(key)

# ################################################################################################################################

    def __setitem__(self, key, value):
        self.set(key, value)

# ################################################################################################################################

    def __delitem__(self, key):
        self.delete(key)

# ################################################################################################################################

    def __contains__(self, key):
        return key in self.impl

# ################################################################################################################################

    def __len__(self):
        return len(self.impl)

# ################################################################################################################################

    def get(self, key, details=False, _GET=CACHE.STATE_CHANGED.GET):
        """ Returns a value stored under a given key. If details is True, return metadata about the key as well.
        """
        needs_sync = self.needs_sync and self.config.extend_expiry_on_get
        meta_ref = {'key':key} if needs_sync else None

        if needs_sync:
            spawn(self.after_state_changed_callback, _GET, self.config.name, meta_ref)

        return self.impl.get(key, details, meta_ref)

# ################################################################################################################################

    def set(self, key, value, expiry=0.0, _SET=CACHE.STATE_CHANGED.SET):
        """ Sets key to a given value. Key must be string/unicode. Value must be an integer or string/unicode.
        Expiry is in seconds (or a fraction of).
        """
        meta_ref = {'key':key, 'value':value, 'expiry':expiry} if self.needs_sync else None
        self.impl.set(key, value, expiry, meta_ref)

        if self.needs_sync:
            spawn(self.after_state_changed_callback, _SET, self.config.name, meta_ref)

# ################################################################################################################################

    def delete(self, key, raise_key_error=True, _DELETE=CACHE.STATE_CHANGED.DELETE):
        """ Deletes a cache entry by its key.
        """
        try:
            self.impl.delete(key)
        except KeyError:
            if raise_key_error:
                raise
        else:
            if self.needs_sync:
                spawn(self.after_state_changed_callback, _DELETE, self.config.name, {'key':key})

# ################################################################################################################################

    def expire(self, key, expiry=0.0, _EXPIRE=CACHE.STATE_CHANGED.EXPIRE):
        """ Sets expiry in seconds (or a fraction of) for a given key.
        """
        meta_ref = {'key':key, 'expiry':expiry} if self.needs_sync else None
        self.impl.expire(key, expiry, meta_ref)

        if self.needs_sync:
            spawn(self.after_state_changed_callback, _EXPIRE, self.config.name, meta_ref)

# ################################################################################################################################

    def keys(self):
        """ Returns all keys in the cache - like dict.keys().
        """
        return self.impl.keys()

# ################################################################################################################################

    def values(self):
        """ Returns all values in the cache - like dict.values().
        """
        return self.impl.values()

# ################################################################################################################################

    def items(self):
        """ Returns all items in the cache - like dict.items().
        """
        return self.impl.items()

    def iteritems(self):
        """ Returns an iterator over all items in the cache - like dict.iteritems().
        """
        return self.impl.items()

# ################################################################################################################################

    def clear(self):
        """ Clears the cache - removes all entries.
        """
        self.impl.clear()

# ################################################################################################################################

    def update_config(self, config):
        self.needs_sync = self.config.sync_method != CACHE.SYNC_METHOD.NO_SYNC.id
        self.impl.update_config(config)

# ################################################################################################################################

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

# ################################################################################################################################

    def sync_after_get(self, data):
        """ Invoked by Cache API to synchronizes this worker's caches after a .get operation in another worker process.
        """
        self.impl.set_expiration_data(data.key, data.expiry, data.expires_at)

# ################################################################################################################################

    def sync_after_set(self, data):
        """ Invoked by Cache API to synchronizes this worker's caches after a .set operation in another worker process.
        """
        self.impl.set(data.key, data.value, data.expiry, None)

# ################################################################################################################################

    def sync_after_delete(self, data):
        """ Invoked by Cache API to synchronizes this worker's caches after a .delete operation in another worker process.
        """
        self.impl.delete(data.key)

# ################################################################################################################################

    def sync_after_expire(self, data):
        """ Invoked by Cache API to synchronizes this worker's caches after an .expire operation in another worker process.
        """
        self.impl.set_expiration_data(data.key, data.expiry, data.expires_at)

# ################################################################################################################################

class _NotConfiguredAPI(object):
    def set(self, *args, **kwargs):
        raise Exception('Default cache is not configured')
    get = set

# ################################################################################################################################

class CacheAPI(object):
    """ Base class for all cache objects.
    """
    def __init__(self, server):
        self.server = server
        self.lock = RLock()
        self.default = _NotConfiguredAPI()
        self.caches = {
            CACHE.TYPE.BUILTIN:{},
            CACHE.TYPE.MEMCACHED:{},
        }

        self.builtin = self.caches[CACHE.TYPE.BUILTIN]
        self.memcached = self.caches[CACHE.TYPE.MEMCACHED]

    def _maybe_set_default(self, config, cache):
        if config.is_default:
            self.default = cache

# ################################################################################################################################

    def after_state_changed(self, op, cache_name, data, _broker_msg=builtin_op_to_broker_msg):
        """ Callback method invoked by each cache if it requires synchronization with other worker processes.
        """
        try:
            data['action'] = _broker_msg[op]
            data['cache_name'] = cache_name
            data['source_worker_id'] = self.server.worker_id
            self.server.broker_client.publish(data)
        except Exception, e:
            logger.warn('Could not run `%s` after_state_changed in cache `%s`, data:`%s`, e:`%s`',
                op, cache_name, data, format_exc(e))

# ################################################################################################################################

    def _create_builtin(self, config):
        """ A low-level method building a bCache object for built-in caches. Must be called with self.lock held.
        """
        config.after_state_changed_callback = self.after_state_changed
        return Cache(config)

# ################################################################################################################################

    def _create_memcached(self, config):
        """ A low-level method building a Memcached-based cache connections.
        """
        def impl():
            try:
                servers = [elem.strip() for elem in config.servers.splitlines()]
                cache = _MemcachedClient(servers, asbool(config.is_debug), **parse_extra_into_dict(config.extra))
                self._add_cache(config, cache)
            except Exception, e:
                logger.warn(format_exc(e))

        spawn(impl)

# ################################################################################################################################

    def _add_cache(self, config, cache):

        # Add it to caches
        self.caches[config.cache_type][config.name] = cache

        # If told to be configuration, make this cache the default one
        self._maybe_set_default(config, cache)

# ################################################################################################################################

    def _create(self, config):
        """ A low-level method building caches. Must be called with self.lock held.
        """
        # Create a cache object out of configuration
        cache = getattr(self, '_create_{}'.format(config.cache_type))(config)

        # Only built-in caches can be added directly because they do not establish
        # any external connections, any other cache will be built in a background greenlet
        if config.cache_type == CACHE.TYPE.BUILTIN:
            self._add_cache(config, cache)

# ################################################################################################################################

    def create(self, config):
        """ Public method for building caches out of configuration.
        """
        with self.lock:
            self._create(config)

# ################################################################################################################################

    def _edit(self, config):
        """ A low-level method for updating configuration of a given cache. Must be called with self.lock held.
        """
        cache = self.caches[config.cache_type].pop(config.old_name)

        if config.cache_type == CACHE.TYPE.BUILTIN:
            cache.update_config(config)
            self._add_cache(config, cache)
        else:
            cache.disconnect_all()
            self._delete(config.cache_type, config.old_name)
            self._create_memcached(config)

# ################################################################################################################################

    def edit(self, config):
        """ Public method for updating configuration of a given cache.
        """
        with self.lock:
            self._edit(config)

# ################################################################################################################################

    def _delete(self, cache_type, name):
        """ A low-level method for deleting a given cache. Must be called with self.lock held.
        """
        cache = self.caches[cache_type][name]

        if cache_type == CACHE.TYPE.BUILTIN:
            self._clear(cache_type, name)
        else:
            cache.disconnect_all()

        del self.caches[cache_type][name]

# ################################################################################################################################

    def delete(self, config):
        """ Public method for updating configuration of a given cache.
        """
        with self.lock:
            self._delete(config.cache_type, config.name)

# ################################################################################################################################

    def _clear(self, cache_type, name):
        """ A low-level method for clearing out contents of a given cache. Must be called with self.lock held.
        """
        self.caches[cache_type][name].clear()

# ################################################################################################################################

    def clear(self, cache_type, name):
        """ Public method for clearing out a given cache.
        """
        with self.lock:
            self._clear(cache_type, name)

# ################################################################################################################################

    def get_cache(self, cache_type, name):
        """ Returns the lower-level cache implementation object by its type and name.
        """
        with self.lock:
            return self.caches[cache_type][name]

# ################################################################################################################################

    def get_size(self, cache_type, name):
        """ Returns current size, the number of entries, in a given cache.
        """
        print(self.caches[cache_type])
        return len(self.caches[cache_type][name])

# ################################################################################################################################

    def sync_after_get(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .get operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_get(data)

# ################################################################################################################################

    def sync_after_set(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .set operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_set(data)

# ################################################################################################################################

    def sync_after_delete(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .delete operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_delete(data)

# ################################################################################################################################

    def sync_after_expire(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after an .expire operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_expire(data)

# ################################################################################################################################
