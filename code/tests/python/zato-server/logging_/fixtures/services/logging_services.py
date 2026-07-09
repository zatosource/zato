# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class DebugWriter(Service):
    """ Emits a DEBUG line through the service logger so tests can assert it lands in server.log.
    """
    name = 'logging-tests.debug-writer'

    def handle(self):
        self.logger.debug('Refreshed the customer cache, entries: 128')
        self.response.payload = {'result': 'ok'}

# ################################################################################################################################
# ################################################################################################################################
