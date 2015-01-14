# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# globre
from globre import match as globre_match

# Zato
from zato.common import FALSE_TRUE, TRUE_FALSE

class Matcher(object):
    def __init__(self):
        self.config = None
        self.items = {True:[], False:[]}
        self.order1 = None
        self.order2 = None
        self.is_allowed_cache = {}

    def read_config(self, config):
        self.config = config
        order = config.get('order', FALSE_TRUE)
        self.order1, self.order2 = (True, False) if order == TRUE_FALSE else (False, True)

        for key, value in config.items():

            # Ignore meta key(s)
            if key == 'order':
                continue

            # Add new items
            self.items[value].append(key)

        # Now sort everything lexicographically, the way it will be used in run-time
        for key in self.items:
            self.items[key] = list(reversed(sorted(self.items[key])))

    def is_allowed(self, value):

        try:
            return self.is_allowed_cache[value]
        except KeyError:
            _match = globre_match
            is_allowed = None
    
            # This iterates over all patterns even if we already matched one
            # but it's OK because we do it only once and subsequent results
            # are returned from cache.
            for order in self.order1, self.order2:
                for pattern in self.items[order]:
                    if globre_match(pattern, value):
                        is_allowed = order

            # No match at all - we don't allow it in that case
            is_allowed = is_allowed if (is_allowed is not None) else False

            self.is_allowed_cache[value] = is_allowed
            return is_allowed
