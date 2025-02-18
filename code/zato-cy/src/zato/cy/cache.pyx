# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import inspect
from base64 import b64decode
from datetime import datetime
from decimal import Decimal
from email.utils import formatdate as stdlib_format_date
from hashlib import sha256
from json import dumps as json_dumps, JSONEncoder
from logging import getLogger
from sys import getsizeof
from time import time

# Arrow
from arrow import Arrow

# Cython
from cpython.list cimport PyList_SetSlice
from cpython.object cimport Py_EQ, PyObject, PyObject_RichCompareBool
from cpython.sequence cimport PySequence_ITEM
from libc.stdint cimport uint64_t

# gevent
from gevent.lock import RLock

# regex
from regex import compile as re_compile

# Python 2/3 compatibility
from builtins import bytes
from six import binary_type, integer_types, string_types, text_type
from zato.common.py23_ import maxint

# Zato
from zato.common.api import CACHE as _COMMON_CACHE

# ################################################################################################################################

logger = getLogger('zato.cache')

# ################################################################################################################################

str_types = string_types + (text_type,)
len_values = (binary_type,) + str_types
key_types = len_values + integer_types

# ################################################################################################################################

class CACHE:
    DEFAULT_SIZE = _COMMON_CACHE.DEFAULT.MAX_SIZE
    MAX_ITEM_SIZE = _COMMON_CACHE.DEFAULT.MAX_ITEM_SIZE

# ################################################################################################################################

class KeyExpiredError(KeyError):
    """ Indicates that an operation would have succeeded had this key not expired before.
    """

# ################################################################################################################################

class _JSONEncoder(JSONEncoder):
    def default(self, elem):
        if isinstance(elem, (datetime, Arrow)):
            return elem.isoformat()
        else:
            return str(elem)

# ################################################################################################################################

cdef class Entry:
    """ Represents an individual value stored in a cache.
    """
    cdef:

        # The actual key and  contents
        public object key
        public object value

        # When was the value last read
        public double last_read

        # When was the value previously read
        public double prev_read

        # When was the value last written to (creation or update)
        public double last_write

        # When was the value previously written to (creation or update)
        public double prev_write

        # Expiration in seconds
        public double expiry

        # When will the key expire - computed when the entry is created or updated
        public double expires_at

        # How many times was this key returned
        public uint64_t hits

        # This entry's position in index
        public long position

        # Hashed in SHA256
        public str hash

        # Non-float timestamps
        public object last_read_iso
        public object prev_read_iso
        public object last_write_iso
        public object prev_write_iso

        public object last_read_http
        public object prev_read_http
        public object last_write_http
        public object prev_write_http

    cpdef dict to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'hash': self.hash,

            'expiry': self.expiry,
            'expires_at': self.expires_at,

            'hits': self.hits,
            'position': self.position,

            'last_read': self.last_read,
            'prev_read': self.prev_read,
            'last_write': self.last_write,
            'prev_write': self.prev_write,

            'last_read_iso': self.last_read_iso,
            'prev_read_iso': self.prev_read_iso,
            'last_write_iso': self.last_write_iso,
            'prev_write_iso': self.prev_write_iso,

            'last_read_http': self.last_read_http,
            'prev_read_http': self.prev_read_http,
            'last_write_http': self.last_write_http,
            'prev_write_http': self.prev_write_http,

        }

    cpdef set_metadata(self, bint log_details=False):
        """ Configures metadata after set* operations.
        """
        # Will contain the computed hash value
        h = sha256()

        # Make sure that we hash a canonical representation of the object,
        # e.g. if it is a dictionary then we want to hash the same representation
        # of this dictionary no matter in which order internally the keys are stored
        # seeing as from our perspective there is no intrinsic order.
        if isinstance(self.value, str_types):
            value = self.value
        else:
            value = json_dumps(self.value, sort_keys=True, cls=_JSONEncoder)
        value = value if isinstance(value, bytes) else value.encode('utf8')

        h.update(value)
        self.hash = str(h.hexdigest())

        # Timestamps in formats other than seconds since epoch

        if self.last_read:
            self.last_read_iso = datetime.fromtimestamp(self.last_read).isoformat()
            self.last_read_http = stdlib_format_date(self.last_read, usegmt=True)

        if self.prev_read:
            self.prev_read_iso = datetime.fromtimestamp(self.prev_read).isoformat()
            self.prev_read_http = stdlib_format_date(self.prev_read, usegmt=True)

        if self.prev_write:
            self.prev_write_iso = datetime.fromtimestamp(self.prev_write).isoformat()
            self.prev_write_http = stdlib_format_date(self.prev_write, usegmt=True)

        # This is always available because it is set during the initial write
        self.last_write_iso = datetime.fromtimestamp(self.last_write).isoformat()
        self.last_write_http = stdlib_format_date(self.last_write, usegmt=True)

        if log_details:
            logger.info('Set metadata %s', self.to_dict())

# ################################################################################################################################

cdef class Cache:
    """ An LRU cache that optionally rejects entries bigger than N bytes. Entries can have a TTL assigned - periodic processes
    will clean up entries older than allowed.
    """
    cdef:
        public long max_size
        public long max_item_size
        public bint has_max_item_size
        public bint extend_expiry_on_get
        public bint extend_expiry_on_set
        public dict _data
        public list _index
        public uint64_t misses
        public uint64_t hits
        public uint64_t set_ops
        public uint64_t get_ops
        public dict hits_per_position # How many times a given position in cache was used
        public list _expired_on_op    # Keys that were found to have expired during a .get or .set operation
        public object _lock
        public object default_get # A singleton indicating that no default value was given for self.get
        public dict _regex_cache

    def __cinit__(self):
        self._data = {}
        self._index = []
        self.hits_per_position = {}
        self._expired_on_op = []
        self.hits = 0
        self.misses = 0
        self.set_ops = 0
        self.get_ops = 0
        self._regex_cache = {}

    def __init__(self, max_size=None, max_item_size=None, extend_expiry_on_get=True, extend_expiry_on_set=True, lock=None):
        self._lock = lock or RLock()
        self.default_get = object()
        with self._lock:
            self._update_config(max_size, max_item_size, extend_expiry_on_get, extend_expiry_on_set)

    def _update_config(self, max_size, max_item_size, extend_expiry_on_get, extend_expiry_on_set):
        self.max_size = max_size or CACHE.DEFAULT_SIZE
        self.max_item_size = max_item_size or CACHE.MAX_ITEM_SIZE
        self.has_max_item_size = self.max_item_size > 0
        self.extend_expiry_on_get = extend_expiry_on_get
        self.extend_expiry_on_set = extend_expiry_on_set
        self.hits_per_position.update(dict((key, 0) for key in xrange(self.max_size)))

    def update_config(self, config):
        with self._lock:
            self._update_config(config.max_size, config.max_item_size, config.extend_expiry_on_get, config.extend_expiry_on_set)

# ################################################################################################################################

    def __repr__(self):
        with self._lock:
            hits_to_misses = (round(1.0 * self.hits / self.misses, 1)) if self.misses else 'n/a'
            hits_to_misses = ' ({})'.format(hits_to_misses)

            get_to_set_ops = (round(1.0 * self.get_ops / self.set_ops, 1)) if self.set_ops and self.get_ops else 'n/a'
            get_to_set_ops = ' ({})'.format(get_to_set_ops)

            return '<{} at {}, size:{}/{} hits/misses:{}/{}{}, get/set:{}/{}{}, max_item_size:{}>'.format(
                self.__class__.__name__, hex(id(self)), len(self._data), self.max_size,
                self.hits, self.misses, hits_to_misses,
                self.get_ops, self.set_ops, get_to_set_ops,
                self.max_item_size
            )

# ################################################################################################################################

    def __contains__(self, object key):
        with self._lock:
            return key in self._data

# ################################################################################################################################

    def __len__(self):
        with self._lock:
            return len(self._index)

# ################################################################################################################################

    cpdef list keys(self):
        with self._lock:
            return self._data.keys()

# ################################################################################################################################

    cpdef object iterkeys(self):
        with self._lock:
            return self._data.iterkeys()

# ################################################################################################################################

    cpdef list keys_by_position(self):
        with self._lock:
            return list(self._index)

# ################################################################################################################################

    cpdef list values(self):
        with self._lock:
            return self._data.values()

# ################################################################################################################################

    cpdef object itervalues(self):
        with self._lock:
            return self._data.itervalues()

# ################################################################################################################################

    cpdef list items(self):
        with self._lock:
            return self._data.items()

# ################################################################################################################################

    cpdef object iteritems(self):
        with self._lock:
            return self._data.iteritems()

# ################################################################################################################################

    def get_slice(self, start, stop, step):
        with self._lock:
            for key in self._index[start:stop:step]:
                entry = self._data[key]
                as_dict = entry.to_dict()
                as_dict['position'] = self._get_index(key)
                yield as_dict

# ################################################################################################################################

    cpdef list clear(self):
        """ Clears the cache - removes all entries and associated metadata.
        """
        # The attributes cleared below must be kept in sync with the ones from __cinit__.
        with self._lock:
            self._data.clear()
            self._index[:] = []
            self.hits_per_position.clear()
            self._expired_on_op[:] = []
            self.hits = 0
            self.misses = 0
            self.set_ops = 0
            self.get_ops = 0

# ################################################################################################################################

    cdef object _delete(self, object key):
        cdef object out
        cdef Entry entry = self._data.get(key)

        if not entry:
            return
        else:
            # We run under self.lock so at this point we know that the key was valid
            # and _remove_from_index_by_idx is safe to call.
            out = entry.value
            del self._data[key]
            self._remove_from_index_by_idx(self._get_index(key))

            return out

# ################################################################################################################################

    cpdef object delete(self, object key):
        with self._lock:
            return self._delete(key)

    __del__ = delete

# ################################################################################################################################

    cpdef dict delete_by_prefix(self, object data, bint return_found, int limit):
        """ Deletes keys matching the input prefix. Non-string-like keys are ignored. Optionally, returns a dict of keys
        that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef object key
        cdef dict out = {}
        cdef object value = None
        cdef list to_delete = []

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if key.startswith(data):
                    if return_found:
                        out[key] = <Entry>self._data[key].value
                    to_delete.append(key)
                if idx == limit:
                    break

        # We could not do in the loop above because that would have changed self._data
        # and result in 'RuntimeError: dictionary changed size during iteration'.
        for key in to_delete:
            self._delete(key)

        return out

# ################################################################################################################################

    cpdef dict delete_by_suffix(self, object data, bint return_found, int limit):
        """ Deletes keys matching the input suffix. Non-string-like keys are ignored. Optionally, returns a dict of keys
        that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef object key
        cdef dict out = {}
        cdef object value = None
        cdef list to_delete = []

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if key.endswith(data):
                    if return_found:
                        out[key] = <Entry>self._data[key].value
                    to_delete.append(key)
                if idx == limit:
                    break

        # We could not do in the loop above because that would have changed self._data
        # and result in 'RuntimeError: dictionary changed size during iteration'.
        for key in to_delete:
            self._delete(key)

        return out

# ################################################################################################################################

    cpdef dict delete_by_regex(self, object data, bint return_found, int limit):
        """ Deletes keys matching the input regex pattern. Non-string-like keys are ignored. Optionally, returns a dict of keys
        that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef object regex = self._regex_cache.setdefault(data, re_compile(data))
        cdef object key
        cdef dict out = {}
        cdef object value = None
        cdef list to_delete = []

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if regex.match(key):
                    if return_found:
                        out[key] = <Entry>self._data[key].value
                    to_delete.append(key)
                if idx == limit:
                    break

        # We could not do in the loop above because that would have changed self._data
        # and result in 'RuntimeError: dictionary changed size during iteration'.
        for key in to_delete:
            self._delete(key)

        return out

# ################################################################################################################################

    cpdef dict delete_contains(self, object data, bint return_found, int limit):
        """ Deletes keys containing the input pattern. Non-string-like keys are ignored. Optionally, returns a dict of keys
        that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef object key
        cdef dict out = {}
        cdef object value = None
        cdef list to_delete = []

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if data in key:
                    if return_found:
                        out[key] = <Entry>self._data[key].value
                    to_delete.append(key)
                if idx == limit:
                    break

        # We could not do in the loop above because that would have changed self._data
        # and result in 'RuntimeError: dictionary changed size during iteration'.
        for key in to_delete:
            self._delete(key)

        return out

# ################################################################################################################################

    cpdef dict delete_not_contains(self, object data, bint return_found, int limit):
        """ Deletes keys that don't contain the input pattern. Non-string-like keys are ignored. Optionally,
        returns a dict of keys that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef object key
        cdef dict out = {}
        cdef object value = None
        cdef list to_delete = []

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if data not in key:
                    if return_found:
                        out[key] = <Entry>self._data[key].value
                    to_delete.append(key)
                if idx == limit:
                    break

        # We could not do in the loop above because that would have changed self._data
        # and result in 'RuntimeError: dictionary changed size during iteration'.
        for key in to_delete:
            self._delete(key)

        return out

# ################################################################################################################################

    cpdef dict delete_contains_all(self, object data, bint return_found, int limit):
        """ Deletes keys that contain all the elements from the input list of patterns. Non-string-like keys are ignored.
        Optionally, returns a dict of keys that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef object key
        cdef dict out = {}
        cdef object value = None
        cdef list to_delete = []
        cdef bint add_key

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue

                use_key = True
                for elem in data:
                    if elem not in key:
                        use_key = False
                        break

                if use_key:
                    if return_found:
                        out[key] = <Entry>self._data[key].value
                    to_delete.append(key)

                if idx == limit:
                    break

        # We could not do in the loop above because that would have changed self._data
        # and result in 'RuntimeError: dictionary changed size during iteration'.
        for key in to_delete:
            self._delete(key)

        return out

# ################################################################################################################################

    cpdef dict delete_contains_any(self, object data, bint return_found, int limit):
        """ Deletes keys that contain at least one of the elements from the input list of patterns.
        Non-string-like keys are ignored. Optionally, returns a dict of keys that matched the input criteria
        along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef object key
        cdef dict out = {}
        cdef object value = None
        cdef list to_delete = []
        cdef bint use_key

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue

                use_key = False
                for elem in data:
                    if elem in key:
                        use_key = True
                        break

                if use_key:
                    if return_found:
                        out[key] = <Entry>self._data[key].value
                    to_delete.append(key)

                if idx == limit:
                    break

        # We could not do in the loop above because that would have changed self._data
        # and result in 'RuntimeError: dictionary changed size during iteration'.
        for key in to_delete:
            self._delete(key)

        return out

# ################################################################################################################################

    cdef inline long _get_index(self, object key):
        """ C-only version of self.get_position that will always return a long - must be called only
        if key is known to be in self._index or self._data and only with self._lock held.
        """
        cdef Py_ssize_t index_idx = 0
        cdef Py_ssize_t cache_size = len(self._index)
        cdef bint index_key_eq

        while index_idx < cache_size:
            if PyObject_RichCompareBool(PySequence_ITEM(self._index, index_idx), <object>key, Py_EQ):
                return index_idx
            index_idx += 1

# ################################################################################################################################

    cpdef object index(self, object key):
        """ Returns position the key given on input currently holds or None if key is not found.
        """
        with self._lock:
            if key in self._data:
                return self._get_index(key)

# ################################################################################################################################

    cdef inline object _remove_from_index_by_idx(self, long idx):
        """ Remove object from from index by its position - this is what listremove in Objects/listobject.c does
        and we use the same technique because there is no public PyList_Remove function. Returns the removed key.
        """
        cdef object index_key = PySequence_ITEM(self._index, idx)
        PyList_SetSlice(self._index, idx, idx+1, <object>NULL)

        return index_key

# ################################################################################################################################

    cdef inline double _get_timestamp(self):
        return time()

# ################################################################################################################################

    cpdef double get_timestamp(self):
        return self._get_timestamp()

# ################################################################################################################################

    cdef object _set(self, object key, value, expiry, bint details, dict meta_ref, object orig_now=None,
        _getsizeof=getsizeof, _key_types=key_types, _len_values=len_values):

        cdef object out = None
        cdef Entry entry
        cdef double _now
        cdef double _orig_now = 0.0
        cdef Py_ssize_t cache_size = len(self._index)
        cdef Py_ssize_t index_idx
        cdef bint old_key_eq
        cdef long hits_per_position
        cdef long len_value

        # If multiple processes synchronize contents of their caches, the one that originally added the keys
        # will dictate what the actual, original key addition timestamp was. Otherwise, we are this first
        # process so we generate the timestamp ourselves.
        if orig_now:
            _now = orig_now
        else:
            _orig_now = _now = self._get_timestamp()

        if not isinstance(key, _key_types):
            raise ValueError('Key must be an instance of one of {}'.format(key_types))

        if self.has_max_item_size:
            if isinstance(value, _len_values):
                len_value = len(value)
                if len_value > self.max_item_size:
                    raise ValueError('Value too long {} > {}'.format(len_value, self.max_item_size))

        # Update total # of .set operations
        self.set_ops += 1

        # Ok, we have this key in cache
        if key in self._data:
            entry = <Entry>self._data[key]

            # If we have a key that previously was not using expiry, we must set it now if expiry is given on input.
            if not entry.expires_at:
                if expiry:
                    entry.expiry = expiry
                    entry.expires_at = _now + expiry
            else:
                # Mark as deleted an entry that has already expired
                if _now >= entry.expires_at:
                    self._delete(key)
                    self._expired_on_op.append(key)
                    raise KeyExpiredError(key)
                else:
                    # If expiry == 0.0 it means that we are resetting an already existing expiry time
                    if expiry == 0.0:
                        entry.expires_at = 0.0
                        entry.expiry = 0.0
                    else:
                        # The entry exists and has not expired so now, if we are configured to, prolong its expiration time
                        if self.extend_expiry_on_set and entry.expiry:
                            entry.expires_at = _now + entry.expiry

            # Update access information for that entry, if we get to this point, the entry is not expired,
            # or at least its expiry time has been extended.
            entry.prev_write = entry.last_write
            entry.last_write = _now
            out = entry.value
            entry.value = value
            entry.set_metadata()

        # No such key in cache - let's add it.
        else:

            # Make sure there is room for the new key
            if cache_size == self.max_size:
                del self._data[self._index.pop()]

            # Actually insert entry
            entry = Entry()
            entry.key = key
            entry.value = value
            entry.last_read = 0.0
            entry.prev_read = 0.0
            entry.last_write = _now
            entry.prev_write = 0.0
            entry.hits = 0
            entry.expiry = expiry
            entry.expires_at = 0.0 if not expiry else _now + expiry
            entry.set_metadata()

            self._data[key] = entry
            self._index.insert(0, key)

        # If any output dict for metadata was passed in by reference, set its requires items.
        if meta_ref is not None:
            meta_ref['expires_at'] = entry.expires_at
            meta_ref['orig_now'] = _orig_now

        return entry if details else out

# ################################################################################################################################

    cpdef object set(self, object key, value, double expiry, bint details, dict meta_ref=None, object orig_now=None):
        with self._lock:
            return self._set(key, value, expiry, details, meta_ref, orig_now)

# ################################################################################################################################

    cpdef dict set_by_prefix(self, object data, value, double expiry, bint details, dict meta_ref, bint return_found,
        int limit, object orig_now=None):
        """ Sets a given value for all keys matching the input prefix. Non-string-like keys are ignored. Optionally,
        returns a dict of keys that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}
        cdef Entry entry
        cdef bint _needs_any_found_report = True if meta_ref else False
        cdef double _now = orig_now if orig_now else self._get_timestamp()

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if key.startswith(data):

                    # Set it before the update which would overwrite it, this is why we can return
                    # value alone, without any metadata.
                    if return_found:
                        entry = <Entry>self._data[key]
                        out[key] = entry if details else entry.value

                    self._set(key, value, expiry, False, None, _now)

                    # Indicate to our caller that there was at least one matching key
                    if _needs_any_found_report:
                        meta_ref['_any_found'] = True
                        _needs_any_found_report = False

                # Our caller knows how many keys to look up at most
                if idx == limit:
                    break

        if meta_ref:
            meta_ref['_now'] = _now

        return out

# ################################################################################################################################

    cpdef dict set_by_suffix(self, object data, value, double expiry, bint details, dict meta_ref, bint return_found,
        int limit, object orig_now=None):
        """ Sets a given value for all keys matching the input suffix. Non-string-like keys are ignored. Optionally,
        returns a dict of keys that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}
        cdef Entry entry
        cdef bint _needs_any_found_report = True if meta_ref else False
        cdef double _now = orig_now if orig_now else self._get_timestamp()

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):

                if not isinstance(key, str_types):
                    continue

                if key.endswith(data):

                    # Set it before the update which would overwrite it, this is why we can return
                    # value alone, without any metadata.
                    if return_found:
                        entry = <Entry>self._data[key]
                        out[key] = entry if details else entry.value

                    self._set(key, value, expiry, False, None, _now)

                    # Indicate to our caller that there was at least one matching key
                    if _needs_any_found_report:
                        meta_ref['_any_found'] = True
                        _needs_any_found_report = False

                # Our caller knows how many keys to look up at most
                if idx == limit:
                    break

        if meta_ref:
            meta_ref['_now'] = _now

        return out

# ################################################################################################################################

    cpdef dict set_by_regex(self, object data, value, double expiry, bint details, dict meta_ref, bint return_found,
        int limit, object orig_now=None):
        """ Sets a given value for all keys matching the input regex pattern. Non-string-like keys are ignored.
        Optionally, returns a dict of keys that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}
        cdef Entry entry
        cdef object regex = self._regex_cache.setdefault(data, re_compile(data))
        cdef bint _needs_any_found_report = True if meta_ref else False
        cdef double _now = orig_now if orig_now else self._get_timestamp()

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):

                if not isinstance(key, str_types):
                    continue

                if regex.match(key):

                    # Set it before the update which would overwrite it, this is why we can return
                    # value alone, without any metadata.
                    if return_found:
                        entry = <Entry>self._data[key]
                        out[key] = entry if details else entry.value

                    self._set(key, value, expiry, False, None, _now)

                    # Indicate to our caller that there was at least one matching key
                    if _needs_any_found_report:
                        meta_ref['_any_found'] = True
                        _needs_any_found_report = False

                # Our caller knows how many keys to look up at most
                if idx == limit:
                    break

        if meta_ref:
            meta_ref['_now'] = _now

        return out

# ################################################################################################################################

    cpdef dict set_contains(self, object data, value, double expiry, bint details, dict meta_ref, bint return_found,
        int limit, object orig_now=None):
        """ Sets a given value for all keys if the key contains the input pattern. Non-string-like keys are ignored.
        Optionally, returns a dict of keys that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}
        cdef Entry entry
        cdef bint _needs_any_found_report = True if meta_ref else False
        cdef double _now = orig_now if orig_now else self._get_timestamp()

        with self._lock:

            for idx, key in enumerate(self._data.iterkeys(), 1):

                if not isinstance(key, str_types):
                    continue

                if data in key:

                    # Set it before the update which would overwrite it, this is why we can return
                    # value alone, without any metadata.
                    if return_found:
                        entry = <Entry>self._data[key]
                        out[key] = entry if details else entry.value

                    self._set(key, value, expiry, False, None, _now)

                    # Indicate to our caller that there was at least one matching key
                    if _needs_any_found_report:
                        meta_ref['_any_found'] = True
                        _needs_any_found_report = False

                # Our caller knows how many keys to look up at most
                if idx == limit:
                    break

        if meta_ref:
            meta_ref['_now'] = _now

        return out

# ################################################################################################################################

    cpdef dict set_not_contains(self, object data, value, double expiry, bint details, dict meta_ref, bint return_found,
        int limit, object orig_now=None):
        """ Sets a given value for all keys if the key doesn't contain the input pattern. Non-string-like keys are ignored.
        Optionally, returns a dict of keys that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}
        cdef Entry entry
        cdef bint _needs_any_found_report = True if meta_ref else False
        cdef double _now = orig_now if orig_now else self._get_timestamp()

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):

                if not isinstance(key, str_types):
                    continue

                if data not in key:

                    # Set it before the update which would overwrite it, this is why we can return
                    # value alone, without any metadata.
                    if return_found:
                        entry = <Entry>self._data[key]
                        out[key] = entry if details else entry.value

                    self._set(key, value, expiry, False, None, _now)

                    # Indicate to our caller that there was at least one matching key
                    if _needs_any_found_report:
                        meta_ref['_any_found'] = True
                        _needs_any_found_report = False

                # Our caller knows how many keys to look up at most
                if idx == limit:
                    break

        return out

# ################################################################################################################################

    cpdef dict set_contains_all(self, list data, value, double expiry, bint details, dict meta_ref, bint return_found,
        int limit, object orig_now=None):
        """ Sets a given value for all keys if the key contains all of input substrings. Non-string-like keys are ignored.
        Optionally, returns a dict of keys that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}
        cdef Entry entry
        cdef bint use_key
        cdef bint _needs_any_found_report = True if meta_ref else False
        cdef double _now = orig_now if orig_now else self._get_timestamp()

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):

                if not isinstance(key, str_types):
                    continue

                use_key = True
                for elem in data:
                    if elem not in key:
                        use_key = False
                        break

                if use_key:

                    # Set it before the update which would overwrite it, this is why we can return
                    # value alone, without any metadata.
                    if return_found:
                        entry = <Entry>self._data[key]
                        out[key] = entry if details else entry.value

                    self._set(key, value, expiry, False, None, _now)

                    # Indicate to our caller that there was at least one matching key
                    if _needs_any_found_report:
                        meta_ref['_any_found'] = True
                        _needs_any_found_report = False

                # Our caller knows how many keys to look up at most
                if idx == limit:
                    break

        if meta_ref:
            meta_ref['_now'] = _now

        return out

# ################################################################################################################################

    cpdef dict set_contains_any(self, list data, value, double expiry, bint details, dict meta_ref, bint return_found,
        int limit, object orig_now=None):
        """ Sets a given value for all keys if the key contains any of input substrings. Non-string-like keys are ignored.
        Optionally, returns a dict of keys that matched the input criteria along with their previous values.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}
        cdef Entry entry
        cdef bint use_key
        cdef bint _needs_any_found_report = True if meta_ref else False
        cdef double _now = orig_now if orig_now else self._get_timestamp()

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):

                if not isinstance(key, str_types):
                    continue

                use_key = False
                for elem in data:
                    if elem in key:
                        use_key = True
                        break

                if use_key:

                    # Set it before the update which would overwrite it, this is why we can return
                    # value alone, without any metadata.
                    if return_found:
                        entry = <Entry>self._data[key]
                        out[key] = entry if details else entry.value

                    self._set(key, value, expiry, False, None, _now)

                    # Indicate to our caller that there was at least one matching key
                    if _needs_any_found_report:
                        meta_ref['_any_found'] = True
                        _needs_any_found_report = False

                # Our caller knows how many keys to look up at most
                if idx == limit:
                    break

        if meta_ref:
            meta_ref['_now'] = _now

        return out

# ################################################################################################################################

    cdef object _get(self, object key, object default, bint details):
        """ Returns data for key in cache if present. Otherwise returns None. If 'details' is True,
        returns a dictionary with value and metadata instead of value alone.
        """
        cdef object _item
        cdef Entry entry
        cdef Py_ssize_t index_idx
        cdef Py_ssize_t cache_size
        cdef object index_key
        cdef double _now = self._get_timestamp()

        try:
            entry = <Entry>self._data[key]
        except KeyError:
            # Add information that there was a cache miss
            self.misses += 1

            # Return the default value, if any was given.
            if default is self.default_get:
                return None
            else:
                return default
        else:

            # We have the key but we must first ensure that it's not expired already
            if entry.expires_at and _now >= entry.expires_at:
                self._delete(key)
                self._expired_on_op.append(key)
                raise KeyExpiredError(key)

            # Update total # of .get operations
            self.get_ops += 1

            # Update total hits counter
            self.hits += 1

            # Current position of that key in index
            index_idx = self._get_index(key)

            # We have the key's position so we can now update per-position counter
            # to be able to offer statistics on how often a key is found at a given position.
            hits_per_position = <object>self.hits_per_position[index_idx]
            hits_per_position += 1
            self.hits_per_position[index_idx] = hits_per_position

            # Remove key from index
            index_key = self._remove_from_index_by_idx(index_idx)

            # Now insert the key back at the head position.
            self._index.insert(0, index_key)

            # Update last/prev access information + hits
            entry.prev_read = entry.last_read
            entry.last_read = _now
            entry.hits += 1

            # The entry exists and has not expired so now, if we are configured to, prolong its expiration time
            if self.extend_expiry_on_get and entry.expiry:
                entry.expires_at = _now + entry.expiry

            # If details are requested, add current position of key to data returned
            if details:
                entry.key = key
                entry.position = index_idx
                return entry

            # Without details, simply return value stored for key
            else:
                return entry.value

# ################################################################################################################################

    cpdef get(self, object key, object default, bint details):
        """ Returns a value by key, or None if the value is not found.
        """
        with self._lock:
            return self._get(key, default, details)

# ################################################################################################################################

    cpdef object get_by_prefix(self, object data, bint details, int limit):
        """ Returns all key:value mappings for keys matching a given prefix, or an empty dictionary
        if none of key matches. Non-string-like keys are ignored. Similarly to other self.get/set/expire/delete methods,
        it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if key.startswith(data):
                    out[key] = self._get(key, self.default_get, details)
                if idx == limit:
                    break

        return out

# ################################################################################################################################

    cpdef object get_by_suffix(self, object data, bint details, int limit):
        """ Returns all key:value mappings for keys matching a given regex pattern, or an empty dictionary
        if none of key matches. Non-string-like keys are ignored. Similarly to other self.get/set/expire/delete methods,
        it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if key.endswith(data):
                    out[key] = self._get(key, self.default_get, details)
                if idx == limit:
                    break

        return out

# ################################################################################################################################

    cpdef object get_by_regex(self, object data, bint details, int limit):
        """ Returns all key:value mappings for keys matching a given suffix, or an empty dictionary
        if none of key matches. Non-string-like keys are ignored. Similarly to other self.get/set/expire/delete methods,
        it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}
        cdef object regex = self._regex_cache.setdefault(data, re_compile(data))

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if regex.match(key):
                    out[key] = self._get(key, self.default_get, details)
                if idx == limit:
                    break

        return out


# ################################################################################################################################

    cpdef object get_contains(self, object data, bint details, int limit):
        """ Returns all key:value mappings for keys containing a given string, or an empty dictionary
        if none of key matches. Non-string-like keys are ignored. Similarly to other self.get/set/expire/delete methods,
        it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if data in key:
                    out[key] = self._get(key, self.default_get, details)
                if idx == limit:
                    break

        return out

# ################################################################################################################################

    cpdef object get_not_contains(self, object data, bint details, int limit):
        """ Returns all key:value mappings for keys that don't contain a given string, or an empty dictionary
        if none of key matches. Non-string-like keys are ignored. Similarly to other self.get/set/expire/delete methods,
        it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if data not in key:
                    out[key] = self._get(key, self.default_get, details)
                if idx == limit:
                    break

        return out

# ################################################################################################################################

    cpdef object get_contains_all(self, list data, bint details, int limit):
        """ Returns all key:value mappings for keys containing all elements from patterns, or an empty dictionary
        if none of key matches. Non-string-like keys are ignored. Similarly to other self.get/set/expire/delete methods,
        it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}
        cdef bint use_key

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):

                if not isinstance(key, str_types):
                    continue

                use_key = True
                for elem in data:
                    if elem not in key:
                        use_key = False
                        break

                if use_key:
                    out[key] = self._get(key, self.default_get, details)

                if idx == limit:
                    break

        return out

# ################################################################################################################################

    cpdef object get_contains_any(self, list data, bint details, int limit):
        """ Returns all key:value mappings for keys containing all elements from patterns, or an empty dictionary
        if none of key matches. Non-string-like keys are ignored. Similarly to other self.get/set/expire/delete methods,
        it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef dict out = {}
        cdef bint use_key

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):

                if not isinstance(key, str_types):
                    continue

                use_key = False
                for elem in data:
                    if elem in key:
                        use_key = True
                        break

                if use_key:
                    out[key] = self._get(key, self.default_get, details)

                if idx == limit:
                    break

        return out

# ################################################################################################################################

    cdef inline _expire(self, object key, double expiry, dict meta_ref):
        """ A low-level method to expire a key after 'expiry' seconds. Must be called with self._lock held.
        """
        self._set(key, self._get(key, self.default_get, False), expiry, False, meta_ref)

# ################################################################################################################################

    cpdef expire(self, object key, double expiry, dict meta_ref):
        """ Makes a given cache entry expire after 'expiry' seconds.
        """
        cdef bint found_key = False

        with self._lock:
            if key in self._data:
                self._expire(key, expiry, meta_ref)
                found_key = True

        return found_key

# ################################################################################################################################

    cdef bint expire_by_prefix(self, object data, double expiry, int limit):
        """ Sets expiration for all keys matching a given prefix. Non-string-like keys are ignored.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef bint found_any = False

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if key.startswith(data):
                    self._expire(key, expiry, None)
                    found_any = True
                if idx == limit:
                    break

        return found_any

# ################################################################################################################################

    cdef bint expire_by_suffix(self, object data, double expiry, int limit):
        """ Sets expiration for all keys matching a given suffix. Non-string-like keys are ignored.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef bint found_any = False

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if key.endswith(data):
                    self._expire(key, expiry, None)
                    found_any = True
                if idx == limit:
                    break

        return found_any

# ################################################################################################################################

    cdef bint expire_by_regex(self, object data, double expiry, int limit):
        """ Sets expiration for all keys matching a given regex pattern. Non-string-like keys are ignored.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef bint found_any = False
        cdef object regex = self._regex_cache.setdefault(data, re_compile(data))

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if regex.match(key):
                    self._expire(key, expiry, None)
                    found_any = True
                if idx == limit:
                    break

        return found_any

# ################################################################################################################################

    cdef bint expire_contains(self, object data, double expiry, int limit):
        """ Sets expiration for all keys containing a given pattern. Non-string-like keys are ignored.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef bint found_any = False

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if data in key:
                    self._expire(key, expiry, None)
                    found_any = True
                if idx == limit:
                    break

        return found_any

# ################################################################################################################################

    cdef bint expire_not_contains(self, object data, double expiry, int limit):
        """ Sets expiration for all keys containing a given pattern. Non-string-like keys are ignored.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef bint found_any = False

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue
                if data not in key:
                    self._expire(key, expiry, None)
                    found_any = True
                if idx == limit:
                    break

        return found_any

# ################################################################################################################################

    cdef bint expire_contains_all(self, object data, double expiry, int limit):
        """ Sets expiration for keys containing all of input elements. Non-string-like keys are ignored.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef bint found_any = False
        cdef bint use_key

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue

                use_key = True
                for elem in data:
                    if elem not in key:
                        use_key = False
                        break

                if use_key:
                    self._expire(key, expiry, None)
                    found_any = True

                if idx == limit:
                    break

        return found_any

# ################################################################################################################################

    cdef bint expire_contains_any(self, object data, double expiry, int limit):
        """ Sets expiration for keys containing at least one of input elements. Non-string-like keys are ignored.
        Similarly to other self.get/set/expire/delete methods, it's a separate one to reduce code branching/CPU mispredictions.
        """
        cdef bint found_any = False
        cdef bint use_key

        with self._lock:
            for idx, key in enumerate(self._data.iterkeys(), 1):
                if not isinstance(key, str_types):
                    continue

                use_key = False
                for elem in data:
                    if elem in key:
                        use_key = True
                        break

                if use_key:
                    self._expire(key, expiry, None)
                    found_any = True

                if idx == limit:
                    break

        return found_any

# ################################################################################################################################

    cpdef set_expiration_data(self, object key, double expiry, double expires_at):
        """ Sets expiry and expires_at attributes of a cache entry. Unlike self.expire,
        this method is not exposed to user API and is instead used in cache synchronization,
        i.e. current worker's Cache API calls this method after another worker issued a call that changes
        a given entry's expiry/expires_at attributes.
        """
        cdef Entry entry

        with self._lock:
            try:
                entry = <Entry>self._data[key]
            except KeyError:
                # We wouldn't have been called if that key hadn't existed in another worker's cache.
                # But since it doesn't in ours, it means that it must have been already deleted,
                # in which case report an error and quit.
                raise KeyError('Key `%s` not found by set_expiration_data' % key)
            else:
                # Process this request only if its expiration data is farther in the future than what we have in cache,
                # i.e. it's possible that our current worker already updated expiration metadata before this request was received
                # and without this condition, we would set expiration data back in the past.
                if expires_at > entry.expires_at:
                    entry.expiry = expiry
                    entry.expires_at = expires_at

# ################################################################################################################################

    cpdef list delete_expired(self):
        """ Deletes all entries expired as of now. Also, deletes all entries possibly found to have expired by .get or .set calls.
        """
        cdef list deleted
        cdef double _now = self._get_timestamp()
        cdef double expires_at

        # Collects all keys to be deleted and in another pass, delete them all.
        # It's performed it two steps so as to be able to hold self._lock only once.

        with self._lock:

            deleted = self._expired_on_op[:]

            # Collect keys still in cache
            for key, value in self._data.items():
                expires_at = value.expires_at
                if expires_at and _now > expires_at:
                    self._delete(key)
                    deleted.append(key)

            # Collect keys deleted by .get operations
            self._expired_on_op[:] = []

        return deleted

# ################################################################################################################################
