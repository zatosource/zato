# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# globre
from globre import match as globre_match

# Paste
from paste.util.converters import asbool

# Zato
from zato.common.api import FALSE_TRUE, TRUE_FALSE

logger = logging.getLogger(__name__)

class Matcher(object):
    def __init__(self):
        self.config = None
        self.items = {True:[], False:[]}
        self.order1 = None
        self.order2 = None
        self.is_allowed_cache = {}
        self.special_case = None

    def read_config(self, config):
        self.config = config
        order = config.get('order', FALSE_TRUE)
        self.order1, self.order2 = (True, False) if order == TRUE_FALSE else (False, True)

        for key, value in config.items():

            # Ignore meta key(s)
            if key == 'order':
                continue

            value = asbool(value)

            # Add new items
            self.items[value].append(key)

        # Now sort everything lexicographically, the way it will be used in run-time
        for key in self.items:
            self.items[key] = list(reversed(sorted(self.items[key])))

        for empty, non_empty in ((True, False), (False, True)):
            if not self.items[empty] and '*' in self.items[non_empty]:
                self.special_case = non_empty
                break

    def is_allowed(self, value):
        logger.debug('Cache:`%s`, value:`%s`', self.is_allowed_cache, value)

        if self.special_case is not None:
            return self.special_case

        try:
            return self.is_allowed_cache[value]
        except KeyError:
            _match = globre_match
            is_allowed = None

            for order in self.order1, self.order2:
                for pattern in self.items[order]:
                    if _match(pattern, value):
                        is_allowed = order

            # No match at all - we don't allow it in that case
            is_allowed = is_allowed if (is_allowed is not None) else False

            self.is_allowed_cache[value] = is_allowed
            return is_allowed
