# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class ByAttr(Service):
    """ Direct structured search by attribute key/value pair.
    """
    name = 'zato.arena.logs.by-attr'

    def handle(self) -> 'None':
        key:'str' = self.request.input['key']
        value = self.request.input['value']

        arena = self.server.work_arena
        result = arena.by_attr(key, value)

        self.response.payload = result

# ################################################################################################################################

class ByRange(Service):
    """ Numeric range query on an integer attribute.
    """
    name = 'zato.arena.logs.by-range'

    def handle(self) -> 'None':
        key:'str' = self.request.input['key']
        min_val:'int' = self.request.input['min']
        max_val:'int' = self.request.input['max']

        arena = self.server.work_arena
        result = arena.by_range(key, min_val, max_val)

        self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################
