# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import OrderedDict

# ################################################################################################################################

class CACHE:
    DEFAULT_SIZE = 2000

# ################################################################################################################################

class Cache(object):
    """ A base class for caches - implements logic independent of cache eviction policies defined by subclasses.
    """
    def __init__(self, max_size=None, cache=None):
        self.max_size = max_size or CACHE.DEFAULT_SIZE
        self.cache = cache or OrderedDict()

# ################################################################################################################################

    def set(self, key, value):
        if key in self.cache:
            return # TODO: Update insertion time

        else:
            # Make sure there is room for the new key
            if len(self.cache) == self.max_size:
                self.make_room()

            # Actually insert entry
            self._set_key(key, value)

# ################################################################################################################################

    def make_room(self):
        print(333, self.cache)

# ################################################################################################################################

    def _set_key(self, key, value):
        print(444, self.cache)

# ################################################################################################################################

