# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class ByText(Service):
    """ Full-text search across all string attributes.
    """
    name = 'zato.arena.logs.by-text'

    def handle(self) -> 'None':
        text:'str' = self.request.input['text']

        arena = self.server.work_arena
        result = arena.by_text(text)

        self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################
