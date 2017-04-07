# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# gevent
from gevent.lock import RLock

# Zato
from zato.cache import Cache

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class _NotConfiguredAPI(object):
    def set(self, *args, **kwargs):
        raise Exception('Default cache is not configured')
    get = set

# ################################################################################################################################

class CacheAPI(object):
    """ Base class for all cache objects.
    """
    def __init__(self):
        self.lock = RLock()
        self.default = _NotConfiguredAPI()
        self.caches = {}
        self._set_api_calls()

    def _maybe_set_default(self, config, cache):
        logger.warn(config)
        if config.is_default:
            self.default = cache
            self._set_api_calls()

    def _set_api_calls(self):
        self.set = self.default.set
        self.get = self.default.get

# ################################################################################################################################

    def _create_builtin(self, config):
        return Cache(config.max_size, config.max_item_size, config.extend_expiry_on_get, config.extend_expiry_on_set)

# ################################################################################################################################

    def _edit(self, config):
        logger.warn('333 %s', config)
        logger.warn('222 %r', config)

# ################################################################################################################################

    def _delete(self):
        pass

# ################################################################################################################################

    def create(self, config):
        with self.lock:
            func = getattr(self, '_create_{}'.format(config.cache_type))
            cache = func(config)
            self.caches[config.name] = cache
            self._maybe_set_default(config, cache)

# ################################################################################################################################

    def edit(self, config):
        with self.lock:
            self._edit(config)

# ################################################################################################################################

    def delete(self):
        pass

# ################################################################################################################################

    def _clear(self):
        pass

# ################################################################################################################################

    def clear(self):
        pass

# ################################################################################################################################

    def get_size(self, name):
        pass

# ################################################################################################################################
