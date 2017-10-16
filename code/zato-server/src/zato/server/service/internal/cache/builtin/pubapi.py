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
from zato.common.exception import BadRequest, NotFound
from zato.server.service import Bool, Dict, Float, ListOfDicts, Service

# ################################################################################################################################

optional_keys = ('key', 'value', 'last_read', 'prev_read', 'last_write', 'prev_write', 'expiry', 'expires_at', 'hits', \
    'position')

datetime_keys = ('last_read', 'prev_read', 'last_write', 'prev_write', 'expires_at')

# ################################################################################################################################

class _BaseService(Service):

    class SimpleIO:
        response_elem = None
        input_required = ('key',)
        skip_empty_keys = True
        force_empty_keys = ('value',)
        allow_empty_required = True

    def _get_cache(self, input):
        cache_name = input.get('cache')
        if cache_name:
            try:
                cache = self.cache.builtin[cache_name]
            except KeyError:
                raise NotFound(self.cid, 'No such cache `{}`'.format(cache_name))
        else:
            cache = self.cache.default

        return cache

    def _convert_item_dict(self, item_dict, _utcfromtimestamp=datetime.utcfromtimestamp, _dt_keys=datetime_keys):
        for key in _dt_keys:
            value = item_dict[key]
            item_dict[key] = _utcfromtimestamp(value).isoformat() if value else None

        expiry = item_dict['expiry']
        item_dict['expiry'] = expiry if expiry else None

        return item_dict

# ################################################################################################################################

class SingleKeyService(_BaseService):
    """ Base class for cache services accepting a single key on input, except for Expiry which uses its own service.
    """
    class SimpleIO(_BaseService.SimpleIO):
        input_optional = ('cache', 'value', Bool('details'), Float('expiry'), 'return_prev')
        output_optional = ('prev_value',)

# ################################################################################################################################

    def handle_GET(self):
        """ Returns cache entries by their keys.
        """
        input = self.request.input
        key = input['key']
        default = input['default'] if input.get('default') else ZATO_NOT_GIVEN
        details = self.request.input.get('details')

        result = self._get_cache(input).get(key, default, details)

        if result is not None:
            if result == default:
                self.response.payload.value = result
            else:
                self.response.payload = self._convert_item_dict(result.to_dict()) if details else {'value': result}
        else:
            raise NotFound(self.cid, 'No such key `{}`'.format(key))

# ################################################################################################################################

    def handle_POST(self):
        """ Stores new cache entries or updates existing ones, including setting their expiry time.
        """
        input = self.request.input
        key = input['key']
        cache = self._get_cache(input)

        # This is an update of value and, possibly, an entry's expiry
        if input.get('value'):
            prev_value = cache.set(input['key'], input.value, input.get('expiry') or 0.0)
            if input.get('return_prev'):
                self.response.payload.prev_value = prev_value

        # We only update the expiry time
        else:
            if not input.get('expiry'):
                raise BadRequest(self.cid, 'At least one of `value` or `expiry` is needed on input')
            else:
                found_key = cache.expire(input['key'], input.expiry)
                if not found_key:
                    raise NotFound(self.cid, 'No such key `{}`'.format(key))

# ################################################################################################################################

    def handle_DELETE(self):
        """ Deletes already existing cache entries
        """
        input = self.request.input
        key = input['key']
        try:
            prev_value = self._get_cache(input).delete(key)
        except KeyError:
            raise NotFound(self.cid, 'No such key `{}`'.format(key))
        else:
            if input.get('return_prev'):
                self.response.payload.prev_value = prev_value

# ################################################################################################################################

'''

class _BaseService(Service):
    def _get_cache(self, input):
        cache_name = input['cache']
        if cache_name:
            try:
                cache = self.cache.builtin[cache_name]
            except KeyError:
                raise NotFound(self.cid, 'No such cache `{}`'.format(cache_name))
        else:
            cache = self.cache.default

        return cache

# ################################################################################################################################

class _BaseGet(_BaseService):

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
        default = input['default'] if input.get('default') else ZATO_NOT_GIVEN
        self._cache_handle(self._get_cache(input), input[self.input_key], self.request.input.get('details'), default)

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

class _BaseSet(_BaseService):

    # Must be provided by subclasses
    input_key = None

    class SimpleIO:
        response_elem = None
        input_optional = ('cache', Bool('return_found'), Float('expiry'))

# ################################################################################################################################

class Set(_BaseSet):

    input_key = 'key'

    class SimpleIO(_BaseSet.SimpleIO):
        input_required = ('key', 'value')
        output_optional = ('prev_value',)
        skip_empty_keys = True

    def handle(self):
        input = self.request.input
        prev_value = self._get_cache(input).set(input[self.input_key], input.value, input.get('expiry') or 0.0)

        if input.return_found:
            self.response.payload.prev_value = prev_value

# ################################################################################################################################

class _SetList(_BaseSet):

    input_key = 'data'

    class SimpleIO(_BaseSet.SimpleIO):
        input_required = ('data', 'value')
        output_optional = ('key', 'prev_value',)
        output_repeated = True
        skip_empty_keys = True

    def handle(self):
        input = self.request.input
        return_found = input.get('return_found')
        cache = self._get_cache(input)

        result = self._get_cache_func(cache)(input[self.input_key], input.value, input.get('expiry') or 0.0, return_found)
        if return_found:
            self.response.payload[:] = [{'key':key, 'prev_value':value} for key, value in result.iteritems()]

    def _get_cache_func(self, cache):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

class SetByPrefix(_SetList):
    def _get_cache_func(self, cache):
        return cache.set_by_prefix

# ################################################################################################################################

class SetBySuffix(_SetList):
    def _get_cache_func(self, cache):
        return cache.set_by_suffix

# ################################################################################################################################

class SetByRegex(_SetList):
    def _get_cache_func(self, cache):
        return cache.set_by_regex

# ################################################################################################################################

class SetContains(_SetList):
    def _get_cache_func(self, cache):
        return cache.set_contains

# ################################################################################################################################

class SetNotContains(_SetList):
    def _get_cache_func(self, cache):
        return cache.set_not_contains

# ################################################################################################################################

class SetContainsAll(_SetList):
    def _get_cache_func(self, cache):
        return cache.set_contains_all

# ################################################################################################################################

class SetContainsAny(_SetList):
    def _get_cache_func(self, cache):
        return cache.set_contains_any

# ################################################################################################################################

class _BaseDelete(_BaseService):

    # Must be provided by subclasses
    input_key = None

    class SimpleIO:
        response_elem = None
        input_optional = ('cache', Bool('return_found'),)
        output_optional = ('prev_value',)
        skip_empty_keys = True

# ################################################################################################################################

class Delete(_BaseService):

    input_key = 'key'

    class SimpleIO(_BaseDelete.SimpleIO):
        response_elem = None
        input_optional = ('cache', Bool('return_found'),)
        output_optional = ('prev_value',)
        skip_empty_keys = True

    def handle(self):
        input = self.request.input
        key = input[self.input_key]
        try:
            prev_value = cache.delete(key)
        except KeyError:
            raise NotFound(self.cid, 'No such key `{}`'.format(key))
        else:
            if input.return_found:
                self.response.payload.prev_value = prev_value

# ################################################################################################################################

class _DeleteList(_BaseDelete):

    input_key = 'data'

    class SimpleIO(_BaseSet.SimpleIO):
        input_required = ('data',)
        output_optional = ('key', 'prev_value',)
        output_repeated = True
        skip_empty_keys = True

    def handle(self):
        input = self.request.input
        return_found = input.get('return_found')

        cache = self._get_cache(input)
        cache_func = self._get_cache_func(cache)

        result = cache_func(input[self.input_key], return_found)
        if return_found:
            self.response.payload[:] = [{'key':key, 'prev_value':value} for key, value in result.iteritems()]

    def _get_cache_func(self, cache):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

class DeleteByPrefix(_DeleteList):
    def _get_cache_func(self, cache):
        return cache.delete_by_prefix

# ################################################################################################################################

class DeleteBySuffix(_DeleteList):
    def _get_cache_func(self, cache):
        return cache.delete_by_suffix

# ################################################################################################################################

class DeleteByRegex(_DeleteList):
    def _get_cache_func(self, cache):
        return cache.delete_by_regex

# ################################################################################################################################

class DeleteContains(_DeleteList):
    def _get_cache_func(self, cache):
        return cache.delete_contains

# ################################################################################################################################

class DeleteNotContains(_DeleteList):
    def _get_cache_func(self, cache):
        return cache.delete_not_contains

# ################################################################################################################################

class DeleteContainsAll(_DeleteList):
    def _get_cache_func(self, cache):
        return cache.delete_contains_all

# ################################################################################################################################

class DeleteContainsAny(_DeleteList):
    def _get_cache_func(self, cache):
        return cache.delete_contains_any

# ################################################################################################################################

'''
