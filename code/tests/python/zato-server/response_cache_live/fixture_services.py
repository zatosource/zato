# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import sleep

# Zato
from zato.server.connection.http_soap.response_cache import counters
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# Module-level invocation state, shared by all the services below - this is what lets the tests
# assert how many times the data service actually ran no matter what the cache did.
invocation_state = {'count': 0}

# How long the data service sleeps, giving concurrent requests time to pile up on the coalescing lock
_sleep_seconds = 0.5

# The name of the channel whose responses the invalidation service purges
_data_channel_name = 'test.response-cache.data.channel'

# ################################################################################################################################
# ################################################################################################################################

class ResponseCacheData(Service):
    """ The service under cache - sleeps and counts its invocations.
    """
    name = 'test.response-cache.data'

    def handle(self) -> 'None':
        invocation_state['count'] += 1
        sleep(_sleep_seconds)
        self.response.content_type = 'application/json'
        self.response.payload = {'result':'ok', 'value':'constant'}

# ################################################################################################################################
# ################################################################################################################################

class ResponseCacheCount(Service):
    """ Returns how many times the data service ran.
    """
    name = 'test.response-cache.count'

    def handle(self) -> 'None':
        self.response.payload = {'count': invocation_state['count']}

# ################################################################################################################################
# ################################################################################################################################

class ResponseCacheReset(Service):
    """ Resets the invocation counter and the in-process coalescing counters.
    """
    name = 'test.response-cache.reset'

    def handle(self) -> 'None':
        invocation_state['count'] = 0
        counters.reset()
        self.response.payload = {'ok': True}

# ################################################################################################################################
# ################################################################################################################################

class ResponseCacheStats(Service):
    """ Returns the first-class coalescing counters of the server process.
    """
    name = 'test.response-cache.stats'

    def handle(self) -> 'None':
        self.response.payload = {
            'invoke_count': counters.invoke_count,
            'coalesced_count': counters.coalesced_count,
            'coalesce_timeout_count': counters.coalesce_timeout_count,
        }

# ################################################################################################################################
# ################################################################################################################################

class ResponseCacheInvalidate(Service):
    """ Purges the cached responses of the data channel through the programmatic facade.
    """
    name = 'test.response-cache.invalidate'

    def handle(self) -> 'None':
        self.cache.invalidate_response(_data_channel_name)
        self.response.payload = {'ok': True}

# ################################################################################################################################
# ################################################################################################################################
