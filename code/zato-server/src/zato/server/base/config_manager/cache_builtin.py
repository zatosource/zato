# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode

# Zato
from zato.common.api import CACHE
from zato.server.base.config_manager.common import ConfigManagerImpl

# Python 2/3 compatibility
from zato.common.py23_ import pickle_loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class CacheBuiltin(ConfigManagerImpl):
    """ Handles asynchronous updates to built-in caches.
    """
    def on_config_event_CACHE_BUILTIN_CREATE(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.cache_api.create(msg)

# ################################################################################################################################

    def on_config_event_CACHE_BUILTIN_EDIT(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.cache_api.edit(msg)

# ################################################################################################################################

    def on_config_event_CACHE_BUILTIN_DELETE(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.cache_api.delete(msg)

# ################################################################################################################################

    def _unpickle_msg(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':

        if msg['is_key_pickled']:
            msg['key'] = pickle_loads(msg['key'])

        if msg['is_value_pickled']:
            msg['value'] = pickle_loads(b64decode(msg['value']))

# ################################################################################################################################

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_SET(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_set(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_SET_BY_PREFIX(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_set_by_prefix(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_SET_BY_SUFFIX(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_set_by_suffix(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_SET_BY_REGEX(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_set_by_regex(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_SET_CONTAINS(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_set_contains(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_SET_NOT_CONTAINS(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_set_not_contains(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_SET_CONTAINS_ALL(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_set_contains_all(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_SET_CONTAINS_ANY(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_set_contains_any(CACHE.TYPE.BUILTIN, msg)

# ################################################################################################################################

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_DELETE(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_delete(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_DELETE_BY_PREFIX(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_delete_by_prefix(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_DELETE_BY_SUFFIX(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self._unpickle_msg(msg)
        self.cache_api.sync_after_delete_by_suffix(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_DELETE_BY_REGEX(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_delete_by_regex(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_DELETE_CONTAINS(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_delete_contains(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_DELETE_NOT_CONTAINS(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_delete_not_contains(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_DELETE_CONTAINS_ALL(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_delete_contains_all(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_DELETE_CONTAINS_ANY(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_delete_contains_any(CACHE.TYPE.BUILTIN, msg)

# ################################################################################################################################

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_EXPIRE(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_expire(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_BY_PREFIX(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_expire_by_prefix(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_BY_SUFFIX(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_expire_by_suffix(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_BY_REGEX(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_expire_by_regex(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_expire_contains(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_NOT_CONTAINS(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_expire_not_contains(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS_ALL(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_expire_contains_all(CACHE.TYPE.BUILTIN, msg)

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS_ANY(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg['is_value_pickled'] or msg['is_key_pickled']:
            self._unpickle_msg(msg)
        self.cache_api.sync_after_expire_contains_any(CACHE.TYPE.BUILTIN, msg)

# ################################################################################################################################

    def on_config_event_CACHE_BUILTIN_STATE_CHANGED_CLEAR(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.cache_api.sync_after_clear(CACHE.TYPE.BUILTIN, msg)

# ################################################################################################################################
# ################################################################################################################################
