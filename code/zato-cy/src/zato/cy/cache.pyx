# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import inspect
from datetime import datetime
from decimal import Decimal
from sys import getsizeof, maxint

# Cython
from cpython.dict cimport PyDict_Contains, PyDict_DelItem, PyDict_GetItem, PyDict_Items, PyDict_Keys, PyDict_SetItem, \
    PyDict_Values
from cpython.int cimport PyInt_AS_LONG,  PyInt_FromLong, PyInt_GetMax
from cpython.list cimport PyList_GET_SIZE, PyList_Insert, PyList_SetSlice
from cpython.object cimport Py_EQ, PyObject, PyObject_RichCompareBool
from cpython.sequence cimport PySequence_ITEM
from libc.stdint cimport uint64_t
from posix.time cimport timeval, timezone, gettimeofday

# six
from six import binary_type, integer_types, string_types, text_type

# Zato
from zato.common import CACHE as _COMMON_CACHE

# gevent
from gevent.lock import RLock

# ################################################################################################################################

len_values = (binary_type,) + string_types + (text_type,)
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

    cpdef dict to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'last_read': self.last_read,
            'prev_read': self.prev_read,
            'last_write': self.last_write,
            'prev_write': self.prev_write,
            'expiry': self.expiry,
            'expires_at': self.expires_at,
            'hits': self.hits,
            'position': self.position,
        }

# ################################################################################################################################

cdef class Cache(object):
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

    def __cinit__(self):
        self._data = {}
        self._index = []
        self.hits_per_position = {}
        self._expired_on_op = []
        self.hits = 0
        self.misses = 0
        self.set_ops = 0
        self.get_ops = 0

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
        with self.lock:
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
            return PyDict_Contains(self._data, key)

# ################################################################################################################################

    def __len__(self):
        with self._lock:
            return PyList_GET_SIZE(self._index)

# ################################################################################################################################

    cpdef list keys(self):
        with self._lock:
            return PyDict_Keys(self._data)

# ################################################################################################################################

    cpdef list keys_by_position(self):
        with self._lock:
            return list(self._index)

# ################################################################################################################################

    cpdef list values(self):
        with self._lock:
            return PyDict_Values(self._data)

# ################################################################################################################################

    cpdef list items(self):
        with self._lock:
            return PyDict_Items(self._data)

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

    cdef _delete(self, object key):
        # Will raise KeyError on invalid key so the next line is safe
        del self._data[key]
        self._remove_from_index_by_idx(self._get_index(key))

# ################################################################################################################################

    cpdef delete(self, object key):
        with self._lock:
            self._delete(key)

    __del__ = delete

# ################################################################################################################################

    cdef inline long _get_index(self, object key):
        """ C-only version of self.get_position that will always return a long - must be called only
        if key is known to be in self._index or self._data and only with self.lock held.
        """
        cdef Py_ssize_t index_idx = 0
        cdef Py_ssize_t cache_size = PyList_GET_SIZE(self._index)
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
            if PyDict_Contains(self._data, key):
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
        """ Uses gettimeofday(2) to return current timestamp as double with microseconds precision.
        """
        cdef timeval tv
        cdef timezone tz

        gettimeofday(&tv, &tz)
        return tv.tv_sec + tv.tv_usec / 1.0e6

# ################################################################################################################################

    cpdef double get_timestamp(self):
        return self._get_timestamp()

# ################################################################################################################################

    cdef _set(self, object key, value, expiry, dict meta_ref, _getsizeof=getsizeof, _key_types=key_types, _len_values=len_values):

        cdef Entry entry
        cdef double _now = self._get_timestamp()
        cdef Py_ssize_t cache_size = PyList_GET_SIZE(self._index)
        cdef Py_ssize_t index_idx
        cdef bint old_key_eq
        cdef long hits_per_position
        cdef long len_value

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
        if PyDict_Contains(self._data, key):
            entry = <Entry>PyDict_GetItem(self._data, key)

            # If we have a key that previously was not using expiry, we must set it now.
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
                    # The entry exists and has not expired so now, if we are configured to, prolong its expiration time
                    if self.extend_expiry_on_set and entry.expiry:
                        entry.expires_at = _now + entry.expiry

            # Update access information for that entry, if we get to this point, the entry is not expired,
            # or at least its expiry time has been extended.
            entry.prev_write = entry.last_write
            entry.last_write = _now
            entry.value = value

        # No such key in cache - let's add it.
        else:

            # Make sure there is room for the new key
            if cache_size == self.max_size:
                PyDict_DelItem(self._data, self._index.pop())

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

            PyDict_SetItem(self._data, key, entry)
            PyList_Insert(self._index, 0, key)

        # If any output dict for metadata was passed in by reference, set its requires items.
        if meta_ref is not None:
            meta_ref['expires_at'] = entry.expires_at

# ################################################################################################################################

    cpdef set(self, object key, value, double expiry, dict meta_ref):
        with self._lock:
            self._set(key, value, expiry, meta_ref)

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

            # Return the default value, if any was given, or re-raise the exception.
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
            hits_per_position = PyInt_AS_LONG(<object>PyDict_GetItem(self.hits_per_position, index_idx))
            hits_per_position += 1
            PyDict_SetItem(self.hits_per_position, index_idx, PyInt_FromLong(hits_per_position))

            # Remove key from index
            index_key = self._remove_from_index_by_idx(index_idx)

            # Now insert the key back at the head position.
            PyList_Insert(self._index, 0, index_key)

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
        with self._lock:
            return self._get(key, default, details)

# ################################################################################################################################

    cpdef get_by_prefix(self, object prefix, object default, bint details):
        with self._lock:
            return self._get(key, prefix, details)

# ################################################################################################################################

    cpdef expire(self, object key, double expiry, dict meta_ref):
        """ Makes a given cache entry expire after 'expiry' seconds.
        """
        with self._lock:
            self._set(key, self._get(key, self.default_get, False), expiry, meta_ref)

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
            for key, value in PyDict_Items(self._data):
                expires_at = value.expires_at
                if expires_at and _now > expires_at:
                    self._delete(key)
                    deleted.append(key)

            # Collect keys deleted by .get operations
            self._expired_on_op[:] = []

        return deleted

# ################################################################################################################################
