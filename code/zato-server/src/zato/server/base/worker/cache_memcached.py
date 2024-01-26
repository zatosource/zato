# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.base.worker import WorkerStore

# ################################################################################################################################
# ################################################################################################################################

class CacheMemcached(WorkerImpl):
    """ Handles asynchronous updates to Memcached-based caches.
    """
    def on_broker_msg_CACHE_MEMCACHED_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.cache_api.create(msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_MEMCACHED_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.cache_api.edit(msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_MEMCACHED_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.cache_api.delete(msg)

# ################################################################################################################################
# ################################################################################################################################
