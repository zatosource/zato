# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from decimal import Decimal
from sys import getsizeof

# Cython
from cpython.dict cimport PyDict_Contains, PyDict_DelItem, PyDict_GetItem, PyDict_SetItem
from cpython.list cimport PyList_GET_SIZE, PyList_Insert, PyList_SetSlice
from cpython.object cimport Py_EQ, PyObject, PyObject_RichCompareBool
from cpython.sequence cimport PySequence_ITEM
from posix.time cimport timeval, timezone, gettimeofday

# ################################################################################################################################

key_types = (int, long, basestring)
value_types = (int, long, float, basestring, Decimal, bytes)

# ################################################################################################################################

class CACHE:
    DEFAULT_SIZE = 2000
    MAX_ITEM_SIZE = None # By default objects may be of unlimited size

# ################################################################################################################################

cdef struct Entry:
    char* value
    double last_accessed

# ################################################################################################################################

cdef class Cache(object):
    """ An LRU cache that optionally rejects entries bigger than N bytes. Entries can have a TTL assigned - periodic processes
    will clean up entries older than allowed.
    """
    cdef:
        long max_size
        long max_item_size
        dict cache
        list index
        long misses
        long hits
        dict hits_per_position # How many times a given position in cache is used

    def __cinit__(self):
        self.cache = dict()
        self.index = list()
        self.hits_per_position = dict()
        self.hits = 0
        self.misses = 0

    def __init__(self, max_size=None, max_item_size=None):
        self.max_size = max_size or CACHE.DEFAULT_SIZE
        self.max_item_size = max_item_size or CACHE.MAX_ITEM_SIZE

# ################################################################################################################################

    def __repr__(self):
        return repr(self.cache.keys())

# ################################################################################################################################

    cdef _set(self, object key, value, _getsizeof=getsizeof, _key_types=key_types, _value_types=value_types):

        cdef Entry entry
        cdef Entry* old_entry
        cdef double _last_accessed
        cdef object old_key
        cdef Py_ssize_t cache_size = PyList_GET_SIZE(self.index)
        cdef Py_ssize_t index_idx
        cdef bint old_key_eq
        cdef object hits_per_position

        cdef timeval tv
        cdef timezone tz

        gettimeofday(&tv, &tz)
        _last_accessed = tv.tv_sec + tv.tv_usec / 1.0e9

        # Ok, we have this key in cache
        if PyDict_Contains(self.cache, key):
            
            # Update total hits counter
            self.hits += 1

            # Update last accessed entry for that key
            old_entry = <Entry*>PyDict_GetItem(self.cache, key)
            (<object>old_entry)['last_accessed'] = _last_accessed

            # Remove key from index ..
            index_idx = 0
            while index_idx < cache_size:

                # Find old key in index
                old_key = PySequence_ITEM(self.index, index_idx)
                old_key_eq = PyObject_RichCompareBool(old_key, <object>key, Py_EQ)

                if old_key_eq:

                    # We have the key's position so we can now update per-position counter
                    # to be able to offer statistics on how often a key is found at a given position.
                    if not PyDict_Contains(self.hits_per_position, index_idx):
                        PyDict_SetItem(self.hits_per_position, index_idx, 1)
                    else:
                        hits_per_position = <object>PyDict_GetItem(self.hits_per_position, index_idx)
                        hits_per_position += 1
                        PyDict_SetItem(self.hits_per_position, index_idx, hits_per_position)

                    # Remove object from index_idx position - this is what listremove in Objects/listobject.c does
                    # because there is no public PyList_Remove function.
                    PyList_SetSlice(self.index, index_idx, index_idx+1, <object>NULL)
                    break

                # Nothing found so far, continue on.
                index_idx += 1

            # Now insert the key back at the head position.
            PyList_Insert(self.index, 0, old_key)

        # No such key in cache - let's add it.
        else:
            # Add information that there was a cache miss
            self.misses += 1

            # Make sure there is room for the new key
            if cache_size == self.max_size:
                PyDict_DelItem(self.cache, self.index.pop())

            # Actually insert entry
            entry = Entry(value=value, last_accessed=_last_accessed)

            self.cache[key] = entry
            PyList_Insert(self.index, 0, key)

    cpdef set(self, str key, value):
        return self._set(key, value)

# ################################################################################################################################
