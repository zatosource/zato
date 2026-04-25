# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class Search(Service):
    """ Searches the LogArena with dual-path resolution, ranking, and pagination.
    """
    name = 'zato.arena.logs.search'

    def handle(self) -> 'None':
        scope:'str' = self.request.input['scope']
        input:'str' = self.request.input['input']
        offset:'int' = self.request.input['offset']
        limit:'int' = self.request.input['limit']

        arena = self.server.work_arena
        result = arena.search({
            'scope': scope or None,
            'input': input,
            'offset': offset,
            'limit': limit,
        })

        self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################
