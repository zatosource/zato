# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
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
from zato.common.api import CACHE, ZATO_NOT_GIVEN
from zato.common.broker_message import CACHE as CACHE_BROKER_MSG
from zato.common.typing_ import cast_
from zato.common.util.api import parse_extra_into_dict

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems, itervalues
from zato.common.py23_.past.builtins import basestring
from zato.common.py23_ import pickle_dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

builtin_ops = [
    'CLEAR',
    'DELETE',
    'DELETE_BY_PREFIX', 'DELETE_BY_SUFFIX',
    'DELETE_BY_REGEX',
    'DELETE_CONTAINS', 'DELETE_NOT_CONTAINS',
    'DELETE_CONTAINS_ALL', 'DELETE_CONTAINS_ANY',
    'EXPIRE',
    'EXPIRE_BY_PREFIX', 'EXPIRE_BY_SUFFIX',
    'EXPIRE_BY_REGEX',
    'EXPIRE_CONTAINS', 'EXPIRE_NOT_CONTAINS',
    'EXPIRE_CONTAINS_ALL', 'EXPIRE_CONTAINS_ANY',
    'SET',
    'SET_BY_PREFIX', 'SET_BY_SUFFIX',
    'SET_BY_REGEX',
    'SET_CONTAINS', 'SET_NOT_CONTAINS',
    'SET_CONTAINS_ALL', 'SET_CONTAINS_ANY',
]

builtin_op_to_broker_msg = {}

for builtin_op in builtin_ops:
    common_key = getattr(CACHE.STATE_CHANGED, builtin_op)
    broker_msg_value = getattr(CACHE_BROKER_MSG, 'BUILTIN_STATE_CHANGED_{}'.format(builtin_op)).value

    builtin_op_to_broker_msg[common_key] = broker_msg_value

# ################################################################################################################################

default_get = ZATO_NOT_GIVEN # A singleton to indicate that no default for Cache.get was given on input

_no_key = 'zato-no-key'
_no_value = 'zato-no-value'

# ################################################################################################################################

class Cache:
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
        return self.set(key, value)

# ################################################################################################################################

    def __delitem__(self, key):
        return self.delete(key)

# ################################################################################################################################

    def __contains__(self, key):
        return key in self.impl

# ################################################################################################################################

    def __len__(self):
        return len(self.impl)

# ################################################################################################################################

    def get(self, key, default=default_get, details=False) -> 'any_':
        """ Returns a value stored under a given key. If details is True, return metadata about the key as well.
        """
        return self.impl.get(key, default if default != default_get else self.impl.default_get, details)

# ################################################################################################################################

    def has_key(self, key, default=default_get, details=False) -> 'bool':
        """ Returns True or False, depending on whether such a key exists in the cache or not.
        """
        value = self.get(key, default=default, details=details)
        return value != ZATO_NOT_GIVEN

# ################################################################################################################################

    def get_by_prefix(self, key, details=False, limit=0):
        """ Returns a dictionary of key:value items for keys matching the prefix given on input.
        """
        return self.impl.get_by_prefix(key, details, limit)

# ################################################################################################################################

    def get_by_suffix(self, key, details=False, limit=0):
        """ Returns a dictionary of key:value items for keys matching the suffix given on input.
        """
        return self.impl.get_by_suffix(key, details, limit)

# ################################################################################################################################

    def get_by_regex(self, key, details=False, limit=0):
        """ Returns a dictionary of key:value items for keys matching the regular expression given on input.
        """
        return self.impl.get_by_regex(key, details, limit)

# ################################################################################################################################

    def get_contains(self, key, details=False, limit=0):
        """ Returns a dictionary of key:value items for keys containing the string given on input.
        """
        return self.impl.get_contains(key, details, limit)

# ################################################################################################################################

    def get_not_contains(self, key, details=False, limit=0):
        """ Returns a dictionary of key:value items for keys that don't contain the string given on input.
        """
        return self.impl.get_not_contains(key, details, limit)

# ################################################################################################################################

    def get_contains_all(self, key, details=False, limit=0):
        """ Returns a dictionary of key:value items for keys that contain all of elements in the input list of strings.
        """
        return self.impl.get_contains_all(key, details, limit)

# ################################################################################################################################

    def get_contains_any(self, key, details=False, limit=0):
        """ Returns a dictionary of key:value items for keys that contain at least one of elements in the input list of strings.
        """
        return self.impl.get_contains_any(key, details, limit)

# ################################################################################################################################

    def set(self, key, value, expiry=0.0, details=False, _OP=CACHE.STATE_CHANGED.SET):
        """ Sets key to a given value. Key must be string/unicode. Value must be an integer or string/unicode.
        Expiry is in seconds (or a fraction of).
        """
        meta_ref = {'key':key, 'value':value, 'expiry':expiry} if self.needs_sync else None
        value = self.impl.set(key, value, expiry, details, meta_ref)
        if self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, meta_ref)

        return value

# ################################################################################################################################

    def set_by_prefix(self, key, value, expiry=0.0, return_found=False, details=False, limit=0,
        _OP=CACHE.STATE_CHANGED.SET_BY_PREFIX):
        """ Sets keys matching the prefix of a given value - non-string-like keys are ignored. Prefix must be string/unicode.
        Value must be an integer or string/unicode. Expiry is in seconds (or a fraction of). Optionally,
        returns all matched keys and their previous values.
        """
        meta_ref = {'_now': None, '_any_found': False}
        out = self.impl.set_by_prefix(key, value, expiry, False, meta_ref, return_found, limit)

        if meta_ref['_any_found'] and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'value':value,
                'expiry':expiry,
                'limit':limit,
                'orig_now':meta_ref['_now']
            })

        return out

# ################################################################################################################################

    def set_by_suffix(self, key, value, expiry=0.0, return_found=False, details=False, limit=0,
        _OP=CACHE.STATE_CHANGED.SET_BY_SUFFIX):
        """ Sets keys matching the suffix to a given value - non-string-like keys are ignored. Suffix must be string/unicode.
        Value must be an integer or string/unicode. Expiry is in seconds (or a fraction of). Optionally,
        returns all matched keys and their previous values.
        """
        meta_ref = {'_now': None, '_any_found': False}
        out = self.impl.set_by_suffix(key, value, expiry, False, meta_ref, return_found, limit)

        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'value':value,
                'expiry':expiry,
                'limit':limit,
                'orig_now':meta_ref['_now']
            })

        return out

# ################################################################################################################################

    def set_by_regex(self, key, value, expiry=0.0, return_found=False, details=False, limit=0,
        _OP=CACHE.STATE_CHANGED.SET_BY_REGEX):
        """ Sets value for keys matching the input regular expresion - non-string-like keys are ignored.
        Value must be an integer or string/unicode. Expiry is in seconds (or a fraction of). Optionally,
        returns all matched keys and their previous values.
        """
        meta_ref = {'_now': None, '_any_found': False}
        out = self.impl.set_by_regex(key, value, expiry, False, meta_ref, return_found, limit)

        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'value':value,
                'expiry':expiry,
                'limit':limit,
                'orig_now':meta_ref['_now']
            })

        return out

# ################################################################################################################################

    def set_contains(self, key, value, expiry=0.0, return_found=False, details=False, limit=0,
        _OP=CACHE.STATE_CHANGED.SET_CONTAINS):
        """ Sets value for keys containing the input string - non-string-like keys are ignored.
        Value must be an integer or string/unicode. Expiry is in seconds (or a fraction of). Optionally,
        returns all matched keys and their previous values.
        """
        meta_ref = {'_now': None, '_any_found': False}
        out = self.impl.set_contains(key, value, expiry, False, meta_ref, return_found, limit)

        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'value':value,
                'expiry':expiry,
                'limit':limit,
                'orig_now':meta_ref['_now']
            })

        return out

# ################################################################################################################################

    def set_not_contains(self, key, value, expiry=0.0, return_found=False, details=False, limit=0,
        _OP=CACHE.STATE_CHANGED.SET_NOT_CONTAINS):
        """ Sets value for keys that don't contain the input string - non-string-like keys are ignored.
        Value must be an integer or string/unicode. Expiry is in seconds (or a fraction of). Optionally,
        returns all matched keys and their previous values.
        """
        meta_ref = {'_now': None, '_any_found': False}
        out = self.impl.set_not_contains(key, value, expiry, False, meta_ref, return_found, limit)

        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'value':value,
                'expiry':expiry,
                'limit':limit,
                'orig_now':meta_ref['_now']
            })

        return out

# ################################################################################################################################

    def set_contains_all(self, key, value, expiry=0.0, return_found=False, details=False, limit=0,
        _OP=CACHE.STATE_CHANGED.SET_CONTAINS_ALL):
        """ Sets value for keys that contain all elements from the input list - non-string-like keys are ignored.
        Value must be an integer or string/unicode. Expiry is in seconds (or a fraction of). Optionally,
        returns all matched keys and their previous values.
        """
        meta_ref = {'_now': None, '_any_found': False}
        out = self.impl.set_contains_all(key, value, expiry, False, meta_ref, return_found, limit)

        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'value':value,
                'expiry':expiry,
                'limit':limit,
                'orig_now':meta_ref['_now']
            })

        return out

# ################################################################################################################################

    def set_contains_any(self, key, value, expiry=0.0, return_found=False, details=False, limit=0,
        _OP=CACHE.STATE_CHANGED.SET_CONTAINS_ANY):
        """ Sets value for keys that contain at least one of elements from the input list - non-string-like keys are ignored.
        Value must be an integer or string/unicode. Expiry is in seconds (or a fraction of). Optionally,
        returns all matched keys and their previous values.
        """
        meta_ref = {'_now': None, '_any_found': False}
        out = self.impl.set_contains_any(key, value, expiry, False, meta_ref, return_found, limit)

        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'value':value,
                'expiry':expiry,
                'limit':limit,
                'orig_now':meta_ref['_now']
            })

        return out

# ################################################################################################################################

    def delete(self, key, raise_key_error=True, _OP=CACHE.STATE_CHANGED.DELETE):
        """ Deletes a cache entry by its key.
        """
        try:
            value = self.impl.delete(key)
        except KeyError:
            if raise_key_error:
                raise
        else:
            if self.needs_sync:
                spawn(self.after_state_changed_callback, _OP, self.config.name, {'key':key})

            return value

# ################################################################################################################################

    def delete_by_prefix(self, key, return_found=False, limit=0, _OP=CACHE.STATE_CHANGED.DELETE_BY_PREFIX):
        """ Deletes cache entries by their key prefixes - non-string-like keys are ignored.
        Optionally, returns all matched keys and their previous values.
        """
        out = self.impl.delete_by_prefix(key, return_found, limit)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def delete_by_suffix(self, key, return_found=False, limit=0, _OP=CACHE.STATE_CHANGED.DELETE_BY_SUFFIX):
        """ Deletes cache entries by their key suffixes - non-string-like keys are ignored.
        Optionally, returns all matched keys and their previous values.
        """
        out = self.impl.delete_by_suffix(key, return_found, limit)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def delete_by_regex(self, key, return_found=False, limit=0, _OP=CACHE.STATE_CHANGED.DELETE_BY_REGEX):
        """ Deletes cache entries with keys matching the input regular expression - non-string-like keys are ignored.
        Optionally, returns all matched keys and their previous values.
        """
        out = self.impl.delete_by_regex(key, return_found, limit)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def delete_contains(self, key, return_found=False, limit=0, _OP=CACHE.STATE_CHANGED.DELETE_CONTAINS):
        """ Deletes cache entries with keys containing the input string - non-string-like keys are ignored.
        Optionally, returns all matched keys and their previous values.
        """
        out = self.impl.delete_contains(key, return_found, limit)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def delete_not_contains(self, key, return_found=False, limit=0, _OP=CACHE.STATE_CHANGED.DELETE_NOT_CONTAINS):
        """ Deletes cache entries with keys that don't contain the input string - non-string-like keys are ignored.
        Optionally, returns all matched keys and their previous values.
        """
        out = self.impl.delete_not_contains(key, return_found, limit)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def delete_contains_all(self, key, return_found=False, limit=0, _OP=CACHE.STATE_CHANGED.DELETE_CONTAINS_ALL):
        """ Deletes cache entries with keys containing all of elements in the input string - non-string-like keys are ignored.
        Optionally, returns all matched keys and their previous values.
        """
        out = self.impl.delete_contains_all(key, return_found, limit)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def delete_contains_any(self, key, return_found=False, limit=0, _OP=CACHE.STATE_CHANGED.DELETE_CONTAINS_ANY):
        """ Deletes cache entries with keys containing at least one of elements in the input string -
        non-string-like keys are ignored. Optionally, returns all matched keys and their previous values.
        """
        out = self.impl.delete_contains_any(key, return_found, limit)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def expire(self, key, expiry=0.0, _OP=CACHE.STATE_CHANGED.EXPIRE):
        """ Sets expiry in seconds (or a fraction of) for a given key.
        """
        meta_ref = {'key':key, 'expiry':expiry} if self.needs_sync else None
        found_key = self.impl.expire(key, expiry, meta_ref)

        if self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, meta_ref)

        return found_key

# ################################################################################################################################

    def expire_by_prefix(self, key, expiry=0.0, limit=0, _OP=CACHE.STATE_CHANGED.EXPIRE_BY_PREFIX):
        """ Sets expiry in seconds (or a fraction of) for all keys matching the input prefix.
        """
        out = self.impl.expire_by_prefix(key, expiry)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'expiry':expiry,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def expire_by_suffix(self, key, expiry=0.0, limit=0, _OP=CACHE.STATE_CHANGED.EXPIRE_BY_SUFFIX):
        """ Sets expiry in seconds (or a fraction of) for all keys matching the input suffix.
        """
        out = self.impl.expire_by_suffix(key, expiry)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'expiry':expiry,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def expire_by_regex(self, key, expiry=0.0, limit=0, _OP=CACHE.STATE_CHANGED.EXPIRE_BY_REGEX):
        """ Sets expiry in seconds (or a fraction of) for all keys matching the input regular expression.
        """
        out = self.impl.expire_by_regex(key, expiry)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'expiry':expiry,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def expire_contains(self, key, expiry=0.0, limit=0, _OP=CACHE.STATE_CHANGED.EXPIRE_CONTAINS):
        """ Sets expiry in seconds (or a fraction of) for all keys containing the input string.
        """
        out = self.impl.expire_contains(key, expiry)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'expiry':expiry,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def expire_not_contains(self, key, expiry=0.0, limit=0, _OP=CACHE.STATE_CHANGED.EXPIRE_NOT_CONTAINS):
        """ Sets expiry in seconds (or a fraction of) for all keys that don't contain the input string.
        """
        out = self.impl.expire_not_contains(key, expiry)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'expiry':expiry,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def expire_contains_all(self, key, expiry=0.0, limit=0, _OP=CACHE.STATE_CHANGED.EXPIRE_CONTAINS_ALL):
        """ Sets expiry in seconds (or a fraction of) for keys that contain all of input elements.
        """
        out = self.impl.expire_contains_all(key, expiry)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'expiry':expiry,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def expire_contains_any(self, key, expiry=0.0, limit=0, _OP=CACHE.STATE_CHANGED.EXPIRE_CONTAINS_ALL):
        """ Sets expiry in seconds (or a fraction of) for keys that contain at least one of input elements.
        """
        out = self.impl.expire_contains_any(key, expiry)
        if out and self.needs_sync:
            spawn(self.after_state_changed_callback, _OP, self.config.name, {
                'key':key,
                'expiry':expiry,
                'limit':limit
            })

        return out

# ################################################################################################################################

    def keys(self):
        """ Returns all keys in the cache - like dict.keys().
        """
        return self.impl.keys()

# ################################################################################################################################

    def iterkeys(self):
        """ Returns an iterator over all keys in the cache - like dict.iterkeys().
        """
        return self.impl.iterkeys()

# ################################################################################################################################

    def values(self):
        """ Returns all values in the cache - like dict.values().
        """
        return self.impl.values()

# ################################################################################################################################

    def itervalues(self):
        """ Returns an iterator over all values in the cache - like dict.itervalues().
        """
        return itervalues(self.impl)

# ################################################################################################################################

    def items(self):
        """ Returns all items in the cache - like dict.items().
        """
        return self.impl.items()

# ################################################################################################################################

    def iteritems(self):
        """ Returns an iterator over all items in the cache - like dict.iteritems().
        """
        return iteritems(self.impl)

# ################################################################################################################################

    def clear(self, _CLEAR=CACHE.STATE_CHANGED.CLEAR):
        """ Clears the cache - removes all entries.
        """
        self.impl.clear()

        if self.needs_sync:
            spawn(self.after_state_changed_callback, _CLEAR, self.config.name, {})

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
                except Exception:
                    logger.warning('Exception while deleting expired keys %s', format_exc())
                    _sleep(2)
                else:
                    if deleted:
                        logger.info('Cache `%s` deleted keys expired in the last %ss - %s', self.config.name, interval, deleted)
        except Exception:
            logger.warning('Exception in _delete_expired loop %s', format_exc())

# ################################################################################################################################

    def sync_after_set(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .set operation in another worker process.
        """
        self.impl.set(data.key, data.value, data.expiry, False, None, data.orig_now)

    def sync_after_set_by_prefix(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .set_by_prefix operation in another worker process.
        """
        self.impl.set_by_prefix(data.key, data.value, data.expiry, False, None, data.limit, data.orig_now)

    def sync_after_set_by_suffix(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .set_by_suffix operation in another worker process.
        """
        self.impl.set_by_suffix(data.key, data.value, data.expiry, False, None, data.limit, data.orig_now)

    def sync_after_set_by_regex(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .set_by_regex operation in another worker process.
        """
        self.impl.set_by_regex(data.key, data.value, data.expiry, False, None, data.limit, data.orig_now)

    def sync_after_set_contains(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .set_contains operation in another worker process.
        """
        self.impl.set_contains(data.key, data.value, data.expiry, False, None, data.limit, data.orig_now)

    def sync_after_set_not_contains(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .set_not_contains operation
        in another worker process.
        """
        self.impl.set_not_contains(data.key, data.value, data.expiry, False, None, data.limit, data.orig_now)

    def sync_after_set_contains_all(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .set_contains_all operation
        in another worker process.
        """
        self.impl.set_contains_all(data.key, data.value, data.expiry, False, None, data.limit, data.orig_now)

    def sync_after_set_contains_any(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .set_contains_any operation
        in another worker process.
        """
        self.impl.set_contains_any(data.key, data.value, data.expiry, False, None, data.limit, data.orig_now)

# ################################################################################################################################

    def sync_after_delete(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .delete operation in another worker process.
        """
        self.impl.delete(data.key)

    def sync_after_delete_by_prefix(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .delete_by_prefix operation
        in another worker process.
        """
        self.impl.delete_by_prefix(data.key, False, data.limit)

    def sync_after_delete_by_suffix(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .delete_by_suffix operation
        in another worker process.
        """
        self.impl.delete_by_suffix(data.key, False, data.limit)

    def sync_after_delete_by_regex(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .delete_by_regex operation
        in another worker process.
        """
        self.impl.delete_by_regex(data.key, False, data.limit)

    def sync_after_delete_contains(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .delete_contains operation
        in another worker process.
        """
        self.impl.delete_contains(data.key, False, data.limit)

    def sync_after_delete_not_contains(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .delete_not_contains operation
        in another worker process.
        """
        self.impl.delete_not_contains(data.key, False, data.limit)

    def sync_after_delete_contains_all(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .delete_contains_all operation
        in another worker process.
        """
        self.impl.delete_contains_all(data.key, False, data.limit)

    def sync_after_delete_contains_any(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .delete_contains_any operation
        in another worker process.
        """
        self.impl.delete_contains_any(data.key, False, data.limit)

# ################################################################################################################################

    def sync_after_expire(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after an .expire operation in another worker process.
        """
        self.impl.set_expiration_data(data.key, data.expiry, data.expires_at)

    def sync_after_expire_by_prefix(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .expire_by_prefix operation
        in another worker process.
        """
        self.impl.expire_by_prefix(data.key, data.expiry, data.limit)

    def sync_after_expire_by_suffix(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .expire_by_suffix operation
        in another worker process.
        """
        self.impl.expire_by_suffix(data.key, data.expiry, data.limit)

    def sync_after_expire_by_regex(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .expire_by_regex operation
        in another worker process.
        """
        self.impl.expire_by_regex(data.key, data.expiry, data.limit)

    def sync_after_expire_contains(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .expire_contains operation
        in another worker process.
        """
        self.impl.expire_contains(data.key, data.expiry, data.limit)

    def sync_after_expire_not_contains(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .expire_not_contains operation
        in another worker process.
        """
        self.impl.expire_not_contains(data.key, data.expiry, data.limit)

    def sync_after_expire_contains_all(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .expire_contains_all operation
        in another worker process.
        """
        self.impl.expire_contains_all(data.key, data.expiry, data.limit)

    def sync_after_expire_contains_any(self, data):
        """ Invoked by Cache API to synchronizes this worker's cache after a .expire_contains_any operation
        in another worker process.
        """
        self.impl.expire_contains_any(data.key, data.expiry, data.limit)

# ################################################################################################################################

    def sync_after_clear(self):
        """ Invoked by Cache API to synchronizes this worker's cache after a .clear operation in another worker process.
        """
        self.impl.clear()

# ################################################################################################################################

class _NotConfiguredAPI:
    def set(self, *args, **kwargs):
        logger.warn('Default cache is not configured')
    get = set

# ################################################################################################################################

class CacheAPI:
    """ Base class for all cache objects.
    """
    def __init__(self, server):
        self.server = server
        self.lock = RLock()
        self.default = cast_('Cache', _NotConfiguredAPI())
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

    def after_state_changed(self, op, cache_name, data, _broker_msg=builtin_op_to_broker_msg, _pickle_dumps=pickle_dumps):
        """ Callback method invoked by each cache if it requires synchronization with other worker processes.
        """
        try:

            data['action'] = _broker_msg[op]
            data['cache_name'] = cache_name
            data['source_worker_id'] = self.server.worker_id

            key = data.get('key', _no_key)
            value = data.get('value', _no_value)

            if isinstance(key, basestring):
                data['is_key_pickled'] = False
            else:
                data['is_key_pickled'] = True
                data['key'] = _pickle_dumps(key)

            if value:
                if isinstance(value, basestring):
                    data['is_value_pickled'] = False
                else:
                    data['is_value_pickled'] = True
                    value = _pickle_dumps(value)
                    value = b64encode(value)
                    value = value.decode('utf8')
                    data['value'] = value
            else:
                data['is_value_pickled'] = False

            self.server.broker_client.publish(data)
        except Exception:
            logger.warning('Could not run `%s` after_state_changed in cache `%s`, data:`%s`, e:`%s`',
                op, cache_name, data, format_exc())

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
            except Exception:
                logger.warning(format_exc())

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
        if config.cache_type == CACHE.TYPE.BUILTIN:
            cache = self.caches[config.cache_type].pop(config.old_name)
            cache.update_config(config)
            self._add_cache(config, cache)
        else:
            cache = self.caches[config.cache_type][config.old_name]
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
#
# ################################################################################################################################

    def _get_cache(self, cache_type:'str', name:'str') -> 'Cache':
        """ Actually returns a cache. Must be called with self.lock held.
        """
        return self.caches[cache_type][name]

# ################################################################################################################################

    def get_cache(self, cache_type:'str', name:'str') -> 'Cache':
        """ Returns the lower-level cache implementation object by its type and name.
        """
        with self.lock:
            return self.caches[cache_type][name]

# ################################################################################################################################

    def get_builtin_cache(self, name):
        """ Returns a built-in cache by its name.
        """
        with self.lock:
            return self._get_cache(CACHE.TYPE.BUILTIN, name)

# ################################################################################################################################

    def get_memcached_cache(self, name):
        """ Returns a Memcached cache by its name.
        """
        with self.lock:
            return self._get_cache(CACHE.TYPE.MEMCACHED, name)

# ################################################################################################################################

    def get_size(self, cache_type, name):
        """ Returns current size, the number of entries, in a given cache.
        """
        return len(self.caches[cache_type][name])

# ################################################################################################################################

    def sync_after_set(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .set operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_set(data)

    def sync_after_set_by_prefix(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .set_by_prefix operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_set_by_prefix(data)

    def sync_after_set_by_suffix(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .set_by_suffix operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_set_by_suffix(data)

    def sync_after_set_by_regex(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .set_by_regex operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_set_by_regex(data)

    def sync_after_set_contains(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .set_contains operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_set_contains(data)

    def sync_after_set_not_contains(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .set_not_contains operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_set_not_contains(data)

    def sync_after_set_contains_all(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .set_contains_all operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_set_contains_all(data)

    def sync_after_set_contains_any(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .set_contains_any operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_set_contains_any(data)

# ################################################################################################################################

    def sync_after_delete(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .delete operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_delete(data)

    def sync_after_delete_by_prefix(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .delete_by_prefix operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_delete_by_prefix(data)

    def sync_after_delete_by_suffix(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .delete_by_suffix operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_delete_by_suffix(data)

    def sync_after_delete_by_regex(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .delete_by_regex operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_delete_by_regex(data)

    def sync_after_delete_contains(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .delete_contains operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_delete_contains(data)

    def sync_after_delete_not_contains(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .delete_not_contains operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_delete_not_contains(data)

    def sync_after_delete_contains_all(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .delete_contains_all operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_delete_contains_all(data)

    def sync_after_delete_contains_any(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .delete_contains_any operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_delete_contains_any(data)

# ################################################################################################################################

    def sync_after_expire(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after an .expire operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_expire(data)

    def sync_after_expire_by_prefix(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .expire_by_prefix operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_expire_by_prefix(data)

    def sync_after_expire_by_suffix(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .expire_by_suffix operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_expire_by_suffix(data)

    def sync_after_expire_by_regex(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .expire_by_regex operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_expire_by_regex(data)

    def sync_after_expire_contains(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .expire_contains operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_expire_contains(data)

    def sync_after_expire_not_contains(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .expire_not_contains operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_expire_not_contains(data)

    def sync_after_expire_contains_all(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .expire_contains_all operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_expire_contains_all(data)

    def sync_after_expire_contains_any(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .expire_contains_any operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_expire_contains_any(data)

# ################################################################################################################################

    def sync_after_clear(self, cache_type, data):
        """ Synchronizes the state of this worker's cache after a .clear operation in another worker process.
        """
        self.caches[cache_type][data.cache_name].sync_after_clear()

# ################################################################################################################################
