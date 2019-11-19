# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

class CacheMemcached(WorkerImpl):
    """ Handles asynchronous updates to Memcached-based caches.
    """

# ################################################################################################################################

    def on_broker_msg_CACHE_MEMCACHED_CREATE(self, msg):
        self.cache_api.create(msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_MEMCACHED_EDIT(self, msg):
        self.cache_api.edit(msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_MEMCACHED_DELETE(self, msg):
        self.cache_api.delete(msg)

# ################################################################################################################################
