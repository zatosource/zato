# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import CACHE
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

class CacheBuiltin(WorkerImpl):
    """ Handles asynchronous updates to built-in caches.
    """

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_CREATE(self, msg):
        self.cache_api.create(msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_EDIT(self, msg):
        self.cache_api.edit(msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_DELETE(self, msg):
        self.cache_api.delete(msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_GET(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            self.cache_api.sync_after_get(_BUILTIN, msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            self.cache_api.sync_after_set(_BUILTIN, msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            self.cache_api.sync_after_delete(_BUILTIN, msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            self.cache_api.sync_after_expire(_BUILTIN, msg)

# ################################################################################################################################
