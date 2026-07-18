# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class CacheCheck(Service):
    """ Exercises self.cache for the Config DB Redis tests - writes a key through the
    server's live cache connection and returns what it read back, so a test can then
    connect to the expected Redis server directly and confirm the key is physically there.
    """

    name = 'test.config-db.cache-check'

    def handle(self):

        # The invoker delivers the payload as a raw JSON string
        request = self.request.payload
        if isinstance(request, str):
            request = loads(request)

        key = request['key']
        value = request['value']

        # Write through the live cache connection and read the value back
        self.cache.set(key, value)
        read_value = self.cache.get(key)

        self.response.payload = dumps({'read_value': read_value})

# ################################################################################################################################
# ################################################################################################################################
