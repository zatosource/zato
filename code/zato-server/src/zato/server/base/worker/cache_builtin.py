# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode

# Zato
from zato.common.api import CACHE
from zato.server.base.worker.common import WorkerImpl

# Python 2/3 compatibility
from zato.common.py23_ import pickle_loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.base.worker import WorkerStore

# ################################################################################################################################
# ################################################################################################################################

class CacheBuiltin(WorkerImpl):
    """ Handles asynchronous updates to built-in caches.
    """
    def on_broker_msg_CACHE_BUILTIN_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.cache_api.create(msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.cache_api.edit(msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.cache_api.delete(msg)

# ################################################################################################################################

    def _unpickle_msg(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':

        if msg['is_key_pickled']:
            msg['key'] = pickle_loads(msg['key'])

        if msg['is_value_pickled']:
            msg['value'] = pickle_loads(b64decode(msg['value']))

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_BY_PREFIX(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_by_prefix(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_BY_SUFFIX(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_by_suffix(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_BY_REGEX(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_by_regex(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_CONTAINS(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_contains(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_NOT_CONTAINS(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_not_contains(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_CONTAINS_ALL(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_contains_all(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_SET_CONTAINS_ANY(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_set_contains_any(CACHE.TYPE.BUILTIN, msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_BY_PREFIX(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_by_prefix(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_BY_SUFFIX(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_by_suffix(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_BY_REGEX(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_by_regex(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_CONTAINS(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_contains(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_NOT_CONTAINS(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_not_contains(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_CONTAINS_ALL(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_contains_all(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_DELETE_CONTAINS_ANY(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_delete_contains_any(CACHE.TYPE.BUILTIN, msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_BY_PREFIX(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_by_prefix(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_BY_SUFFIX(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_by_suffix(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_BY_REGEX(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_by_regex(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_contains(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_NOT_CONTAINS(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_not_contains(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS_ALL(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_contains_all(CACHE.TYPE.BUILTIN, msg)

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS_ANY(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            if msg['is_value_pickled'] or msg['is_key_pickled']:
                self._unpickle_msg(msg)
            self.cache_api.sync_after_expire_contains_any(CACHE.TYPE.BUILTIN, msg)

# ################################################################################################################################

    def on_broker_msg_CACHE_BUILTIN_STATE_CHANGED_CLEAR(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.source_worker_id != self.server.worker_id:
            self.cache_api.sync_after_clear(CACHE.TYPE.BUILTIN, msg)

# ################################################################################################################################
