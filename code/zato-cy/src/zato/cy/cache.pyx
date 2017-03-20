# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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

# ################################################################################################################################

key_types = (int, long, basestring)
value_types = (int, long, float, basestring, Decimal, bytes)

# ################################################################################################################################

class CACHE:
    DEFAULT_SIZE = 2000
    MAX_ITEM_SIZE = PyInt_GetMax() # By default objects have no practical length limit

# ################################################################################################################################

cdef struct Entry:
    # Represents an individual value stored in a cache. 

    # The actual contents
    char* value

    # When was the value last read
    double last_read

    # When was the value previously read
    double prev_read

    # When was the value last written to (creation or update)
    double last_write

    # When was the value previously written to (creation or update)
    double prev_write

    # How many times was this key returned
    uint64_t hits

# ################################################################################################################################

cdef class Cache(object):
    """ An LRU cache that optionally rejects entries bigger than N bytes. Entries can have a TTL assigned - periodic processes
    will clean up entries older than allowed.
    """
    cdef:
        public long max_size
        public long max_item_size
        public dict _data
        public list _index
        public uint64_t misses
        public uint64_t hits
        public uint64_t set_ops
        public uint64_t get_ops
        public dict hits_per_position # How many times a given position in cache is used

    def __cinit__(self):
        self._data = dict()
        self._index = list()
        self.hits_per_position = dict()
        self.hits = 0
        self.misses = 0
        self.set_ops = 0
        self.get_ops = 0

    def __init__(self, max_size=None, max_item_size=None):
        self.max_size = max_size or CACHE.DEFAULT_SIZE
        self.max_item_size = max_item_size or CACHE.MAX_ITEM_SIZE
        self.hits_per_position.update(dict((key, 0) for key in xrange(self.max_size)))

# ################################################################################################################################

    def __repr__(self):
        hits_to_misses = (round(1.0 * self.hits / self.misses, 1)) if self.misses else 'n/a'
        hits_to_misses = ' ({})'.format(hits_to_misses)

        get_to_set_ops = (round(1.0 * self.get_ops / self.set_ops, 1)) if self.set_ops else 'n/a'
        get_to_set_ops = ' ({})'.format(get_to_set_ops)

        return '<{} at {}, size:{}/{} hits/misses:{}/{}{}, get/set:{}/{}{}, max_item_size:{}>'.format(
            self.__class__.__name__, hex(id(self)), len(self._data), self.max_size,
            self.hits, self.misses, hits_to_misses,
            self.get_ops, self.set_ops, get_to_set_ops,
            self.max_item_size
        ) 

# ################################################################################################################################

    def __len__(self):
        return PyList_GET_SIZE(self._index)

# ################################################################################################################################

    cpdef list keys(self):
        return PyDict_Keys(self._data)

# ################################################################################################################################

    cpdef list keys_by_position(self):
        return list(self._index)

# ################################################################################################################################

    cpdef list values(self):
        return PyDict_Values(self._data)

# ################################################################################################################################

    cpdef list items(self):
        return PyDict_Values(self._data)

# ################################################################################################################################

    cdef inline long _get_index(self, str key):
        """ C-only version of self.get_position that will always return a long - must be called only
        if key is known to be in self._index or self._data.
        """
        cdef Py_ssize_t index_idx = 0
        cdef Py_ssize_t cache_size = PyList_GET_SIZE(self._index)
        cdef bint index_key_eq

        while index_idx < cache_size:
            if PyObject_RichCompareBool(PySequence_ITEM(self._index, index_idx), <object>key, Py_EQ):
                return index_idx
            index_idx += 1

# ################################################################################################################################

    cpdef object index(self, str key):
        """ Returns position key given on input currently holds or None if key is not found.
        """
        if PyDict_Contains(self._data, key):
            return self._get_index(key)

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

    cdef _set(self, object key, value, _getsizeof=getsizeof, _key_types=key_types, _value_types=value_types):

        cdef Entry entry
        cdef Entry* old_entry
        cdef dict py_old_entry
        cdef double _now = self._get_timestamp()
        cdef Py_ssize_t cache_size = PyList_GET_SIZE(self._index)
        cdef Py_ssize_t index_idx
        cdef bint old_key_eq
        cdef long hits_per_position

        # Update total # of .set operations
        self.set_ops += 1

        # Ok, we have this key in cache
        if PyDict_Contains(self._data, key):

            # Update access information for that entry
            old_entry = <Entry*>PyDict_GetItem(self._data, key)
            py_old_entry = <dict>old_entry
            PyDict_SetItem(py_old_entry, 'prev_write', <object>PyDict_GetItem(py_old_entry, 'last_write'))
            PyDict_SetItem(py_old_entry, 'last_write', _now)
            PyDict_SetItem(py_old_entry, 'value', value)

        # No such key in cache - let's add it.
        else:

            # Make sure there is room for the new key
            if cache_size == self.max_size:
                PyDict_DelItem(self._data, self._index.pop())

            # Actually insert entry
            entry = Entry(value=value, last_read=0.0, prev_read=0.0, last_write=_now, prev_write=_now, hits=0)

            PyDict_SetItem(self._data, key, entry)
            PyList_Insert(self._index, 0, key)

# ################################################################################################################################

    cpdef set(self, str key, value):
        self._set(key, value)

# ################################################################################################################################

    cpdef object get(self, str key, bint details=False):
        """ Returns data for key in cache if present. Otherwise returns None. If 'details' is True,
        returns a dictionary with value and metadata instead of value alone.
        """
        cdef dict py_entry
        cdef Entry* entry = <Entry*>PyDict_GetItem(self._data, key)
        cdef Py_ssize_t index_idx
        cdef Py_ssize_t cache_size
        cdef object index_key
        cdef bint index_key_eq

        # Update total # of .get operations
        self.get_ops += 1

        if entry != NULL:

            # Update total hits counter
            self.hits += 1

            # Current position of that key in index
            index_idx = self._get_index(key)

            # We have the key's position so we can now update per-position counter
            # to be able to offer statistics on how often a key is found at a given position.
            hits_per_position = PyInt_AS_LONG(<object>PyDict_GetItem(self.hits_per_position, index_idx))
            hits_per_position += 1
            PyDict_SetItem(self.hits_per_position, index_idx, PyInt_FromLong(hits_per_position))

            # Remove object from index_idx position - this is what listremove in Objects/listobject.c does
            # and we use the same technique because there is no public PyList_Remove function.
            index_key = PySequence_ITEM(self._index, index_idx)
            PyList_SetSlice(self._index, index_idx, index_idx+1, <object>NULL)

            # Now insert the key back at the head position.
            PyList_Insert(self._index, 0, index_key)

            # Update last/prev access information
            py_entry = <dict>entry
            PyDict_SetItem(py_entry, 'prev_read', <object>PyDict_GetItem(py_entry, 'last_read'))
            PyDict_SetItem(py_entry, 'last_read', <object>self._get_timestamp())
            PyDict_SetItem(py_entry, 'hits', <object>PyDict_GetItem(py_entry, 'hits') + 1 )

            # If details are requested, add current position of key to data returned
            if details:
                PyDict_SetItem(py_entry, 'key', key)
                PyDict_SetItem(py_entry, 'position', PyInt_FromLong(index_idx))
                return py_entry

            # Without details, simply return value stored for key
            else:
                return <object>PyDict_GetItem(py_entry, 'value')

        else:
            # Add information that there was a cache miss
            self.misses += 1

# ################################################################################################################################

