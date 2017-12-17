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
from zato.common.exception import BadRequest, InternalServerError, NotFound
from zato.server.service import Bool, Float, Service

# ################################################################################################################################

optional_keys = ('key', 'value', 'last_read', 'prev_read', 'last_write', 'prev_write', 'expiry', 'expires_at', 'hits', \
    'position')

datetime_keys = ('last_read', 'prev_read', 'last_write', 'prev_write', 'expires_at')

# ################################################################################################################################

class _BaseService(Service):

    class SimpleIO:
        response_elem = None
        input_required = ('key',)
        input_optional = (Bool('return_prev'),)
        output_optional = optional_keys
        skip_empty_keys = True
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
        input_optional = _BaseService.SimpleIO.input_optional + ('cache', 'value', 'details', Float('expiry'))
        output_optional = _BaseService.SimpleIO.output_optional + ('prev_value',)

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

class _Multi(_BaseService):
    action = None

    class SimpleIO(_BaseService.SimpleIO):
        input_optional = _BaseService.SimpleIO.input_optional + ('expiry', 'value')
        output_optional = ('key', 'prev_value',)
        output_repeated = True

    def handle(self):
        input = self.request.input
        return_prev = input.get('return_prev')
        cache = self._get_cache(input)

        # Input for all Set* commands
        if self.action == 'set':
            args = (input['key'], input.value, input.get('expiry') or 0.0, return_prev)

        # Input for all Delete* commands
        elif self.action == 'delete':
            args = (input['key'], return_prev)

        # Input for all Expire* commands
        elif self.action == 'expire':
            args = (input['key'], input.expiry)

        # Must be extended if more commands are added in the future
        else:
            # Do not return too much information to the caller - but store it in logs nevertheless.
            self.logger.warn('Invalid internal action found `%s` in `%s` (%s)', self.action, self.name, self.cid)
            raise InternalServerError(self.cid, 'Invalid internal action found')

        result = self._get_cache_func(cache)(*args)
        if return_prev:
            self.response.payload[:] = [{'key':key, 'prev_value':value} for key, value in result.iteritems()]

    def _get_cache_func(self, cache):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

class _SetMulti(_Multi):
    action = 'set'

class _DeleteMulti(_Multi):
    action = 'delete'

class _ExpireMulti(_Multi):
    action = 'expire'

# ################################################################################################################################

class SetByPrefix(_SetMulti):
    def _get_cache_func(self, cache):
        return cache.set_by_prefix

class SetBySuffix(_SetMulti):
    def _get_cache_func(self, cache):
        return cache.set_by_suffix

class SetByRegex(_SetMulti):
    def _get_cache_func(self, cache):
        return cache.set_by_regex

class SetContains(_SetMulti):
    def _get_cache_func(self, cache):
        return cache.set_contains

class SetNotContains(_SetMulti):
    def _get_cache_func(self, cache):
        return cache.set_not_contains

class SetContainsAll(_SetMulti):
    def _get_cache_func(self, cache):
        return cache.set_contains_all

class SetContainsAny(_SetMulti):
    def _get_cache_func(self, cache):
        return cache.set_contains_any

# ################################################################################################################################

class DeleteByPrefix(_DeleteMulti):
    def _get_cache_func(self, cache):
        return cache.delete_by_prefix

class DeleteBySuffix(_DeleteMulti):
    def _get_cache_func(self, cache):
        return cache.delete_by_suffix

class DeleteByRegex(_DeleteMulti):
    def _get_cache_func(self, cache):
        return cache.delete_by_regex

class DeleteContains(_DeleteMulti):
    def _get_cache_func(self, cache):
        return cache.delete_contains

class DeleteNotContains(_DeleteMulti):
    def _get_cache_func(self, cache):
        return cache.delete_not_contains

class DeleteContainsAll(_DeleteMulti):
    def _get_cache_func(self, cache):
        return cache.delete_contains_all

class DeleteContainsAny(_DeleteMulti):
    def _get_cache_func(self, cache):
        return cache.delete_contains_any

# ################################################################################################################################

class ExpireByPrefix(_ExpireMulti):
    def _get_cache_func(self, cache):
        return cache.expire_by_prefix

class ExpireBySuffix(_ExpireMulti):
    def _get_cache_func(self, cache):
        return cache.expire_by_suffix

class ExpireByRegex(_ExpireMulti):
    def _get_cache_func(self, cache):
        return cache.expire_by_regex

class ExpireContains(_ExpireMulti):
    def _get_cache_func(self, cache):
        return cache.expire_contains

class ExpireNotContains(_ExpireMulti):
    def _get_cache_func(self, cache):
        return cache.expire_not_contains

class ExpireContainsAll(_ExpireMulti):
    def _get_cache_func(self, cache):
        return cache.expire_contains_all

class ExpireContainsAny(_ExpireMulti):
    def _get_cache_func(self, cache):
        return cache.expire_contains_any

# ################################################################################################################################
