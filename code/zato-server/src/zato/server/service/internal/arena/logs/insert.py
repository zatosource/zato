# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class Insert(Service):
    """ Inserts a new log entry into the LogArena.
    """
    name = 'zato.arena.logs.insert'

    def handle(self) -> 'None':
        parent_id:'int' = self.request.input['parent_id']
        attrs:'dict' = self.request.input['attrs']

        arena = self.server.work_arena
        entry_id = arena.insert(parent_id, attrs)

        self.response.payload = {'entry_id': entry_id}

# ################################################################################################################################
# ################################################################################################################################
