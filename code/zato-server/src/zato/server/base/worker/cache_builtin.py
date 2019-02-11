# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from base64 import b64decode

# Zato
from zato.common import CACHE
from zato.server.base.worker.common import WorkerImpl

# Python 2/3 compatibility
from zato.common.py23_ import pickle_loads

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

    def _unpickle_msg(self, msg, _pickle_loads=pickle_loads):

        if msg['is_key_pickled']:
            msg['key'] = _pickle_loads(msg['key'])

        if msg['is_value_pickled']:
            msg['value'] = _pickle_loads(b64decode(msg['value']))

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_BY_PREFIX(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_by_prefix(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_BY_SUFFIX(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_by_suffix(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_BY_REGEX(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_by_regex(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_CONTAINS(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_contains(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_NOT_CONTAINS(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_not_contains(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_CONTAINS_ALL(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_contains_all(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_CONTAINS_ANY(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_contains_any(_BUILTIN, msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_BY_PREFIX(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_by_prefix(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_BY_SUFFIX(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_by_suffix(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_BY_REGEX(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_by_regex(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_CONTAINS(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_contains(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_NOT_CONTAINS(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_not_contains(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_CONTAINS_ALL(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_contains_all(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_CONTAINS_ANY(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_contains_any(_BUILTIN, msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_BY_PREFIX(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_by_prefix(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_BY_SUFFIX(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_by_suffix(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_BY_REGEX(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_by_regex(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_contains(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_NOT_CONTAINS(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_not_contains(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS_ALL(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_contains_all(_BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS_ANY(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_contains_any(_BUILTIN, msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_CLEAR(self, msg, _BUILTIN=CACHE.TYPE.BUILTIN):
        if msg.source_worker_id != self.server.worker_id:
            self.cache_api.sync_after_clear(_BUILTIN, msg)

# ################################################################################################################################
