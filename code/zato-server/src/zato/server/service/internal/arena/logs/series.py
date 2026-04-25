# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class GetSeries(Service):
    """ Returns all entries in a LogArena series.
    """
    name = 'zato.arena.logs.get-series'

    def handle(self) -> 'None':
        series_id:'int' = self.request.input['series_id']

        arena = self.server.work_arena
        result = arena.get_series(series_id)

        self.response.payload = result

# ################################################################################################################################

class GetChildren(Service):
    """ Returns direct child entries of a LogArena entry.
    """
    name = 'zato.arena.logs.get-children'

    def handle(self) -> 'None':
        entry_id:'int' = self.request.input['entry_id']

        arena = self.server.work_arena
        result = arena.get_children(entry_id)

        self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################
