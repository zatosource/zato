# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime

# Zato
from zato.common import ZATO_NOT_GIVEN
from zato.common.exception import NotFound
from zato.server.service import Bool, Dict, ListOfDicts, Service

# ################################################################################################################################

optional_keys = ('key', 'value', 'last_read', 'prev_read', 'last_write', 'prev_write', 'expiry', 'expires_at', 'hits', \
    'position')

datetime_keys = ('last_read', 'prev_read', 'last_write', 'prev_write', 'expires_at')

# ################################################################################################################################

class _BaseGet(Service):

    # Must be provided by subclasses
    input_key = None

    class SimpleIO:
        response_elem = None
        input_optional = ('cache', Bool('details'),)
        skip_empty_keys = True
        force_empty_keys = ('value',)
        allow_empty_required = True

    def _convert_item_dict(self, item_dict, _utcfromtimestamp=datetime.utcfromtimestamp, _dt_keys=datetime_keys):
        for key in _dt_keys:
            value = item_dict[key]
            item_dict[key] = _utcfromtimestamp(value).isoformat() if value else None

        expiry = item_dict['expiry']
        item_dict['expiry'] = expiry if expiry else None

        return item_dict

    def handle(self):

        input = self.request.input
        cache_name = input['cache']

        if cache_name:
            try:
                cache = self.cache.builtin[cache_name]
            except KeyError:
                raise NotFound(self.cid, 'No such cache `{}`'.format(cache_name))
        else:
            cache = self.cache.default

        default = input['default'] if input.get('default') else ZATO_NOT_GIVEN

        self._cache_handle(cache, input[self.input_key], input.get('details'), default)

    def _cache_handle(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

class Get(_BaseGet):

    input_key = 'key'

    class SimpleIO(_BaseGet.SimpleIO):
        input_required = ('key',)
        input_optional = _BaseGet.SimpleIO.input_optional + ('default',)
        output_required = ('value',)
        output_optional = optional_keys

# ################################################################################################################################

    def _cache_handle(self, cache, key, details, default):

        item = cache.get(key, default, details)

        if item is not None:
            if item == default:
                self.response.payload.value = item
            else:
                self.response.payload = self._convert_item_dict(item.to_dict()) if details else {'value': item}
        else:
            raise NotFound(self.cid, 'No such key `{}`'.format(key))

# ################################################################################################################################

class _BaseGetList(_BaseGet):

    input_key = 'data'

    class SimpleIO(_BaseGet.SimpleIO):
        input_required = ('data',)
        output_optional = optional_keys
        output_repeated = True

# ################################################################################################################################

    def _cache_handle(self, cache, data, details, *ignored):

        result = self._cache_get_list(cache, data, details)

        if result:
            if details:
                out = [self._convert_item_dict(value.to_dict()) for value in result.itervalues()]
            else:
                out = [{'key':key, 'value':value} for key, value in result.iteritems()]

            self.response.payload[:] = out

    def _cache_get_list(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

class GetByPrefix(_BaseGetList):
    def _cache_get_list(self, cache, data, details):
        return cache.get_by_prefix(data, details)

# ################################################################################################################################

class GetBySuffix(_BaseGetList):
    def _cache_get_list(self, cache, data, details):
        return cache.get_by_suffix(data, details)

# ################################################################################################################################

class GetByRegex(_BaseGetList):
    def _cache_get_list(self, cache, data, details):
        return cache.get_by_regex(data, details)

# ################################################################################################################################

class GetByRegex(_BaseGetList):
    def _cache_get_list(self, cache, data, details):
        return cache.get_by_regex(data, details)

# ################################################################################################################################

class GetContains(_BaseGetList):
    def _cache_get_list(self, cache, data, details):
        return cache.get_contains(data, details)

# ################################################################################################################################

class GetNotContains(_BaseGetList):
    def _cache_get_list(self, cache, data, details):
        return cache.get_not_contains(data, details)

# ################################################################################################################################

class GetContainsAll(_BaseGetList):
    def _cache_get_list(self, cache, data, details):
        return cache.get_contains_all(data, details)

# ################################################################################################################################

class GetContainsAny(_BaseGetList):
    def _cache_get_list(self, cache, data, details):
        return cache.get_contains_any(data, details)

# ################################################################################################################################
