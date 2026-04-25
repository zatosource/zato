# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class Get(Service):
    """ Retrieves a single LogArena entry by ID.
    """
    name = 'zato.arena.logs.get'

    def handle(self) -> 'None':
        entry_id:'int' = self.request.input['entry_id']

        arena = self.server.work_arena
        result = arena.get(entry_id)

        self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################
